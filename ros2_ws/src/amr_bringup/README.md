# AMR Bringup

This package starts the complete SIH26112 warehouse autonomy chain:

```text
Gazebo + LiDAR + odometry
        -> SLAM Toolbox
        -> Nav2
        -> /amr/target_pose bridge
        -> Mission Manager
        -> SKU -> rack approach pose
```

## Full autonomous demo

```bash
source /opt/ros/jazzy/setup.bash
cd /workspace/AWR-Bot-/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch amr_bringup full_demo.launch.py headless:=true rviz:=false
```

The launch waits for Gazebo, then starts SLAM, Nav2, and the Mission Manager.

In another sourced Docker terminal, send a warehouse task:

```bash
ros2 run amr_mission_manager send_demo_task SKU004
```

Watch end-to-end mission state:

```bash
ros2 topic echo /amr/mission_status
```

Expected lifecycle:

```text
TASK_RECEIVED
SKU_RESOLVED
TARGET_GENERATED
NAVIGATION_REQUESTED
NAVIGATING
MISSION_COMPLETE
```

Available demo SKUs are `SKU001` through `SKU010`. Their rack approach poses are aligned to the current `warehouse.sdf` and assume the AMR spawn pose in `amr_simulation/launch/sim.launch.py` remains `(-10.0, -7.5, yaw=0)`.

## Visualization

Keep the full demo running headless and attach Gazebo GUI from a second Docker shell after XLaunch / VcXsrv is active:

```bash
source /opt/ros/jazzy/setup.bash
export DISPLAY=host.docker.internal:0.0
export QT_X11_NO_MITSHM=1
export LIBGL_ALWAYS_SOFTWARE=1
gz sim -g
```

RViz can also be started with the stack when X display forwarding is already working:

```bash
ros2 launch amr_bringup full_demo.launch.py headless:=true rviz:=true
```

## Lower-level checks

Motion test:

```bash
ros2 run amr_simulation motion_smoke_test.py
```

Sensors / localization inputs:

```bash
ros2 topic echo /odom --once
ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo odom base_footprint
```
