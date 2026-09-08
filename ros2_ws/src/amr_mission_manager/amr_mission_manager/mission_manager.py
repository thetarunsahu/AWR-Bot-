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
    """Resolve warehouse tasks into map goals and track navigation completion."""

    def __init__(self, **kwargs: Any) -> None:
        """Load inventory once and create the mission I/O topics."""
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
        except Exception as exc:
            self.get_logger().error(f'Cannot load warehouse inventory: {exc}')
            self.destroy_node()
            raise

        self.active_request: TaskRequest | None = None
        self.active_rack: RackLocation | None = None

        self.target_publisher = self.create_publisher(
            PoseStamped, '/amr/target_pose', 10,
        )
        self.status_publisher = self.create_publisher(
            String, '/amr/mission_status', 10,
        )
        self.task_subscription = self.create_subscription(
            String, '/amr/task_request', self.handle_task_request, 10,
        )
        self.navigation_subscription = self.create_subscription(
            String, '/amr/navigation_status', self.handle_navigation_status, 10,
        )
        self.get_logger().info(
            f'Loaded inventory from {inventory_path}; listening on /amr/task_request',
        )

    def handle_task_request(self, message: String) -> None:
        """Validate a task, resolve its SKU and publish a single rack approach pose."""
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

        self._publish_status('SKU_RESOLVED', f'rack={rack.rack_id}', request)
        target = self.create_target_pose(rack)

        # Set active state before publishing so a fast navigation-status callback
        # can always be associated with the correct task.
        self.active_request = request
        self.active_rack = rack
        self.target_publisher.publish(target)
        self._publish_status(
            'TARGET_GENERATED',
            f'rack={rack.rack_id} frame=map x={rack.x} y={rack.y} yaw={rack.yaw}',
            request,
        )

    def handle_navigation_status(self, message: String) -> None:
        """Translate Nav2 bridge states into mission-level warehouse states."""
        if self.active_request is None:
            return

        nav_state = message.data.strip()
        request = self.active_request
        rack_id = self.active_rack.rack_id if self.active_rack else 'UNKNOWN'

        if nav_state == 'NAVIGATION_GOAL_SENT':
            self._publish_status('NAVIGATION_REQUESTED', f'rack={rack_id}', request)
        elif nav_state == 'NAVIGATION_ACTIVE':
            self._publish_status('NAVIGATING', f'toward rack={rack_id}', request)
        elif nav_state == 'NAVIGATION_SUCCEEDED':
            self._publish_status('MISSION_COMPLETE', f'arrived_at={rack_id}', request)
            self._clear_active_mission()
        elif nav_state in {
            'NAVIGATION_GOAL_REJECTED',
            'NAVIGATION_CANCELED',
            'NAVIGATION_ABORTED',
            'NAV2_UNAVAILABLE',
        }:
            self._publish_status('MISSION_FAILED', f'{nav_state} rack={rack_id}', request)
            self._clear_active_mission()
        elif nav_state.startswith('NAVIGATION_FINISHED_STATUS_'):
            self._publish_status('MISSION_FAILED', f'{nav_state} rack={rack_id}', request)
            self._clear_active_mission()

    def _clear_active_mission(self) -> None:
        self.active_request = None
        self.active_rack = None

    def create_target_pose(self, rack: RackLocation) -> PoseStamped:
        """Stamp a planar inventory location using this node's ROS clock."""
        target = PoseStamped()
        target.header.frame_id = 'map'
        target.header.stamp = self.get_clock().now().to_msg()
        target.pose.position.x = rack.x
        target.pose.position.y = rack.y
        target.pose.position.z = 0.0
        quaternion = yaw_to_quaternion(rack.yaw)
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
        """Publish readable mission events and mirror them to the ROS log."""
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
    """Run the node and shut down cleanly on interrupt or invalid inventory."""
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
