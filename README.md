# SIH26112 — Modular Autonomous Warehouse Robot (AMR)

> A modular Autonomous Mobile Robot platform for smart warehouse automation, developed for Smart India Hackathon 2026.

## Project Goal

Build a **universal autonomous mobile robot base** that can navigate an indoor warehouse safely and accept interchangeable task modules. The first target module is a **bin / pallet handling attachment**; future modules can include inventory scanning, conveyor transfer, inspection, and robotic picking.

## Current Development Tracks

| Track | Owner | Current Focus |
|---|---|---|
| System Architecture & Fusion CAD | Tarun | AMR specifications, modular interface, CAD architecture, integration |
| ROS 2 & Gazebo Simulation | Yashraj | robot model, motion, LiDAR, bridge, SLAM/Nav2 |
| Physical Prototype & Hardware | Aaditya | chassis, motors, electronics, sensors, wiring, attachment hardware |

See [`docs/TEAM_RESPONSIBILITIES.md`](docs/TEAM_RESPONSIBILITIES.md) and the individual files under [`team/`](team/) for detailed work ownership.

## System Overview

```text
Warehouse Task / Mission
          |
          v
   Mission Manager
          |
          v
+---------------------------+
|        ROS 2 Stack        |
| Localization / SLAM       |
| Nav2 + Path Planning      |
| Obstacle Avoidance        |
+-------------+-------------+
              |
     Sensor Fusion / TF
              |
   +----------+----------+
   | LiDAR | IMU | Encoder|
   +----------+----------+
              |
              v
      Motor Controller
              |
              v
      4-Wheel AMR Base
              |
              v
   Universal Module Interface
       /        |        \
 Pallet/    Scanner    Conveyor
 Bin Lift     Module      Module
```

## Repository Layout

```text
AWR-Bot-/
├── README.md
├── CONTRIBUTING.md
├── docs/                     # architecture, roadmap, status, integration
├── team/                     # member-wise responsibilities
├── legacy/
│   └── yashraj-handover/     # original simulation handover preserved unchanged
├── ros2_ws/                  # clean ROS 2 workspace (development target)
├── simulation/               # Gazebo worlds / models / test assets
├── cad/                      # Fusion design exports, meshes, manufacturing notes
├── hardware/                 # wiring, BOM, electronics, mechanical notes
├── firmware/                 # microcontroller / motor-controller code
└── media/                    # renders, screenshots, demo media
```

## Current Status

Yashraj's initial ROS 2 / Gazebo handover has been preserved under `legacy/yashraj-handover/`. It establishes the simulation foundation, including a basic robot model, Gazebo world, wheel joints, `cmd_vel` controller, odometry configuration, and LiDAR foundation.

The next priority is **not** to jump directly to SLAM/Nav2. First we must make the base motion chain reliable:

```text
ROS 2 /cmd_vel
      -> ROS-Gazebo bridge
      -> Gazebo DiffDrive
      -> wheel joints
      -> robot motion
```

After motion is verified:

1. Bridge LiDAR data into ROS 2.
2. Validate TF and odometry.
3. Add obstacle avoidance.
4. Add SLAM.
5. Integrate Nav2.
6. Replace the placeholder robot geometry with the final CAD-derived AMR model.
7. Integrate the physical prototype.

Detailed status: [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md)

## Engineering Principle

The physical prototype, Gazebo simulation, and Fusion CAD are **three representations of the same robot**, not separate projects. Dimensions, frame names, sensor placement, wheel geometry, and modular-interface definitions should stay synchronized.

## SIH Demo Target

**Scaled functional prototype + engineering CAD + simulation validation** demonstrating:

- autonomous warehouse navigation,
- obstacle detection and avoidance,
- modular payload interface,
- one functional bin/pallet handling module,
- Fusion-based design and optimization,
- a clear path from prototype to industrial AMR.

---

**Team:** Tarun · Yashraj · Aaditya  
**Problem Statement:** SIH26112
