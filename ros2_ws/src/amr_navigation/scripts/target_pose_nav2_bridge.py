#!/usr/bin/env python3
"""Bridge Mission Manager targets to Nav2 with bounded recovery and watchdogs."""

from copy import deepcopy
import time
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
        self.declare_parameter('goal_timeout_sec', 95.0)
        self.declare_parameter('no_progress_timeout_sec', 30.0)
        self.declare_parameter('progress_epsilon_m', 0.10)
        self._max_retries = int(self.get_parameter('max_retries').value)
        self._retry_delay = float(self.get_parameter('retry_delay_sec').value)
        self._goal_timeout = float(self.get_parameter('goal_timeout_sec').value)
        self._no_progress_timeout = float(
            self.get_parameter('no_progress_timeout_sec').value
        )
        self._progress_epsilon = float(
            self.get_parameter('progress_epsilon_m').value
        )

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
        self._cancel_subscription = self.create_subscription(
            String,
            '/amr/navigation_cancel',
            self._on_navigation_cancel,
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
        self._watchdog_timer = None
        self._attempt_started = 0.0
        self._last_progress = 0.0
        self._best_distance: Optional[float] = None
        self._cancel_for_retry = False

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
        future = self._client.send_goal_async(
            goal,
            feedback_callback=lambda msg, g=generation: self._feedback_callback(msg, g),
        )
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
        now = time.monotonic()
        self._attempt_started = now
        self._last_progress = now
        self._best_distance = None
        self._cancel_for_retry = False
        self._start_watchdog(generation)
        self._publish_status('NAVIGATION_ACTIVE')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda f, h=goal_handle, g=generation: self._result_callback(f, h, g)
        )

    def _feedback_callback(self, feedback_msg, generation: int) -> None:
        if generation != self._goal_generation:
            return
        try:
            distance = float(feedback_msg.feedback.distance_remaining)
        except (AttributeError, TypeError, ValueError):
            return

        if self._best_distance is None or distance < self._best_distance - self._progress_epsilon:
            self._best_distance = distance
            self._last_progress = time.monotonic()

    def _start_watchdog(self, generation: int) -> None:
        self._stop_watchdog()

        def check_progress() -> None:
            if generation != self._goal_generation or self._active_goal is None:
                return
            if self._cancel_for_retry:
                return
            now = time.monotonic()
            elapsed = now - self._attempt_started
            stalled = now - self._last_progress
            if elapsed >= self._goal_timeout:
                self._cancel_active_for_recovery(generation, 'goal_timeout')
            elif self._best_distance is not None and stalled >= self._no_progress_timeout:
                self._cancel_active_for_recovery(generation, 'no_progress')

        self._watchdog_timer = self.create_timer(1.0, check_progress)

    def _stop_watchdog(self) -> None:
        if self._watchdog_timer is not None:
            self.destroy_timer(self._watchdog_timer)
            self._watchdog_timer = None

    def _cancel_active_for_recovery(self, generation: int, reason: str) -> None:
        if generation != self._goal_generation or self._active_goal is None:
            return
        if self._cancel_for_retry:
            return

        self._cancel_for_retry = True
        self._stop_watchdog()
        self.get_logger().warning(
            f'Cancelling stalled Nav2 goal for recovery: {reason}'
        )
        future = self._active_goal.cancel_goal_async()
        future.add_done_callback(
            lambda _f, g=generation, r=reason: self._cancel_complete_for_recovery(g, r)
        )

    def _cancel_complete_for_recovery(self, generation: int, reason: str) -> None:
        if generation != self._goal_generation:
            return
        self._active_goal = None
        self._cancel_for_retry = False
        self.get_logger().warning(f'Nav2 goal cancelled for retry: {reason}')
        self._recover_or_abort(generation, reason=reason)

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
        self._stop_watchdog()

        # A status=5 result is expected while the watchdog is deliberately
        # cancelling a stuck goal. The cancel callback owns the retry path.
        if status == 5 and self._cancel_for_retry:
            return

        if status == 4:
            self._retry_count = 0
            self._publish_status('NAVIGATION_SUCCEEDED')
        elif status == 5:
            self._publish_status('NAVIGATION_CANCELED')
        elif status == 6:
            self._recover_or_abort(generation, reason='nav2_aborted')
        else:
            self._publish_status(f'NAVIGATION_FINISHED_STATUS_{status}')

    def _recover_or_abort(self, generation: int, reason: str) -> None:
        """Clear stale costmaps and retry a bounded number of times."""
        if self._last_pose is None or self._retry_count >= self._max_retries:
            self._publish_status('NAVIGATION_ABORTED')
            return

        self._retry_count += 1
        self._publish_status(
            f'NAVIGATION_RETRYING attempt={self._retry_count}/{self._max_retries} reason={reason}'
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

    def _on_navigation_cancel(self, _message: String) -> None:
        """Cancel an active Nav2 goal when the mission layer times out/cancels."""
        self._goal_generation += 1
        self._stop_watchdog()
        if self._retry_timer is not None:
            self.destroy_timer(self._retry_timer)
            self._retry_timer = None

        goal_handle = self._active_goal
        self._active_goal = None
        self._last_pose = None
        self._retry_count = 0
        self._cancel_for_retry = False

        if goal_handle is not None:
            try:
                goal_handle.cancel_goal_async()
            except Exception as exc:  # pragma: no cover
                self.get_logger().warning(f'Nav2 cancel request failed: {exc}')
        self._publish_status('NAVIGATION_CANCELED')


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
