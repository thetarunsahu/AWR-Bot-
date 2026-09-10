"""Run one complete warehouse mission and print its live status stream."""

import argparse
import json
import sys
import time
from uuid import uuid4

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.utilities import remove_ros_args
from std_msgs.msg import String


TERMINAL_STATES = {
    'MISSION_COMPLETE': 0,
    'MISSION_FAILED': 2,
    'BUSY': 3,
    'INVALID_SKU': 4,
    'INVALID_REQUEST': 5,
    'INVENTORY_ERROR': 6,
    'MISSION_CANCELED': 7,
}


class WarehouseDemo(Node):
    def __init__(self, task_id: str) -> None:
        super().__init__('warehouse_demo')
        self.task_id = task_id
        self.result_code: int | None = None
        self.publisher = self.create_publisher(String, '/amr/task_request', 10)
        self.cancel_publisher = self.create_publisher(String, '/amr/cancel_request', 10)
        self.subscription = self.create_subscription(
            String,
            '/amr/mission_status',
            self._on_status,
            10,
        )

    def _on_status(self, message: String) -> None:
        text = message.data.strip()
        if f'task_id={self.task_id}' not in text:
            return
        self.get_logger().info(text)
        state = text.split(' ', 1)[0]
        if state in TERMINAL_STATES:
            self.result_code = TERMINAL_STATES[state]

    def cancel_active_task(self) -> None:
        """Ask Mission Manager/Nav2 to stop this task before the client exits."""
        self.cancel_publisher.publish(String(data=self.task_id))
        deadline = time.monotonic() + 1.0
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)


def main(args: list[str] | None = None) -> int:
    raw_args = sys.argv if args is None else ['warehouse_demo', *args]
    parser = argparse.ArgumentParser(
        description='Send one DELIVER task and wait for rack pickup + packing delivery.'
    )
    parser.add_argument('sku', help='Inventory SKU, e.g. SKU004')
    parser.add_argument('--timeout', type=float, default=210.0)
    parser.add_argument('--task-id', default=f'DEMO-{uuid4().hex[:10]}')
    options = parser.parse_args(remove_ros_args(args=raw_args)[1:])
    if options.timeout <= 0:
        parser.error('--timeout must be greater than zero')

    rclpy.init(args=raw_args[1:])
    node = WarehouseDemo(options.task_id)
    payload = json.dumps({
        'task_id': options.task_id,
        'sku': options.sku,
        'action': 'DELIVER',
    })

    try:
        discovery_deadline = time.monotonic() + 10.0
        while rclpy.ok() and node.publisher.get_subscription_count() == 0:
            if time.monotonic() >= discovery_deadline:
                node.get_logger().error(
                    'Mission Manager not discovered on /amr/task_request.'
                )
                return 10
            rclpy.spin_once(node, timeout_sec=0.1)

        node.publisher.publish(String(data=payload))
        node.get_logger().info(f'SENT {payload}')

        deadline = time.monotonic() + options.timeout
        while rclpy.ok() and node.result_code is None:
            if time.monotonic() >= deadline:
                node.get_logger().error(
                    f'Mission timed out after {options.timeout:.0f}s; cancelling task.'
                )
                node.cancel_active_task()
                return 11
            rclpy.spin_once(node, timeout_sec=0.2)

        return node.result_code if node.result_code is not None else 12
    except (KeyboardInterrupt, ExternalShutdownException):
        if rclpy.ok():
            node.cancel_active_task()
        return 130
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
