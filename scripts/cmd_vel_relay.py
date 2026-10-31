#!/usr/bin/env python3
"""Forward /cmd_vel_smoothed to /cmd_vel.

Workaround for collision_monitor not publishing in the simulation VM.
"""
import rclpy
from geometry_msgs.msg import TwistStamped
from rclpy.node import Node


class CmdVelRelay(Node):
    def __init__(self):
        super().__init__('cmd_vel_relay')
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.create_subscription(
            TwistStamped, '/cmd_vel_smoothed', self.pub.publish, 10)
        self.get_logger().info('Relaying /cmd_vel_smoothed to /cmd_vel')


def main():
    rclpy.init()
    rclpy.spin(CmdVelRelay())


if __name__ == '__main__':
    main()
