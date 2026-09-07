# NavBot Handover

## Working
- ROS 2 Jazzy in Docker
- Gazebo Sim 8
- Custom NavBot URDF
- URDF successfully converts to SDF
- Gazebo server starts headless
- NavBot successfully spawns
- Gazebo GUI attaches to the running server
- Custom obstacle world file created

## Start commands

Terminal 1:
gz sim -s

Terminal 2:
gz sim -g

Build:
cd /root/navbot_ws
colcon build
source install/setup.bash

Spawn robot:
gz sdf -p src/navbot_description/urdf/navbot.urdf > navbot_final.sdf

gz service -s /world/default/create \
--reqtype gz.msgs.EntityFactory \
--reptype gz.msgs.Boolean \
--timeout 5000 \
--req 'sdf_filename: "/root/navbot_ws/navbot_final.sdf", name: "navbot_final", pose: {position: {x: 2, y: 0, z: 0.5}}'

## Next work
1. Final wheel physics
2. Differential drive plugin
3. cmd_vel control
4. LiDAR
5. Obstacle avoidance
6. SLAM / Nav2
