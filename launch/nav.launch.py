import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('antropi_nav_demo')
    nav2 = get_package_share_directory('nav2_bringup')

    # My generated map and my tuned parameters
    map_yaml = os.path.join(pkg, 'maps', 'loading_bay.yaml')
    params = os.path.join(pkg, 'config', 'nav2_params.yaml')

    bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': map_yaml,
            'params_file': params,
            'use_sim_time': 'true',
            'autostart': 'true',
        }.items())

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2, 'launch', 'rviz_launch.py')))

    # collision_monitor never forwarded velocity in my VM, so the smoothed
    # command goes to the robot through this small relay instead.
    relay = Node(
        package='antropi_nav_demo',
        executable='cmd_vel_relay.py',
        name='cmd_vel_relay',
        parameters=[{'use_sim_time': True}],
        output='screen')

    return LaunchDescription([bringup, rviz, relay])
