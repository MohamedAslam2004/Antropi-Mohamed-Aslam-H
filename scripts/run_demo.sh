#!/usr/bin/env bash
# Clean start: kill stale processes, launch the sim, wait, launch Nav2.
pkill -9 -f component_container ; pkill -9 -f rviz2 ; pkill -9 -f "gz sim"
pkill -9 -f cmd_vel_relay ; pkill -9 -f parameter_bridge
source /opt/ros/jazzy/setup.bash
source ~/antropi_ws/install/setup.bash
export TURTLEBOT3_MODEL=waffle
export LIBGL_ALWAYS_SOFTWARE=1
ros2 daemon stop ; sleep 2 ; ros2 daemon start

ros2 launch antropi_nav_demo sim.launch.py > /tmp/sim.log 2>&1 &
SIM=$!
trap 'kill $SIM 2>/dev/null; pkill -f "gz sim"' EXIT

echo "Sim starting, waiting 25 s. Do not move the robot."
sleep 25
ros2 launch antropi_nav_demo nav.launch.py
