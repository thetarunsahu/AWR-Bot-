#!/usr/bin/env python3
"""Bridge Mission Manager targets to Nav2 with lightweight demo recovery."""

from copy import deepcopy
from typing import Optional

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from nav2_msgs.srv import ClearEntireCostmap
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from rclpy.node import Node
from std_msgs.msg import String


class TargetPoseNav2Bridge(Node):
    """Convert Mission Manager PoseStamped targets into resilient Nav2 goals."""

    def __init__(self) -> None:
        super().__init__('target_pose_nav2_bridge')

        self.declare_parameter('max_retries', 2)
        self.declare_parameter('retry_delay_sec', 1.0)
        self._max_retries = int(self.get_parameter('max_retries').value)
        self._retry_delay = float(self.get_parameter('retry_delay_sec').value)

        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._global_clear = self.create_client(
            ClearEntireCostmap,
            '/global_costmap/clear_entirely_global_costmap',
        )
        self._local_clear = self.create_client(
            ClearEntireCostmap,
            '/local_costmap/clear_entirely_local_costmap',
        )

        self._subscription = self.create_subscription(
            PoseStamped,
            '/amr/target_pose',
            self._on_target_pose,
            10,
        )
        self._status_pub = self.create_publisher(
            String,
            '/amr/navigation_status',
            10,
        )

        self._active_goal: Optional[ClientGoalHandle] = None
        self._last_pose: Optional[PoseStamped] = None
        self._retry_count = 0
        self._goal_generation = 0
        self._retry_timer = None

    def _publish_status(self, text: str) -> None:
        self._status_pub.publish(String(data=text))
        self.get_logger().info(text)

    def _on_target_pose(self, pose: PoseStamped) -> None:
        if self._active_goal is not None:
            self._publish_status('NAVIGATION_GOAL_REJECTED')
            self.get_logger().warning('Received a new AMR target while Nav2 is busy.')
            return

        target = deepcopy(pose)
        if not target.header.frame_id:
            target.header.frame_id = 'map'

        if not self._client.wait_for_server(timeout_sec=2.0):
            self._publish_status('NAV2_UNAVAILABLE')
            return

        self._goal_generation += 1
        self._retry_count = 0
        self._last_pose = target
        self._send_goal(target, self._goal_generation)

    def _send_goal(self, pose: PoseStamped, generation: int) -> None:
        if generation != self._goal_generation:
            return

        target = deepcopy(pose)
        target.header.stamp = self.get_clock().now().to_msg()
        goal = NavigateToPose.Goal()
        goal.pose = target

        self._publish_status('NAVIGATION_GOAL_SENT')
        future = self._client.send_goal_async(goal)
        future.add_done_callback(
            lambda f, g=generation: self._goal_response_callback(f, g)
        )

    def _goal_response_callback(self, future, generation: int) -> None:
        if generation != self._goal_generation:
            return
        try:
            goal_handle = future.result()
        except Exception as exc:  # pragma: no cover - transport failure path
            self.get_logger().error(f'NavigateToPose goal request failed: {exc}')
            self._publish_status('NAV2_UNAVAILABLE')
            return

        if not goal_handle.accepted:
            self._publish_status('NAVIGATION_GOAL_REJECTED')
            return

        self._active_goal = goal_handle
        self._publish_status('NAVIGATION_ACTIVE')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda f, h=goal_handle, g=generation: self._result_callback(f, h, g)
        )

    def _result_callback(
        self,
        future,
        goal_handle: ClientGoalHandle,
        generation: int,
    ) -> None:
        if generation != self._goal_generation:
            return

        try:
            status = future.result().status
        except Exception as exc:  # pragma: no cover - transport failure path
            self.get_logger().error(f'NavigateToPose result failed: {exc}')
            status = 6

        if self._active_goal == goal_handle:
            self._active_goal = None

        if status == 4:
            self._retry_count = 0
            self._publish_status('NAVIGATION_SUCCEEDED')
        elif status == 5:
            self._publish_status('NAVIGATION_CANCELED')
        elif status == 6:
            self._recover_or_abort(generation)
        else:
            self._publish_status(f'NAVIGATION_FINISHED_STATUS_{status}')

    def _recover_or_abort(self, generation: int) -> None:
        """Clear stale costmaps and retry a bounded number of times."""
        if self._last_pose is None or self._retry_count >= self._max_retries:
            self._publish_status('NAVIGATION_ABORTED')
            return

        self._retry_count += 1
        self._publish_status(
            f'NAVIGATION_RETRYING attempt={self._retry_count}/{self._max_retries}'
        )
        self._clear_costmaps()
        self._schedule_retry(generation)

    def _clear_costmaps(self) -> None:
        request = ClearEntireCostmap.Request()
        for name, client in (
            ('global', self._global_clear),
            ('local', self._local_clear),
        ):
            if client.service_is_ready() or client.wait_for_service(timeout_sec=0.25):
                client.call_async(request)
                self.get_logger().info(f'Requested {name} costmap clear before retry.')
            else:
                self.get_logger().warning(
                    f'{name.capitalize()} costmap clear service unavailable; retrying anyway.'
                )

    def _schedule_retry(self, generation: int) -> None:
        if self._retry_timer is not None:
            self.destroy_timer(self._retry_timer)
            self._retry_timer = None

        def retry_once() -> None:
            if self._retry_timer is not None:
                self.destroy_timer(self._retry_timer)
                self._retry_timer = None
            if generation == self._goal_generation and self._last_pose is not None:
                self._send_goal(self._last_pose, generation)

        self._retry_timer = self.create_timer(self._retry_delay, retry_once)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TargetPoseNav2Bridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
