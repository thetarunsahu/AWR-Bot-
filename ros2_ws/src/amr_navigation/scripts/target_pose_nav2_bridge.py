#!/usr/bin/env python3
from typing import Optional

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node
from std_msgs.msg import String


class TargetPoseNav2Bridge(Node):
    """Convert Mission Manager PoseStamped targets into Nav2 goals."""

    def __init__(self) -> None:
        super().__init__("target_pose_nav2_bridge")
        self._client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self._subscription = self.create_subscription(PoseStamped, "/amr/target_pose", self._on_target_pose, 10)
        self._status_pub = self.create_publisher(String, "/amr/navigation_status", 10)
        self._active_goal: Optional[ClientGoalHandle] = None

    def _publish_status(self, text: str) -> None:
        msg = String(); msg.data = text
        self._status_pub.publish(msg)
        self.get_logger().info(text)

    def _on_target_pose(self, pose: PoseStamped) -> None:
        if not pose.header.frame_id:
            pose.header.frame_id = "map"
        if not self._client.wait_for_server(timeout_sec=1.0):
            self._publish_status("NAV2_UNAVAILABLE")
            return
        self._send_goal(pose)

    def _send_goal(self, pose: PoseStamped) -> None:
        goal = NavigateToPose.Goal(); goal.pose = pose
        self._publish_status("NAVIGATION_GOAL_SENT")
        future = self._client.send_goal_async(goal)
        future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self._publish_status("NAVIGATION_GOAL_REJECTED")
            return
        self._active_goal = goal_handle
        self._publish_status("NAVIGATION_ACTIVE")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(lambda f, h=goal_handle: self._result_callback(f, h))

    def _result_callback(self, future, goal_handle: ClientGoalHandle) -> None:
        status = future.result().status
        if self._active_goal == goal_handle:
            self._active_goal = None
        if status == 4:
            self._publish_status("NAVIGATION_SUCCEEDED")
        elif status == 5:
            self._publish_status("NAVIGATION_CANCELED")
        elif status == 6:
            self._publish_status("NAVIGATION_ABORTED")
        else:
            self._publish_status(f"NAVIGATION_FINISHED_STATUS_{status}")


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TargetPoseNav2Bridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node(); rclpy.shutdown()


if __name__ == "__main__":
    main()
