# SIH26112 Final Autonomous Warehouse Demo

## Final demo behavior

`SKU -> inventory lookup -> rack approach -> Nav2 -> simulated pickup -> packing zone -> simulated drop -> mission complete`

The physical/modular interface remains independent of navigation. In simulation the mission manager publishes `/amr/module_command` with `PICKUP` and `DROP`; a real bin-lift, conveyor, pallet, scanner, or arm controller can subscribe to the same interface later.

## Windows: start everything

From the repository root in PowerShell:

```powershell
git pull --ff-only origin feature/amr-mission-manager
powershell -ExecutionPolicy Bypass -File .\tools\final_demo.ps1
```

The launcher restarts the ROS container, builds the workspace, launches Gazebo headless, SLAM Toolbox, the lean Nav2 stack, the Nav2 target bridge, and Mission Manager, then verifies the critical ROS nodes/topics.

## Open Gazebo GUI

In another PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\show_gazebo.ps1
```

## Run an autonomous SKU mission

In another PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\run_mission.ps1 SKU004
```

Available demo SKUs are `SKU001` through `SKU010`.

Expected status flow:

```text
TASK_RECEIVED
SKU_RESOLVED
RACK_TARGET_GENERATED
NAVIGATION_REQUESTED
NAVIGATING
ARRIVED_RACK
LOAD_ACQUIRED
PACKING_TARGET_GENERATED
NAVIGATION_REQUESTED
NAVIGATING
ARRIVED_PACKING
MISSION_COMPLETE
```

## ROS interfaces

- `/scan` - LiDAR scan
- `/odom` - wheel/diff-drive odometry
- `/map` - SLAM occupancy map
- `/cmd_vel` - robot velocity command
- `/amr/task_request` - warehouse task input
- `/amr/target_pose` - mission navigation goal
- `/amr/navigation_status` - Nav2 adapter state
- `/amr/mission_status` - warehouse mission state
- `/amr/module_command` - modular payload pickup/drop command

## Demo geometry

The AMR spawns at the Gazebo world/map origin. Rack coordinates in `amr_mission_manager/config/inventory.yaml` are aisle-side approach poses aligned with `warehouse.sdf`, not rack centers. This avoids planning a goal inside collision geometry.

The final delivery target is inside the green packing-zone marker.
