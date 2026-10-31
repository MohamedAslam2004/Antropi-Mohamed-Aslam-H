#!/usr/bin/env bash
# Clean start for the demo: stop leftovers, launch the simulator, then Nav2.
# WORKSPACE (workspace path) and WARMUP (seconds) can be overridden.

WS="${WORKSPACE:-$HOME/workstation}"
WARMUP="${WARMUP:-25}"

for pattern in component_container rviz2 "gz sim" cmd_vel_relay parameter_bridge; do
  pkill -9 -f "$pattern"
done

source /opt/ros/jazzy/setup.bash
source "$WS/install/setup.bash"
export TURTLEBOT3_MODEL=waffle
export LIBGL_ALWAYS_SOFTWARE=1

ros2 daemon stop
sleep 2
ros2 daemon start

ros2 launch navigation sim.launch.py > /tmp/sim.log 2>&1 &
SIM=$!
trap 'kill $SIM 2>/dev/null; pkill -f "gz sim"' EXIT

echo "Simulator starting (log: /tmp/sim.log), waiting ${WARMUP} s. Leave the robot alone."
sleep "$WARMUP"
ros2 launch navigation nav.launch.py
