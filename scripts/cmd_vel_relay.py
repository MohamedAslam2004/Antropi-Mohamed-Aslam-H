#!/usr/bin/env python3
"""Forward /cmd_vel_smoothed to /cmd_vel (workaround for silent collision_monitor)."""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped


class Relay(Node):
    def __init__(self):
        super().__init__('cmd_vel_relay')
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.create_subscription(TwistStamped, '/cmd_vel_smoothed', self.pub.publish, 10)
        self.get_logger().info('Relaying /cmd_vel_smoothed -> /cmd_vel')


def main():
    rclpy.init()
    rclpy.spin(Relay())


if __name__ == '__main__':
    main()
