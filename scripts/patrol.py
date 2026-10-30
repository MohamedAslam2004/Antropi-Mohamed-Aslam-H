#!/usr/bin/env python3
"""Patrol the warehouse: left room -> through the gap -> right room -> back.

Uses nav2_simple_commander, so Nav2 does all the planning and driving.
Run from a fresh start (robot at its spawn point), or pass --keep-pose
to skip setting the initial pose.
"""
import sys

import rclpy
from rclpy.duration import Duration
from rclpy.utilities import remove_ros_args
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

SPAWN = (-4.0, -3.0)

# (x, y) in the map frame. Chosen with clearance from walls and crates.
WAYPOINTS = [
    ('left room, near the partition', (-3.5, 2.0)),
    ('gap in the partition',          (0.0, 3.0)),
    ('right room, top',               (3.0, 3.0)),
    ('right room, bottom',            (4.0, -3.0)),
    ('back to start',                 SPAWN),
]


def make_pose(nav, x, y, yaw_w=1.0):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = nav.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.w = yaw_w
    return pose


def main():
    args = remove_ros_args(sys.argv)[1:]
    rclpy.init()
    nav = BasicNavigator()

    if '--keep-pose' not in args:
        nav.setInitialPose(make_pose(nav, *SPAWN))
    else:
        nav.initial_pose_received = True

    nav.waitUntilNav2Active()
    nav.get_logger().info('Nav2 is active, starting patrol')

    poses = [make_pose(nav, *xy) for _, xy in WAYPOINTS]
    nav.followWaypoints(poses)

    last = -1
    while not nav.isTaskComplete():
        fb = nav.getFeedback()
        if fb and fb.current_waypoint != last:
            last = fb.current_waypoint
            nav.get_logger().info(
                'Heading to waypoint %d/%d: %s'
                % (last + 1, len(WAYPOINTS), WAYPOINTS[last][0]))

    result = nav.getResult()
    if result == TaskResult.SUCCEEDED:
        nav.get_logger().info('Patrol complete')
    elif result == TaskResult.CANCELED:
        nav.get_logger().warn('Patrol canceled')
    else:
        nav.get_logger().error('Patrol failed')

    nav.lifecycleShutdown() if '--shutdown' in args else None
    rclpy.shutdown()


if __name__ == '__main__':
    main()
