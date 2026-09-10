# AMR Simulation

Clean replacement for the legacy NavBot simulation. The original Yashraj handover remains untouched under `legacy/yashraj-handover/`.

## Fixes over the handover

- one canonical four-wheel robot model,
- wheel geometry and DiffDrive use the same radius,
- all four drive-wheel joints are controlled,
- explicit ROS 2 ↔ Gazebo bridge,
- `/cmd_vel`, `/odom`, `/tf`, `/scan`, `/joint_states`, `/clock`,
- warehouse world with rack rows,
- repeatable movement smoke test.

## Run

```bash
source /opt/ros/jazzy/setup.bash
cd ~/AWR-Bot-/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch amr_simulation sim.launch.py
```

Second terminal:

```bash
source ~/AWR-Bot-/ros2_ws/install/setup.bash
ros2 run amr_simulation motion_smoke_test.py
```

Verify:

```bash
ros2 topic echo /odom --once
ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo odom base_footprint
```
