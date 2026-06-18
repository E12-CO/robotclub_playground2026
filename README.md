# robotclub_playground2026

```robotclub_playground2026``` is a advanced mobile robot playground developed as the learning and experimental platform as well as a capability demonstration of the Robot Club Engineering KMITL. Most, if not all of the examples here are based of the work done back in the ABU 2025 package.

## Learning outcome
- Understand the general concept of ROS2 and **can distinguish** between **core concept of robotics** and **core concept of ROS**
- Familiarize with using ROS2 command line, built-in tools, simulation and launch system
- Can utilize common ROS2 packages and libraries, as well as in-house/self developed package to fullfil the goal of making autonomous robots.

## Dependencies

- ROS2 Humble on Ubuntu 22.04 or tier 3 OSes
- RViz2 and RQT graph
- Gazebo classic
- Cartographer ROS (ros2)
- iRob_bot_ros2 package set

## Build process

- Create a ROS workspace, or use the existing one
- Clone this repository
- run ```colcon build --symlink-install --packages-select robotclub_playground2026```
- source the workspace

## Launch demos 

Use the following command to launch the mapping + navigation sim
```
ros2 launch robotclub_playground2026 launch_sim_mapping.launch.py
```

To save the map, use the following command
```
ros2 service call /r1/write_state cartographer_ros_msgs/srv/WriteState "filename: playground2026_map.pbstream"
```
The map should appear in the same working directory as the command was called such as home folder or ROS2 workspace  

Use the following command to launch the localization + navigation sim
```
ros2 launch robotclub_playground2026 launch_sim_localize.launch.py
```

## TODO
- Fix the localization not realign with the map
- Add the initial pose capability
- Documents