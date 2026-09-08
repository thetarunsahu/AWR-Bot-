# AMR Bringup

One-command simulation + SLAM + Nav2 bringup:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/AWR-Bot-/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch amr_bringup sim_slam_nav.launch.py
```

First validate motion separately:

```bash
ros2 run amr_simulation motion_smoke_test.py
```
