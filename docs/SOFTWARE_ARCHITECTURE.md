# Software Architecture — SIH26112

```text
Warehouse Task / Order
        |
        v
Mission Manager
SKU -> Rack -> Pose
        |
 /amr/target_pose
        |
        v
Nav2 Target Adapter
Pose -> NavigateToPose
        |
        v
Nav2
Planner + Controller + Costmaps
        |
     /cmd_vel
        |
        v
ros_gz_bridge
        |
        v
Gazebo DiffDrive -> 4 wheels
        |
  /odom + /tf + /scan
        |
        v
slam_toolbox -> /map -> Nav2
```

## Canonical TF

```text
map
└── odom
    └── base_footprint
        └── base_link
            └── lidar_link
```

- `map -> odom`: SLAM / localization
- `odom -> base_footprint`: drivetrain odometry
- fixed robot links: `robot_state_publisher`

## Packages

- `amr_description`: canonical geometry, joints, LiDAR and DiffDrive definition
- `amr_simulation`: Gazebo warehouse, bridge and motion smoke test
- `amr_navigation`: SLAM, Nav2 and target-pose adapter
- `amr_bringup`: top-level launcher
- `amr_mission_manager`: SKU / rack mission logic developed separately

`legacy/yashraj-handover/` remains preserved and is not the canonical runtime stack.
