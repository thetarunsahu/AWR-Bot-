# Yashraj — ROS 2, Gazebo & Autonomous Navigation

## Role

Primary owner of the **software simulation and autonomy stack**.

The original handover is preserved under `legacy/yashraj-handover/` and should remain unchanged as a baseline reference.

## Work Already Present in Handover

- ROS 2 Jazzy workflow,
- Gazebo Sim world,
- basic NavBot URDF,
- wheel joints,
- DiffDrive configuration foundation,
- `/cmd_vel` publishing node,
- odometry topic configuration,
- LiDAR sensor foundation,
- obstacle world,
- startup / handover documentation.

## Immediate Work Queue

### Y1 — Canonical Robot Model
Remove the current split between:

- four-wheel URDF model,
- two-wheel robot embedded in the world SDF.

Use one canonical four-wheel model.

### Y2 — Geometry Consistency
Synchronize wheel geometry and DiffDrive values with the frozen project dimensions.

Current handover contains a known wheel-radius mismatch and must not be treated as final geometry.

### Y3 — ROS <-> Gazebo Bridge
Configure and verify bridging for at least:

- velocity command,
- odometry,
- LiDAR,
- clock as required by the stack.

### Y4 — Base Motion Verification
Pass repeatable tests for:

- forward,
- reverse,
- rotate / turn left,
- rotate / turn right,
- stop,
- command timeout behaviour.

### Y5 — TF + Odometry
Create a navigation-compatible frame tree and validate odometry before SLAM.

Recommended target:

```text
map -> odom -> base_footprint -> base_link -> sensors / wheels
```

### Y6 — LiDAR
Expose the Gazebo LiDAR to ROS 2, verify scan data and visualize it.

### Y7 — Autonomy
Only after Y1–Y6:

1. obstacle stop / avoidance,
2. SLAM Toolbox,
3. saved warehouse map,
4. Nav2,
5. goal navigation,
6. dynamic obstacle tests,
7. warehouse mission / docking logic.

## Inputs Needed From Team

### From Tarun
- final wheel geometry,
- chassis geometry,
- sensor poses,
- CAD meshes where appropriate,
- module mount geometry.

### From Aaditya
- physical drive limitations,
- encoder information,
- controller/MCU interface,
- physical sensor update rates and placement.

## Deliverables

- clean ROS 2 package layout,
- canonical Xacro/URDF,
- Gazebo launch flow,
- bridge configuration,
- valid `/cmd_vel`, `/odom`, `/scan`, `/tf`,
- SLAM map,
- Nav2 configuration,
- autonomous warehouse simulation,
- documentation of commands and repeatable tests.
