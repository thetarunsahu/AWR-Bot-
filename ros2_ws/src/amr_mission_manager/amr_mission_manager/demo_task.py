"""Publish one warehouse task after ROS discovers a task subscriber."""

import argparse
import json
import math
import sys
import time
from uuid import uuid4

import rclpy
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.utilities import remove_ros_args
from std_msgs.msg import String

from amr_mission_manager.mission_logic import InvalidRequestError, parse_task_request


def positive_timeout(value: str) -> float:
    """Parse a finite, positive timeout for discovery and DDS acknowledgment."""
    try:
        timeout = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError('timeout must be a number') from exc
    if not math.isfinite(timeout) or timeout <= 0.0:
        raise argparse.ArgumentTypeError('timeout must be finite and greater than zero')
    return timeout


def main(args: list[str] | None = None) -> int:
    """Send a single DELIVER request; report missing subscribers as a failure."""
    raw_args = sys.argv if args is None else ['send_demo_task', *args]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sku', help='Inventory SKU, for example SKU001')
    parser.add_argument('--task-id', default=f'TASK-{uuid4().hex[:12]}')
    parser.add_argument('--action', default='DELIVER', choices=['DELIVER'])
    parser.add_argument('--timeout', type=positive_timeout, default=5.0)
    options = parser.parse_args(remove_ros_args(args=raw_args)[1:])
    payload = json.dumps({
        'task_id': options.task_id,
        'sku': options.sku,
        'action': options.action,
    })
    try:
        parse_task_request(payload)
    except InvalidRequestError as exc:
        parser.error(str(exc))

    rclpy.init(args=raw_args[1:])
    node = Node('send_demo_task')
    try:
        publisher = node.create_publisher(String, '/amr/task_request', 10)
        deadline = time.monotonic() + options.timeout
        while rclpy.ok() and publisher.get_subscription_count() == 0:
            remaining = deadline - time.monotonic()
            if remaining <= 0.0:
                node.get_logger().error(
                    'No /amr/task_request subscriber discovered; start mission_manager.',
                )
                return 1
            rclpy.spin_once(node, timeout_sec=min(0.1, remaining))
        if not rclpy.ok():
            return 1
        publisher.publish(String(data=payload))
        if not publisher.wait_for_all_acked(Duration(seconds=options.timeout)):
            node.get_logger().error('Timed out waiting for DDS acknowledgment.')
            return 1
        node.get_logger().info(f'Sent {payload}; inspect /amr/mission_status for resolution.')
        return 0
    except (KeyboardInterrupt, ExternalShutdownException):
        return 130
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
