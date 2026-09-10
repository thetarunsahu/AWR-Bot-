#!/usr/bin/env python3
import time
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class MotionSmokeTest(Node):
    def __init__(self) -> None:
        super().__init__("motion_smoke_test")
        self.publisher = self.create_publisher(Twist, "/cmd_vel", 10)

    def publish_for(self, linear_x: float, angular_z: float, seconds: float) -> None:
        msg = Twist()
        msg.linear.x = linear_x
        msg.angular.z = angular_z
        end_time = time.monotonic() + seconds
        while rclpy.ok() and time.monotonic() < end_time:
            self.publisher.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.0)
            time.sleep(0.1)

    def stop(self) -> None:
        self.publisher.publish(Twist())


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MotionSmokeTest()
    try:
        node.get_logger().info("Forward test")
        node.publish_for(0.30, 0.0, 2.0)
        node.stop(); time.sleep(0.5)
        node.get_logger().info("Rotate-left test")
        node.publish_for(0.0, 0.70, 2.0)
        node.stop(); time.sleep(0.5)
        node.get_logger().info("Backward test")
        node.publish_for(-0.20, 0.0, 1.5)
        node.stop()
        node.get_logger().info("Motion smoke test complete")
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
