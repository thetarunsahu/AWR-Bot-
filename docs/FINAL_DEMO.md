# SIH26112 Final Autonomous Warehouse Demo

## Final demo behavior

```text
SKU
  -> inventory lookup
  -> rack approach target
  -> Nav2 autonomous navigation
  -> modular PICKUP event
  -> packing-zone target
  -> Nav2 autonomous navigation
  -> modular DROP event
  -> MISSION_COMPLETE
```

The physical payload interface remains independent of navigation. In simulation Mission Manager publishes `/amr/module_command` with PICKUP and DROP events; a real bin lift, conveyor, pallet, scanner, or arm controller can subscribe to the same interface later.

## Reliability layer

The final Nav2 target bridge contains bounded recovery instead of immediately failing on the first navigation abort:

1. detect Nav2 abort,
2. publish `RECOVERY_RETRY` through Mission Manager,
3. clear global and local Nav2 costmaps,
4. refresh the goal timestamp,
5. retry the same destination,
6. stop after the configured retry limit and publish `MISSION_FAILED` if recovery is impossible.

This avoids an unbounded retry loop while making repeated rack-to-rack missions more tolerant of stale costmap state.

## Windows: start everything

From the repository root in PowerShell:

```powershell
git pull --ff-only origin feature/amr-mission-manager
powershell -ExecutionPolicy Bypass -File .\tools\final_demo.ps1
```

The launcher:

- starts Docker Desktop if necessary,
- restarts the stable ROS container,
- builds the ROS 2 workspace,
- launches Gazebo headless,
- starts SLAM Toolbox,
- starts the lean Nav2 stack,
- starts the target bridge and Mission Manager,
- checks critical nodes/topics,
- verifies Nav2 costmap recovery services.

## Visualization

Gazebo warehouse view:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\show_gazebo.ps1
```

RViz judge view:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\show_rviz.ps1
```

The custom RViz preset is designed to show the evidence judges care about: SLAM map, LiDAR, AMR model, global costmap and Nav2 path.

## Run an autonomous SKU mission

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
[RECOVERY_RETRY if recovery is needed]
ARRIVED_RACK
LOAD_ACQUIRED
PACKING_TARGET_GENERATED
NAVIGATION_REQUESTED
NAVIGATING
[RECOVERY_RETRY if recovery is needed]
ARRIVED_PACKING
MISSION_COMPLETE
```

## One-command judge mode

Gazebo + mission:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\judge_demo.ps1 SKU004
```

Gazebo + RViz + mission:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\judge_demo.ps1 SKU006 -WithRViz
```

## Dedicated obstacle demo

The Gazebo warehouse contains a visible static obstacle crate in the centre aisle. The Nav2 local/global obstacle layers consume `/scan`, mark the crate in costmaps and plan/control around occupied space.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\obstacle_demo.ps1
```

This resets the AMR to a repeatable start, opens Gazebo and runs SKU006 toward RACK_F while recording a text evidence log.

## Final multi-rack validation

Do not freeze/merge the release candidate until all six rack destinations pass on the final machine:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\final_validation.ps1
```

Validation sequence covers SKU001–SKU006 and stores a timestamped report under `media/evidence/`.

## Evidence capture

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\capture_evidence.ps1
```

This stores a ROS graph / map / odom / LiDAR / Nav2 log snapshot under `media/evidence/`.

## ROS interfaces

- `/scan` — LiDAR scan
- `/odom` — differential-drive odometry
- `/map` — SLAM occupancy map
- `/cmd_vel` — Nav2 velocity command
- `/amr/task_request` — warehouse task input
- `/amr/target_pose` — current mission navigation goal
- `/amr/navigation_status` — Nav2 adapter state
- `/amr/mission_status` — warehouse mission state
- `/amr/module_command` — modular PICKUP / DROP command

## Demo geometry

The AMR spawns at the Gazebo world/map origin. Rack coordinates in `amr_mission_manager/config/inventory.yaml` are aisle-side approach poses aligned with `warehouse.sdf`, not rack centres. The final delivery target is inside the green packing-zone marker.

## Release state

A complete SKU004 -> RACK_D -> pickup -> PACKING_ZONE -> drop mission has already executed successfully end-to-end. The current branch includes the reliability and presentation changes required for the final six-rack release-candidate validation.

See also:

- `docs/FINAL_TEST_CHECKLIST.md`
- `docs/DEMO_RECORDING_SHOTLIST.md`
