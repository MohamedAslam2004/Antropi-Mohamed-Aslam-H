# Navigation

A TurtleBot3 patrols a simulated loading bay using ROS 2 Jazzy, Nav2 and Gazebo.
The robot localizes on a map built with slam_toolbox and visits a list of
waypoints around the obstacles (slalom posts, cone clusters, a pallet stack,
a barrier and pillars).

## Requirements

- Ubuntu 24.04 with ROS 2 Jazzy
- Gazebo Sim (`gz`) and the TurtleBot3 simulation packages
- Nav2

```bash
sudo apt install ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
                 ros-jazzy-turtlebot3-gazebo
```

Re-mapping the world additionally needs `ros-jazzy-slam-toolbox` and Pillow
(`python3-pil`) for `scripts/clean_map.py`.

## Build

```bash
cd ~/workstation
colcon build --packages-select navigation
source install/setup.bash
```

## Run

Start the simulator and Nav2 with one command:

```bash
src/navigation/scripts/run.sh
```

It stops leftover Gazebo/Nav2 processes, launches the simulator, waits 25 s
(set `WARMUP` to change this) and then starts Nav2 with RViz. Rendering is
forced to software (`LIBGL_ALWAYS_SOFTWARE=1`), so expect a slow start in a VM.

Once RViz shows the map and the robot, run the patrol from a second terminal:

```bash
source /opt/ros/jazzy/setup.bash && source ~/workstation/install/setup.bash
ros2 run navigation patrol.py
```

Options: `--keep-pose` skips setting the initial pose, `--shutdown` stops Nav2
when the patrol finishes.

## Coordinates

The robot spawns at world position (-4, -3), and that point is the origin of
the saved map. Waypoints in `scripts/patrol.py` are written in Gazebo world
coordinates and converted with `map = world + (4, 3)`.

## Re-mapping

1. Drive the robot around with slam_toolbox running and save the map as
   `maps/loading_bay_raw`.
2. Clean it up:
   `python3 scripts/clean_map.py maps/loading_bay_raw.pgm maps/loading_bay.pgm`
3. Check the `origin` in `maps/loading_bay.yaml`, then rebuild the package.

## Layout

| Path | Contents |
| --- | --- |
| `worlds/loading_bay.sdf` | Gazebo world |
| `models/traffic_cone/` | Cone model used in the world |
| `maps/` | Raw and cleaned occupancy maps |
| `config/nav2_params.yaml` | Nav2 parameters |
| `launch/sim.launch.py` | Gazebo, robot state publisher, TurtleBot3 spawn |
| `launch/nav.launch.py` | Nav2 bringup, RViz, velocity relay |
| `scripts/patrol.py` | Waypoint patrol |
| `scripts/cmd_vel_relay.py` | Forwards `/cmd_vel_smoothed` to `/cmd_vel` |
| `scripts/clean_map.py` | SLAM map clean-up |
| `scripts/run.sh` | Clean start for the whole demo |

## Known issue

`collision_monitor` did not publish velocity commands in the VM used for
development, so `cmd_vel_relay.py` forwards the smoothed command straight to
the robot. This bypasses the collision monitor.

## License

MIT, see `LICENSE`.
