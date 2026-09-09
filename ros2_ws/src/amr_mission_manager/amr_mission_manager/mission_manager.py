"""ROS transport for warehouse task validation, target generation, and mission state."""

from pathlib import Path
from typing import Any

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
import rclpy
from rcl_interfaces.msg import ParameterDescriptor
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

from amr_mission_manager.inventory_manager import (
    InventoryError,
    InventoryManager,
    RackLocation,
    UnknownSKUError,
)
from amr_mission_manager.mission_logic import (
    InvalidRequestError,
    TaskRequest,
    parse_task_request,
    yaw_to_quaternion,
)


class MissionManager(Node):
    """Execute a complete SKU -> rack -> packing-zone warehouse mission."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__('mission_manager', **kwargs)
        try:
            default_inventory = (
                Path(get_package_share_directory('amr_mission_manager'))
                / 'config' / 'inventory.yaml'
            )
            self.declare_parameter(
                'inventory_file',
                str(default_inventory),
                ParameterDescriptor(
                    description='Inventory YAML path; restart to load changes.',
                    read_only=True,
                ),
            )
            inventory_path = self.get_parameter('inventory_file').value
            self.inventory = InventoryManager(inventory_path)
            self.packing_zone = self.inventory.get_rack('PACKING_ZONE')
        except Exception as exc:
            self.get_logger().error(f'Cannot load warehouse inventory: {exc}')
            self.destroy_node()
            raise

        self.active_request: TaskRequest | None = None
        self.active_rack: RackLocation | None = None
        self.phase: str | None = None

        self.target_publisher = self.create_publisher(
            PoseStamped, '/amr/target_pose', 10,
        )
        self.status_publisher = self.create_publisher(
            String, '/amr/mission_status', 10,
        )
        self.module_publisher = self.create_publisher(
            String, '/amr/module_command', 10,
        )
        self.task_subscription = self.create_subscription(
            String, '/amr/task_request', self.handle_task_request, 10,
        )
        self.navigation_subscription = self.create_subscription(
            String, '/amr/navigation_status', self.handle_navigation_status, 10,
        )
        self.get_logger().info(
            f'Loaded inventory from {inventory_path}; ready for DELIVER missions',
        )

    def handle_task_request(self, message: String) -> None:
        """Resolve an SKU and start the first navigation leg to its rack."""
        try:
            request = parse_task_request(message.data)
        except InvalidRequestError as exc:
            self._publish_status('INVALID_REQUEST', str(exc))
            return

        if self.active_request is not None:
            self._publish_status(
                'BUSY',
                f'active_task={self.active_request.task_id}; wait for completion',
                request,
            )
            return

        self._publish_status('TASK_RECEIVED', f'action={request.action}', request)
        try:
            rack = self.inventory.resolve_sku(request.sku)
        except UnknownSKUError as exc:
            self._publish_status('INVALID_SKU', str(exc), request)
            return
        except InventoryError as exc:
            self._publish_status('INVENTORY_ERROR', str(exc), request)
            return

        self.active_request = request
        self.active_rack = rack
        self.phase = 'TO_RACK'

        self._publish_status('SKU_RESOLVED', f'rack={rack.rack_id}', request)
        self._publish_target(rack, 'RACK_TARGET_GENERATED')

    def handle_navigation_status(self, message: String) -> None:
        """Advance the mission state machine from rack pickup to delivery."""
        if self.active_request is None or self.phase is None:
            return

        nav_state = message.data.strip()
        request = self.active_request
        destination = self._current_destination_name()

        if nav_state == 'NAVIGATION_GOAL_SENT':
            self._publish_status(
                'NAVIGATION_REQUESTED',
                f'phase={self.phase} destination={destination}',
                request,
            )
        elif nav_state == 'NAVIGATION_ACTIVE':
            self._publish_status(
                'NAVIGATING',
                f'phase={self.phase} destination={destination}',
                request,
            )
        elif nav_state == 'NAVIGATION_SUCCEEDED':
            self._handle_navigation_success()
        elif nav_state in {
            'NAVIGATION_GOAL_REJECTED',
            'NAVIGATION_CANCELED',
            'NAVIGATION_ABORTED',
            'NAV2_UNAVAILABLE',
        }:
            self._publish_status(
                'MISSION_FAILED',
                f'{nav_state} phase={self.phase} destination={destination}',
                request,
            )
            self._clear_active_mission()
        elif nav_state.startswith('NAVIGATION_FINISHED_STATUS_'):
            self._publish_status(
                'MISSION_FAILED',
                f'{nav_state} phase={self.phase} destination={destination}',
                request,
            )
            self._clear_active_mission()

    def _handle_navigation_success(self) -> None:
        request = self.active_request
        if request is None:
            return

        if self.phase == 'TO_RACK':
            rack_id = self.active_rack.rack_id if self.active_rack else 'UNKNOWN'
            self._publish_status('ARRIVED_RACK', f'rack={rack_id}', request)
            self._publish_module_command(
                f'PICKUP task_id={request.task_id} sku={request.sku} rack={rack_id}'
            )
            self._publish_status(
                'LOAD_ACQUIRED',
                f'sku={request.sku} module=BIN_LOAD_SIM',
                request,
            )
            self.phase = 'TO_PACKING'
            self._publish_target(self.packing_zone, 'PACKING_TARGET_GENERATED')
            return

        if self.phase == 'TO_PACKING':
            self._publish_status('ARRIVED_PACKING', 'destination=PACKING_ZONE', request)
            self._publish_module_command(
                f'DROP task_id={request.task_id} sku={request.sku} station=PACKING_ZONE'
            )
            self._publish_status(
                'MISSION_COMPLETE',
                'rack pickup and packing-zone delivery completed',
                request,
            )
            self._clear_active_mission()

    def _publish_target(self, location: RackLocation, state: str) -> None:
        request = self.active_request
        if request is None:
            return
        self.target_publisher.publish(self.create_target_pose(location))
        self._publish_status(
            state,
            (
                f'destination={location.rack_id} frame=map '
                f'x={location.x} y={location.y} yaw={location.yaw}'
            ),
            request,
        )

    def _publish_module_command(self, command: str) -> None:
        self.module_publisher.publish(String(data=command))
        self.get_logger().info(f'MODULE_COMMAND {command}')

    def _current_destination_name(self) -> str:
        if self.phase == 'TO_RACK' and self.active_rack is not None:
            return self.active_rack.rack_id
        if self.phase == 'TO_PACKING':
            return 'PACKING_ZONE'
        return 'UNKNOWN'

    def _clear_active_mission(self) -> None:
        self.active_request = None
        self.active_rack = None
        self.phase = None

    def create_target_pose(self, location: RackLocation) -> PoseStamped:
        """Stamp a planar configured location using this node's ROS clock."""
        target = PoseStamped()
        target.header.frame_id = 'map'
        target.header.stamp = self.get_clock().now().to_msg()
        target.pose.position.x = location.x
        target.pose.position.y = location.y
        target.pose.position.z = 0.0
        quaternion = yaw_to_quaternion(location.yaw)
        (
            target.pose.orientation.x,
            target.pose.orientation.y,
            target.pose.orientation.z,
            target.pose.orientation.w,
        ) = quaternion
        return target

    def _publish_status(
        self,
        state: str,
        detail: str,
        request: TaskRequest | None = None,
    ) -> None:
        task_id = request.task_id if request else '-'
        sku = request.sku if request else '-'
        status = f'{state} task_id={task_id} sku={sku}: {detail}'
        self.status_publisher.publish(String(data=status))
        if state in {
            'INVALID_REQUEST',
            'INVALID_SKU',
            'INVENTORY_ERROR',
            'BUSY',
            'MISSION_FAILED',
        }:
            self.get_logger().warning(status)
        else:
            self.get_logger().info(status)


def main(args: list[str] | None = None) -> int:
    rclpy.init(args=args)
    node: MissionManager | None = None
    try:
        node = MissionManager()
        rclpy.spin(node)
    except InventoryError:
        return 1
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
