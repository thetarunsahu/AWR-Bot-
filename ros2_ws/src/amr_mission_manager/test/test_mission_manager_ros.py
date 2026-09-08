"""Exercise the real ROS topics when run in a sourced ROS 2 environment."""

import json
import math
import os
from pathlib import Path
import time
from typing import Callable

import pytest

rclpy = pytest.importorskip("rclpy", reason="ROS 2 is not installed or sourced")

from geometry_msgs.msg import PoseStamped  # noqa: E402
from rclpy.context import Context  # noqa: E402
from rclpy.executors import SingleThreadedExecutor  # noqa: E402
from rclpy.node import Node  # noqa: E402
from rclpy.parameter import Parameter  # noqa: E402
from std_msgs.msg import String  # noqa: E402

from amr_mission_manager.mission_manager import MissionManager  # noqa: E402


def spin_until(
    executor: SingleThreadedExecutor,
    condition: Callable[[], bool],
    timeout: float = 5.0,
) -> None:
    """Wait for a graph/message condition without an unbounded test hang."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return
        executor.spin_once(timeout_sec=0.02)
    assert condition(), "Timed out waiting for ROS discovery or mission output"


def test_requests_publish_goals_and_recover_from_invalid_input() -> None:
    """Verify discovery, states, poses, rejection, and subsequent valid tasks."""
    context = Context()
    # Isolate this test from nodes in the developer's normal ROS domain.
    rclpy.init(args=[], context=context, domain_id=100 + os.getpid() % 100)
    executor = SingleThreadedExecutor(context=context)
    observer = Node("mission_manager_test_observer", context=context)
    manager = None
    try:
        inventory_file = Path(__file__).resolve().parents[1] / "config" / "inventory.yaml"
        manager = MissionManager(
            context=context,
            parameter_overrides=[
                Parameter("inventory_file", Parameter.Type.STRING, str(inventory_file)),
            ],
        )
        poses: list[PoseStamped] = []
        statuses: list[str] = []
        target_subscription = observer.create_subscription(
            PoseStamped, "/amr/target_pose", poses.append, 10
        )
        status_subscription = observer.create_subscription(
            String, "/amr/mission_status", lambda message: statuses.append(message.data), 10
        )
        requests = observer.create_publisher(String, "/amr/task_request", 10)
        executor.add_node(observer)
        executor.add_node(manager)
        spin_until(
            executor,
            lambda: requests.get_subscription_count() > 0
            and target_subscription.get_publisher_count() > 0
            and status_subscription.get_publisher_count() > 0,
        )

        def send(sku: str, task_id: str) -> None:
            """Publish one request only after topic discovery is complete."""
            requests.publish(
                String(data=json.dumps({"task_id": task_id, "sku": sku, "action": "DELIVER"}))
            )

        send("SKU001", "TEST001")
        spin_until(executor, lambda: len(poses) == 1 and len(statuses) == 3)
        assert [status.split()[0] for status in statuses] == [
            "TASK_RECEIVED", "SKU_RESOLVED", "TARGET_GENERATED"
        ]
        assert all("task_id=TEST001" in status and "sku=SKU001" in status for status in statuses)
        pose = poses[0]
        assert pose.header.frame_id == "map"
        assert pose.header.stamp.sec > 0
        stamp = pose.header.stamp.sec * 1_000_000_000 + pose.header.stamp.nanosec
        assert abs(observer.get_clock().now().nanoseconds - stamp) < 5_000_000_000
        assert pose.pose.position.x == pytest.approx(2.0)
        assert pose.pose.position.y == pytest.approx(4.0)
        assert pose.pose.position.z == pytest.approx(0.0)
        assert pose.pose.orientation.x == pytest.approx(0.0)
        assert pose.pose.orientation.y == pytest.approx(0.0)
        assert pose.pose.orientation.z == pytest.approx(0.0)
        assert pose.pose.orientation.w == pytest.approx(1.0)

        statuses.clear()
        send("SKU_DOES_NOT_EXIST", "TEST002")
        spin_until(executor, lambda: len(statuses) >= 2)
        assert [status.split()[0] for status in statuses] == ["TASK_RECEIVED", "INVALID_SKU"]

        statuses.clear()
        requests.publish(String(data="{malformed JSON"))
        spin_until(executor, lambda: bool(statuses))
        assert [status.split()[0] for status in statuses] == ["INVALID_REQUEST"]

        # Allow queued deliveries to drain before proving neither rejected task
        # produced a target. A later valid task must still work on the same node.
        deadline = time.monotonic() + 0.2
        while time.monotonic() < deadline:
            executor.spin_once(timeout_sec=0.02)
        assert len(poses) == 1
        statuses.clear()
        send("SKU002", "TEST003")
        spin_until(executor, lambda: len(poses) == 2 and len(statuses) == 3)
        assert [status.split()[0] for status in statuses] == [
            "TASK_RECEIVED", "SKU_RESOLVED", "TARGET_GENERATED"
        ]
        assert poses[1].pose.position.x == pytest.approx(6.5)
        assert poses[1].pose.position.y == pytest.approx(1.5)
        orientation = poses[1].pose.orientation
        assert orientation.z == pytest.approx(math.sin(1.57 / 2.0))
        assert orientation.w == pytest.approx(math.cos(1.57 / 2.0))
        assert sum(value ** 2 for value in (
            orientation.x, orientation.y, orientation.z, orientation.w
        )) == pytest.approx(1.0)
    finally:
        executor.shutdown()
        if manager is not None:
            manager.destroy_node()
        observer.destroy_node()
        context.try_shutdown()
