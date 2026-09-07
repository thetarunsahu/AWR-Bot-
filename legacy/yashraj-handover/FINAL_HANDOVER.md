# NAVBOT PROJECT - FINAL HANDOVER

## Project
NavBot is a four-wheel mobile robot simulation developed using ROS 2 Jazzy and Gazebo Sim.

## Completed Work
- ROS 2 Jazzy Docker environment configured
- navbot_description ROS 2 package created
- Four-wheel NavBot URDF created
- URDF validated successfully using check_urdf
- Four wheel joints created:
  - front_left_joint
  - front_right_joint
  - rear_left_joint
  - rear_right_joint
- Robot converted from URDF to Gazebo SDF
- NavBot successfully spawned in Gazebo
- Gazebo GUI successfully connected
- Differential-drive configuration added to the robot SDF
- cmd_vel topic configured
- odom topic configured
- Obstacle world asset created
- Project documentation and handover files created

## Main Files
src/navbot_description/urdf/navbot.urdf
src/navbot_description/launch/display_navbot.launch.py
src/navbot_description/CMakeLists.txt
src/navbot_description/package.xml
navbot_final.sdf
navbot_movable.sdf
obstacle_world.sdf
README.md
HANDOVER.md

## Verification
The URDF was successfully parsed with four wheel links connected to base_link.

The Gazebo model was successfully spawned and wheel joints were verified in the running simulation.

## Pending Integration
- Final motion controller tuning
- Nav2 integration
- LiDAR integration
- SLAM
- Autonomous obstacle avoidance
