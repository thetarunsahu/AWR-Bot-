# Project Status

Last structured baseline: initial Yashraj handover + repository architecture setup.

## Status Legend

- ✅ implemented / verified
- 🟡 partially implemented / needs verification
- ❌ not implemented
- ⏸ waiting on design decision

## Software / Simulation

| Item | Status | Notes |
|---|---:|---|
| ROS 2 Jazzy environment | ✅ | present in handover workflow |
| Gazebo Sim environment | ✅ | world and robot spawn foundation exists |
| Basic robot URDF | ✅ | four-wheel placeholder model exists |
| Gazebo obstacle world | ✅ | basic world with static obstacles exists |
| Wheel joints | ✅ | four-wheel joints in URDF; separate two-wheel SDF also exists |
| Gazebo DiffDrive | 🟡 | configured but motion chain not yet confirmed |
| ROS `/cmd_vel` publisher | ✅ | simple constant forward velocity node exists |
| ROS-Gazebo bridge | ❌ | not present in handover package |
| Reliable robot movement | ❌ | must be verified before navigation work |
| Odometry in ROS 2 | 🟡 | Gazebo odom configuration exists; ROS-side bridge/validation pending |
| LiDAR in Gazebo | 🟡 | sensor foundation exists in the world SDF |
| LiDAR in ROS 2 | ❌ | bridge and LaserScan validation pending |
| TF tree | ❌ | canonical navigation TF tree not yet defined |
| Obstacle avoidance | ❌ | pending |
| SLAM | ❌ | pending |
| Nav2 | ❌ | pending |
| Warehouse mission logic | ❌ | pending |

## Current Simulation Issues to Resolve

1. **Two robot definitions exist:**
   - four-wheel URDF,
   - two-wheel robot embedded in `navbot_sih_world.sdf`.

   These must be consolidated into one canonical robot model.

2. **Wheel radius mismatch:**
   - wheel geometry in URDF = `0.15 m`,
   - URDF DiffDrive plugin = `0.12 m`.

   The value must be made consistent after the final dimensions are frozen.

3. **ROS-Gazebo bridge missing:**
   ROS 2 `/cmd_vel` and Gazebo transport are not automatically the same transport system. The project needs an explicit `ros_gz_bridge` configuration for the required interfaces.

4. **Navigation should not be started before motion/TF/odom are stable.**

## CAD / Mechanical

| Item | Status | Notes |
|---|---:|---|
| Final AMR dimensions | ⏸ | must be frozen |
| Fusion base chassis | ❌ | pending |
| Motor mounts | ❌ | pending |
| Sensor mounts | ❌ | pending |
| Electronics enclosure | ❌ | pending |
| Universal module interface | ❌ | pending |
| Bin/pallet module concept | 🟡 | selected as primary direction; mechanism not frozen |
| Structural simulation | ❌ | pending |
| topology / generative optimization | ❌ | pending |
| CAD mesh export to URDF | ❌ | pending |

## Physical Prototype

| Item | Status | Notes |
|---|---:|---|
| Base robot/chassis available | 🟡 | existing prototype visible; full inventory pending |
| Chassis measurements | ❌ | document exact dimensions |
| Motor specifications | ❌ | inventory required |
| Motor driver specification | ❌ | inventory required |
| Battery / power specification | ❌ | inventory required |
| Encoders | ⏸ | confirm existing hardware |
| LiDAR mounting | ❌ | pending |
| IMU integration | ❌ | pending |
| Emergency stop | ❌ | pending |
| Clean electronics mounting | ❌ | pending |
| Physical modular attachment | ❌ | pending |
| ROS-to-hardware movement | ❌ | pending |

## Immediate Team Priority

```text
1. Freeze dimensions + hardware inventory
2. Fix Gazebo movement chain
3. Create canonical robot description
4. Validate odometry + TF
5. Bridge and validate LiDAR
6. Begin Fusion chassis + module interface
7. Add SLAM
8. Add Nav2
9. Build attachment prototype
10. Integrate simulation + CAD + physical robot
```

## Definition of the Next Milestone

**Milestone M1 — Base AMR Motion Ready**

M1 is complete only when:

- the canonical four-wheel robot model is used,
- ROS 2 publishes velocity commands,
- Gazebo receives them through a bridge,
- the robot moves forward, backward and turns,
- `/odom` is visible and sensible,
- TF is coherent,
- wheel dimensions match the frozen design values.
