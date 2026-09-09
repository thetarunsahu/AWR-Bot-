"""Exercise the final rack-pickup -> packing-delivery mission state machine."""

import json
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
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return
        executor.spin_once(timeout_sec=0.02)
    assert condition(), "Timed out waiting for ROS discovery or mission output"


def states(statuses: list[str]) -> list[str]:
    return [status.split(" ", 1)[0] for status in statuses]


def test_complete_delivery_mission_and_invalid_recovery() -> None:
    context = Context()
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
        modules: list[str] = []
        target_subscription = observer.create_subscription(
            PoseStamped, "/amr/target_pose", poses.append, 10
        )
        status_subscription = observer.create_subscription(
            String, "/amr/mission_status", lambda m: statuses.append(m.data), 10
        )
        module_subscription = observer.create_subscription(
            String, "/amr/module_command", lambda m: modules.append(m.data), 10
        )
        requests = observer.create_publisher(String, "/amr/task_request", 10)
        nav_status = observer.create_publisher(String, "/amr/navigation_status", 10)

        executor.add_node(observer)
        executor.add_node(manager)
        spin_until(
            executor,
            lambda: requests.get_subscription_count() > 0
            and nav_status.get_subscription_count() > 0
            and target_subscription.get_publisher_count() > 0
            and status_subscription.get_publisher_count() > 0
            and module_subscription.get_publisher_count() > 0,
        )

        requests.publish(String(data=json.dumps({
            "task_id": "TEST001",
            "sku": "SKU001",
            "action": "DELIVER",
        })))
        spin_until(executor, lambda: len(poses) == 1 and "RACK_TARGET_GENERATED" in states(statuses))
        assert states(statuses)[:3] == [
            "TASK_RECEIVED", "SKU_RESOLVED", "RACK_TARGET_GENERATED"
        ]
        assert poses[0].header.frame_id == "map"
        assert poses[0].pose.position.x == pytest.approx(-7.0)
        assert poses[0].pose.position.y == pytest.approx(2.2)

        # Recovery telemetry must not terminate or reset the active mission.
        for value in [
            "NAVIGATION_GOAL_SENT",
            "NAVIGATION_ACTIVE",
            "NAVIGATION_RETRYING attempt=1/2",
            "NAVIGATION_GOAL_SENT",
            "NAVIGATION_ACTIVE",
            "NAVIGATION_SUCCEEDED",
        ]:
            nav_status.publish(String(data=value))
            executor.spin_once(timeout_sec=0.05)

        spin_until(
            executor,
            lambda: len(poses) == 2 and "PACKING_TARGET_GENERATED" in states(statuses),
        )
        assert "RECOVERY_RETRY" in states(statuses)
        assert "ARRIVED_RACK" in states(statuses)
        assert "LOAD_ACQUIRED" in states(statuses)
        assert modules and modules[0].startswith("PICKUP task_id=TEST001 sku=SKU001")
        assert poses[1].pose.position.x == pytest.approx(9.0)
        assert poses[1].pose.position.y == pytest.approx(-7.5)

        for value in ["NAVIGATION_GOAL_SENT", "NAVIGATION_ACTIVE", "NAVIGATION_SUCCEEDED"]:
            nav_status.publish(String(data=value))
            executor.spin_once(timeout_sec=0.05)

        spin_until(executor, lambda: "MISSION_COMPLETE" in states(statuses))
        assert "ARRIVED_PACKING" in states(statuses)
        assert len(modules) == 2
        assert modules[1].startswith("DROP task_id=TEST001 sku=SKU001")

        # A terminal mission clears BUSY state; the manager can accept another request.
        statuses.clear()
        requests.publish(String(data=json.dumps({
            "task_id": "TEST002",
            "sku": "NO_SUCH_SKU",
            "action": "DELIVER",
        })))
        spin_until(executor, lambda: "INVALID_SKU" in states(statuses))
        assert states(statuses)[:2] == ["TASK_RECEIVED", "INVALID_SKU"]
    finally:
        executor.shutdown()
        if manager is not None:
            manager.destroy_node()
        observer.destroy_node()
        context.try_shutdown()
