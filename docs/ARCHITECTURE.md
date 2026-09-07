# System Architecture — SIH26112 Modular AMR

## 1. Architecture Goal

The project is designed as a **single modular AMR platform** with three synchronized representations:

1. **Fusion CAD** — mechanical truth: dimensions, mounts, payload interface, manufacturability.
2. **ROS 2 + Gazebo** — autonomy truth: frames, sensors, motion, localization, navigation, missions.
3. **Physical Prototype** — real-world validation: motors, electronics, sensors, control and attachment.

A change to wheel radius, wheelbase, LiDAR position, chassis size, or module interface must be reflected across all three.

---

## 2. Top-Level Functional Architecture

```text
                    WAREHOUSE / OPERATOR
                           |
                  Task / Goal / Mission
                           |
                           v
+-------------------------------------------------------------+
|                     MISSION LAYER                           |
| Task Manager | Docking Logic | Module Action | Safety State |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
|                    AUTONOMY LAYER                           |
| Nav2 | Global Planner | Local Planner | Recovery Behaviours |
+----------------------------+--------------------------------+
                             |
                +------------+------------+
                |                         |
                v                         v
+----------------------------+  +-----------------------------+
| LOCALIZATION / PERCEPTION  |  |       MOTION CONTROL        |
| SLAM / Map / AMCL          |  | /cmd_vel -> drive control   |
| LiDAR / IMU / Encoders     |  | odometry / wheel feedback   |
+-------------+--------------+  +--------------+--------------+
              |                                |
              +---------------+----------------+
                              v
+-------------------------------------------------------------+
|                    AMR HARDWARE BASE                        |
| 4-wheel chassis | motors | drivers | battery | controller   |
+----------------------------+--------------------------------+
                             |
                             v
+-------------------------------------------------------------+
|              UNIVERSAL MODULAR INTERFACE                    |
| mechanical lock | power | data | module ID | safety interlock|
+---------------+----------------+----------------------------+
                |                |                 |
                v                v                 v
       Bin/Pallet Lift    Inventory Scanner   Conveyor Module
          (Phase 1)           (Future)           (Future)
```

---

## 3. Mechanical Architecture

### AMR Base

Target architecture:

```text
Top Module / Payload
        |
Universal Mounting Plate
        |
Upper Electronics Layer
        |
Structural Chassis
  |             |
Left Wheels   Right Wheels
        |
Battery / Low-CG Components
```

Design principles:

- low center of gravity,
- symmetric drive geometry,
- protected electronics,
- serviceable motor mounts,
- clear sensor field of view,
- standard top-module footprint,
- quick module replacement,
- separate prototype and industrial payload targets.

### Universal Module Interface

The interface should ultimately define:

- mounting-hole pattern,
- locating pins / guides,
- mechanical locking mechanism,
- DC power connector,
- data connector,
- module-presence detection,
- emergency disconnect / safety interlock.

The first functional module will be a **bin / pallet handling attachment**.

---

## 4. ROS 2 Architecture

Planned package split:

```text
ros2_ws/src/
├── amr_description/       # URDF/Xacro, meshes, TF geometry
├── amr_bringup/           # launch, parameters, system startup
├── amr_simulation/        # Gazebo-specific integration
├── amr_navigation/        # Nav2, maps, planner configuration
├── amr_control/           # base control / hardware interface
└── amr_missions/          # warehouse missions and docking logic
```

### Core Topics / Interfaces

```text
/cmd_vel          velocity command
/odom             wheel / simulated odometry
/scan             ROS LiDAR LaserScan target topic
/tf, /tf_static   robot transform tree
/map              SLAM / navigation map
/imu/data         IMU data when integrated
/joint_states     wheel / mechanism state
```

Topic names may change during implementation, but should be standardized before Nav2 integration.

---

## 5. Robot Frame Plan

Recommended TF hierarchy:

```text
map
└── odom
    └── base_footprint
        └── base_link
            ├── front_left_wheel
            ├── front_right_wheel
            ├── rear_left_wheel
            ├── rear_right_wheel
            ├── lidar_link
            ├── imu_link
            └── module_mount_link
                └── attachment_link
```

The final Fusion dimensions should drive these transforms.

---

## 6. Simulation Architecture

```text
ROS 2 Nodes
   |
   |  /cmd_vel, /scan, /odom, /tf
   v
ros_gz_bridge
   |
   v
Gazebo Sim
   |
   +-- AMR physics
   +-- wheel joints
   +-- DiffDrive
   +-- LiDAR
   +-- warehouse world
```

### Immediate Simulation Rule

Do **not** add SLAM/Nav2 until the following chain is proven:

```text
ROS /cmd_vel
   -> bridge
   -> Gazebo DiffDrive
   -> correct wheel joints
   -> visible robot movement
   -> odometry
```

Then bridge LiDAR and validate sensor data.

---

## 7. Hardware Architecture

Prototype target:

```text
Compute Layer
   |
ROS 2 / High-Level Logic
   |
Motor / MCU Interface
   |
Motor Drivers
   |
4 Drive Motors

Sensors:
LiDAR + IMU + Wheel Encoders + safety/obstacle sensors
```

Exact controller, motor driver, battery, and sensors will be frozen after the existing hardware inventory is documented.

---

## 8. CAD-to-Simulation-to-Hardware Flow

```text
Fusion CAD
   |
   +--> dimensions --------------------+
   +--> mesh export ----------------+  |
   +--> mass / CG assumptions ----+ |  |
                                  | |  |
                                  v v  v
                              URDF / Xacro
                                  |
                                  v
                               Gazebo
                                  |
                           autonomy validation
                                  |
                                  v
                         physical prototype
                                  |
                                  v
                          measured feedback
                                  |
                                  +----> CAD / model update
```

This loop is the core engineering workflow of the project.

---

## 9. Safety Architecture

The final AMR concept should include:

- emergency stop,
- obstacle stop zone,
- speed limiting,
- command timeout / watchdog,
- safe startup state,
- module-lock verification,
- low-battery safe behaviour,
- manual override for prototype testing.

---

## 10. Phase-1 Success Criteria

Architecture is considered integrated when:

1. one canonical robot geometry is used,
2. ROS 2 commands move the Gazebo robot reliably,
3. odometry and TF are valid,
4. LiDAR is visible in ROS 2,
5. SLAM can create a warehouse map,
6. Nav2 can reach a selected goal,
7. physical prototype follows the same motion/control assumptions,
8. the modular attachment concept is represented in Fusion and documented.
