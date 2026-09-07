#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class NavBotController(Node):
    def __init__(self):
        super().__init__('navbot_controller')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.move)

    def move(self):
        msg = Twist()
        msg.linear.x = 0.4
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = NavBotController()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
