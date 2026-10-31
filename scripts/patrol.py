#!/usr/bin/env python3
"""Patrol the loading bay by sending a list of waypoints to Nav2.

Waypoints are written in Gazebo world coordinates (as in loading_bay.sdf)
and converted to the map frame, whose origin is the robot's spawn point.

Start it with the robot at its spawn point so the initial pose is correct,
or pass --keep-pose to leave the current localization untouched.
"""
import argparse
import sys

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.utilities import remove_ros_args

SPAWN = (-4.0, -3.0)
WORLD_TO_MAP = (4.0, 3.0)  # map = world + WORLD_TO_MAP

WAYPOINTS = [
    ('south-west lane',        (-2.2, -2.4)),
    ('south middle',           (1.5, -2.6)),
    ('centre east',            (2.4, -0.2)),
    ('north-east corner',      (4.0, 2.9)),
    ('between pillar & crate', (-2.0, 1.2)),
    ('back to start',          SPAWN),
]


def to_map(xy):
    return xy[0] + WORLD_TO_MAP[0], xy[1] + WORLD_TO_MAP[1]


def make_pose(nav, x, y):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = nav.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.orientation.w = 1.0
    return pose


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--keep-pose', action='store_true',
                        help='do not set the initial pose')
    parser.add_argument('--shutdown', action='store_true',
                        help='shut Nav2 down when the patrol ends')
    return parser.parse_args(remove_ros_args(sys.argv)[1:])


def main():
    args = parse_args()
    rclpy.init()
    nav = BasicNavigator()

    if args.keep_pose:
        nav.initial_pose_received = True
    else:
        nav.setInitialPose(make_pose(nav, *to_map(SPAWN)))

    nav.waitUntilNav2Active()
    nav.get_logger().info('Nav2 is active, starting patrol')

    nav.followWaypoints([make_pose(nav, *to_map(xy)) for _, xy in WAYPOINTS])

    current = -1
    while not nav.isTaskComplete():
        feedback = nav.getFeedback()
        if feedback and feedback.current_waypoint != current:
            current = feedback.current_waypoint
            nav.get_logger().info(
                f'Waypoint {current + 1}/{len(WAYPOINTS)}: '
                f'{WAYPOINTS[current][0]}')

    result = nav.getResult()
    if result == TaskResult.SUCCEEDED:
        nav.get_logger().info('Patrol complete')
    elif result == TaskResult.CANCELED:
        nav.get_logger().warn('Patrol canceled')
    else:
        nav.get_logger().error('Patrol failed')
    if nav.result_future and nav.result_future.result():
       action_result=nav.result_future.result();
        
       nav.get_logger().error(f'Action staus:{action_result.status}')
       nav.get_logger().error(f'Action result:{action_result.result}')

    if args.shutdown:
        nav.lifecycleShutdown()
    rclpy.shutdown()
    return 0 if result == TaskResult.SUCCEEDED else 1


if __name__ == '__main__':
    sys.exit(main())
