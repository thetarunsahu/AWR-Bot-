"""ROS transport for warehouse task validation and target generation."""

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
    """Resolve each valid task into one map-frame pose, without navigation."""

    def __init__(self, **kwargs: Any) -> None:
        """Load the inventory once; fail startup if its configuration is invalid."""
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
            # Construction failed: release the partially created ROS node too.
            self.get_logger().error(f'Cannot load warehouse inventory: {exc}')
            self.destroy_node()
            raise

        self.target_publisher = self.create_publisher(
            PoseStamped, '/amr/target_pose', 10,
        )
        self.status_publisher = self.create_publisher(
            String, '/amr/mission_status', 10,
        )
        self.task_subscription = self.create_subscription(
            String, '/amr/task_request', self.handle_task_request, 10,
        )
        self.get_logger().info(
            f'Loaded inventory from {inventory_path}; listening on /amr/task_request',
        )

    def handle_task_request(self, message: String) -> None:
        """Reject bad requests without publishing a pose or stopping the node."""
        try:
            request = parse_task_request(message.data)
        except InvalidRequestError as exc:
            self._publish_status('INVALID_REQUEST', str(exc))
            return

        self._publish_status('TASK_RECEIVED', f'action={request.action}', request)
        try:
            rack = self.inventory.resolve_sku(request.sku)
        except UnknownSKUError as exc:
            self._publish_status('INVALID_SKU', str(exc), request)
            return
        except InventoryError as exc:
            # Normally prevented by full inventory validation during startup.
            self._publish_status('INVENTORY_ERROR', str(exc), request)
            return

        self._publish_status('SKU_RESOLVED', f'rack={rack.rack_id}', request)
        target = self.create_target_pose(rack)
        self.target_publisher.publish(target)
        self._publish_status(
            'TARGET_GENERATED',
            f'rack={rack.rack_id} frame=map x={rack.x} y={rack.y} yaw={rack.yaw}',
            request,
        )

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
        """Publish readable resolution events and mirror them to the ROS log."""
        task_id = request.task_id if request else '-'
        sku = request.sku if request else '-'
        status = f'{state} task_id={task_id} sku={sku}: {detail}'
        self.status_publisher.publish(String(data=status))
        if state in {'INVALID_REQUEST', 'INVALID_SKU', 'INVENTORY_ERROR'}:
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
        # The constructor already logged the configuration failure.
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
