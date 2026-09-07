# Simulation Workspace

Gazebo worlds, models, scenario files and simulation-specific test assets go here.

The active robot description should ultimately come from the clean ROS 2 workspace, not from a duplicate robot model embedded inside a world file.

Suggested layout:

```text
simulation/
├── worlds/
├── models/
├── configs/
└── tests/
```

Warehouse scenarios should gradually progress from static obstacles to shelves, aisles, pickup/drop zones and dynamic obstacles.
