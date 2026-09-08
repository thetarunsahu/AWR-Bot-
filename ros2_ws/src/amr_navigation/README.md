# AMR Navigation

```text
LiDAR /scan + /odom + TF
          |
          v
    slam_toolbox
          |
     /map + map->odom
          |
          v
        Nav2
          ^
          |
/amr/target_pose
          ^
          |
 Mission Manager
```

The Mission Manager publishes `geometry_msgs/PoseStamped` to `/amr/target_pose`. `target_pose_nav2_bridge.py` converts it into a Nav2 `NavigateToPose` action goal.

## Run

```bash
ros2 launch amr_navigation slam.launch.py
ros2 launch amr_navigation navigation.launch.py
```

Save a map:

```bash
ros2 run nav2_map_server map_saver_cli -f src/amr_navigation/maps/warehouse
```

Core TF: `map -> odom -> base_footprint -> base_link -> lidar_link`.
