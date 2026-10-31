import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (ExecuteProcess, IncludeLaunchDescription,
                            SetEnvironmentVariable)
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    pkg = get_package_share_directory('navigation')
    tb3 = get_package_share_directory('turtlebot3_gazebo')

    world = os.path.join(pkg, 'worlds', 'loading_bay.sdf')

    # Gazebo needs both the demo's models and the TurtleBot3 meshes.
    resource_path = SetEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.pathsep.join([os.path.join(pkg, 'models'),
                         os.path.join(tb3, 'models')]))

    gz = ExecuteProcess(
        cmd=['gz', 'sim', '-r', '-v2', '--render-engine', 'ogre2', world],
        output='screen')

    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3, 'launch', 'robot_state_publisher.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items())

    # The spawn point is also the origin of the SLAM map (see scripts/patrol.py).
    spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3, 'launch', 'spawn_turtlebot3.launch.py')),
        launch_arguments={'x_pose': '-4.0', 'y_pose': '-3.0'}.items())

    return LaunchDescription([resource_path, gz, robot_state_publisher, spawn])
