# SIH26112 — Modular Autonomous Warehouse Robot (AMR)

A modular Autonomous Mobile Robot platform for Smart India Hackathon 2026, built to demonstrate autonomous warehouse navigation, SKU-to-rack mission planning, obstacle-aware motion, modular payload handling, and rack-to-packing delivery.

## What the prototype demonstrates

```text
Warehouse SKU / Task
        ↓
Inventory Lookup
        ↓
Rack Resolution
        ↓
Mission Manager
        ↓
SLAM + Nav2
        ↓
LiDAR-aware Autonomous Navigation
        ↓
Rack Arrival
        ↓
Modular PICKUP Interface
        ↓
Packing Zone Navigation
        ↓
Modular DROP Interface
        ↓
MISSION_COMPLETE
```

The software interface is deliberately independent from the payload mechanism. In simulation `/amr/module_command` publishes PICKUP and DROP events; the same interface can later drive a real bin lift, pallet module, conveyor, scanner, or robotic attachment.

## Current software stack

- **ROS 2 Jazzy** — middleware and robot software
- **Gazebo Sim** — warehouse and AMR simulation
- **SLAM Toolbox** — online mapping / localization for the SIH demo
- **Nav2** — global planning, local control and obstacle-aware navigation
- **2D LiDAR** — `/scan` obstacle observations
- **Differential drive odometry** — `/odom`
- **Mission Manager** — SKU → rack → pickup → packing → drop state machine
- **Nav2 recovery adapter** — bounded retry with local/global costmap clearing
- **RViz judge view** — map, LiDAR, robot, costmap and planned path

## Demo warehouse

The Gazebo world contains six rack destinations, a packing zone, walls and a visible centre-aisle obstacle crate. Inventory approach poses are placed in aisle-side free space rather than at rack collision centres.

| Demo SKU | Destination |
|---|---|
| SKU001 / SKU007 | RACK_A |
| SKU002 | RACK_B |
| SKU003 / SKU008 | RACK_C |
| SKU004 | RACK_D |
| SKU005 / SKU009 | RACK_E |
| SKU006 / SKU010 | RACK_F |

## Repository layout

```text
AWR-Bot-/
├── docs/                     # architecture, final demo and validation docs
├── ros2_ws/
│   └── src/
│       ├── amr_description/  # URDF/Xacro robot description
│       ├── amr_simulation/   # Gazebo launch/world/bridge
│       ├── amr_navigation/   # SLAM, Nav2, RViz and target bridge
│       ├── amr_mission_manager/
│       └── amr_bringup/      # full demo orchestration
├── tools/                    # Windows one-command demo/test helpers
├── cad/
├── hardware/
├── firmware/
├── media/
└── legacy/yashraj-handover/  # original handover preserved
```

## One-command startup on Windows

From the repository root in PowerShell:

```powershell
git pull --ff-only origin feature/amr-mission-manager
powershell -ExecutionPolicy Bypass -File .\tools\final_demo.ps1
```

The launcher starts/restarts Docker Desktop when required, builds the ROS workspace, launches Gazebo headless, SLAM Toolbox, the lean Nav2 stack, the target bridge and Mission Manager, then checks critical ROS nodes/topics.

### Open Gazebo

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\show_gazebo.ps1
```

### Open RViz judge view

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\show_rviz.ps1
```

### Run one autonomous mission

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\run_mission.ps1 SKU004
```

### Judge presentation mode

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\judge_demo.ps1 SKU004
```

For Gazebo + RViz:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\judge_demo.ps1 SKU006 -WithRViz
```

## Reliability features

The release-candidate Nav2 adapter does not immediately kill a warehouse mission on the first navigation abort. It can clear both local and global Nav2 costmaps, wait briefly, refresh the goal timestamp, and retry a bounded number of times. Mission status exposes this as `RECOVERY_RETRY`; an unrecoverable mission still exits cleanly as `MISSION_FAILED` rather than looping forever.

Nav2 parameters are tuned for the demo AMR with a larger local costmap, more progress time, conservative speed, collision detection, obstacle layers and rack-approach tolerance.

## Final validation

The software is considered final only when all six rack destinations pass on the actual demo machine.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\final_validation.ps1
```

This validates SKU001–SKU006 sequentially and stores evidence in `media/evidence/`.

Dedicated obstacle route:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\obstacle_demo.ps1
```

System evidence snapshot:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\capture_evidence.ps1
```

See:

- [`docs/FINAL_DEMO.md`](docs/FINAL_DEMO.md)
- [`docs/FINAL_TEST_CHECKLIST.md`](docs/FINAL_TEST_CHECKLIST.md)
- [`docs/DEMO_RECORDING_SHOTLIST.md`](docs/DEMO_RECORDING_SHOTLIST.md)

## Demonstrated milestone

A complete **SKU004 → RACK_D → simulated pickup → PACKING_ZONE → simulated drop → MISSION_COMPLETE** run has already executed end-to-end. The current branch is a release candidate containing additional multi-rack recovery and presentation tooling; the final six-rack validation is intentionally the release gate before merge/freeze.

## Team

| Track | Owner | Responsibility |
|---|---|---|
| System Architecture / CAD / Integration | Tarun | AMR architecture, modularity, Fusion CAD, final integration |
| ROS 2 / Gazebo / Navigation | Yashraj | simulation and autonomy implementation |
| Physical Prototype / Hardware | Aaditya | chassis, motors, electronics, sensors and attachment hardware |

**Problem Statement:** SIH26112  
**Project:** Modular Autonomous Mobile Robot Platform for Smart Warehouse Automation
