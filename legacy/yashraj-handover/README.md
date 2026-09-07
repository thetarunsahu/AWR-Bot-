# NavBot SIH Foundation

Current implemented simulation layer:

- ROS 2 Jazzy package
- Gazebo Sim world
- Differential-drive NavBot
- cmd_vel interface
- odometry interface
- LiDAR sensor foundation
- obstacle environment
- autonomous controller foundation

Next layer:

- ROS-Gazebo bridge
- obstacle avoidance logic
- SLAM
- Nav2
- global path planning
- autonomous mission logic
- hardware integration


## Current Project Status

### Working

- Docker environment
- ROS 2 Jazzy
- Gazebo Sim
- NavBot model loads successfully
- Gazebo GUI rendering
- Ground and obstacle environment
- LiDAR sensor foundation

### Current Blocker

The robot successfully appears in the Gazebo simulation, but actual physical movement has not yet been confirmed.

The movement chain currently needs debugging:

cmd_vel → DiffDrive plugin → wheel joints → physics → robot movement

### Immediate Priority

Fix and verify robot movement before proceeding with navigation features.

## Software Flow

Environment / Obstacles
        ↓
      LiDAR
        ↓
   ROS 2 Logic
        ↓
     cmd_vel
        ↓
 Differential Drive
        ↓
  Robot Movement

## Recommended Development Order

1. Fix robot movement
2. Verify ROS-Gazebo communication
3. Access and process LiDAR data
4. Implement obstacle avoidance
5. Implement SLAM
6. Integrate Nav2
7. Add path planning
8. Build autonomous mission logic
9. Integrate with physical hardware
