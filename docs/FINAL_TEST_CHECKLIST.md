# SIH26112 Final Test Checklist

This checklist is the release gate for the software/simulation prototype. Code may be prepared before these tests, but the integration branch must not be frozen/merged until every **P0** item passes on Tarun's Windows + Docker + ROS 2 machine.

## P0 — Must pass before final merge

- [ ] `final_demo.ps1` reaches `FINAL STACK READY` from a clean restart.
- [ ] `/scan`, `/odom`, `/map`, `/cmd_vel`, `/amr/task_request`, `/amr/mission_status` are present.
- [ ] Nav2 action `/navigate_to_pose` is available.
- [ ] Costmap clear recovery services are available.
- [ ] SKU001 completes RACK_A pickup + PACKING_ZONE delivery.
- [ ] SKU002 completes RACK_B pickup + PACKING_ZONE delivery.
- [ ] SKU003 completes RACK_C pickup + PACKING_ZONE delivery.
- [ ] SKU004 completes RACK_D pickup + PACKING_ZONE delivery.
- [ ] SKU005 completes RACK_E pickup + PACKING_ZONE delivery.
- [ ] SKU006 completes RACK_F pickup + PACKING_ZONE delivery.
- [ ] Existing centre-aisle crate is detected by LiDAR/costmap and the AMR avoids it during the obstacle demo.
- [ ] Recovery path is bounded: an abort may trigger `RECOVERY_RETRY`, but an unrecoverable mission ends cleanly with `MISSION_FAILED` instead of hanging.

Run the complete P0 sequence with:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\final_validation.ps1
```

A pass is recorded in `media/evidence/final-validation-*.txt`.

## P1 — Judge presentation quality

- [ ] Gazebo opens through `show_gazebo.ps1` and the full warehouse is visible.
- [ ] RViz opens through `show_rviz.ps1` with map, LiDAR, AMR model, costmap and Nav2 path visible.
- [ ] Mission terminal text remains readable during recording.
- [ ] At least one complete mission video is captured from command -> rack -> pickup -> packing -> completion.
- [ ] At least one obstacle-avoidance clip is captured.
- [ ] Screenshots captured: warehouse overview, RViz map/LiDAR/path, `MISSION_COMPLETE`, modular PICKUP/DROP state.
- [ ] `capture_evidence.ps1` produces a system evidence text file.

## P2 — Freeze / merge gate

Only after P0 passes:

1. Pull the latest `feature/amr-mission-manager` branch.
2. Store final evidence under `media/evidence/`.
3. Do not add new features; only critical fixes are allowed.
4. Merge the release candidate into the integration/main target branch.
5. Tag/record the exact final commit SHA in the SIH submission notes.

## Expected mission state flow

```text
TASK_RECEIVED
SKU_RESOLVED
RACK_TARGET_GENERATED
NAVIGATION_REQUESTED
NAVIGATING
[RECOVERY_RETRY if required]
ARRIVED_RACK
LOAD_ACQUIRED
PACKING_TARGET_GENERATED
NAVIGATION_REQUESTED
NAVIGATING
[RECOVERY_RETRY if required]
ARRIVED_PACKING
MISSION_COMPLETE
```
