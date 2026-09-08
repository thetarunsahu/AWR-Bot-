# Software Runbook — SIH26112 AMR

## Target stack

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic / modern Gazebo
- ros_gz
- slam_toolbox
- Nav2

Install missing packages:

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-ros-gz \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-tf2-tools \
  ros-jazzy-slam-toolbox \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup
```

## Build

```bash
cd ~/AWR-Bot-
git checkout simulation
git pull origin simulation
source /opt/ros/jazzy/setup.bash
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## Phase 1 — base motion

Terminal 1:

```bash
ros2 launch amr_simulation sim.launch.py
```

Terminal 2:

```bash
source ~/AWR-Bot-/ros2_ws/install/setup.bash
ros2 run amr_simulation motion_smoke_test.py
```

Required checks:

```bash
ros2 topic echo /odom --once
ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo odom base_footprint
```

Do not continue to navigation until movement, odometry, scan and TF pass.

## Phase 2 — SLAM

```bash
ros2 launch amr_navigation slam.launch.py
```

Expected TF: `map -> odom -> base_footprint -> base_link -> lidar_link`.

Save the map:

```bash
ros2 run nav2_map_server map_saver_cli -f src/amr_navigation/maps/warehouse
```

## Phase 3 — Nav2

```bash
ros2 launch amr_navigation navigation.launch.py
```

## Phase 4 — mission integration

The Mission Manager publishes `/amr/target_pose`. The adapter turns it into a Nav2 `NavigateToPose` goal.

```text
SKU -> rack -> coordinates -> /amr/target_pose -> Nav2 -> /cmd_vel -> AMR
```

## Software-complete checklist

- [ ] `/cmd_vel` moves the robot reliably
- [ ] odometry is valid
- [ ] TF tree is connected
- [ ] LiDAR is visible in ROS
- [ ] SLAM creates a warehouse map
- [ ] Nav2 reaches a goal
- [ ] obstacle avoidance works
- [ ] Mission Manager resolves SKU to rack pose
- [ ] `/amr/target_pose` triggers Nav2
- [ ] failure/status topics are visible

Code committed is not the same as runtime verification. Capture screenshots/logs for every runtime check.
