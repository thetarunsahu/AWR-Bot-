# Integration Plan

## Objective

Keep Fusion CAD, ROS/Gazebo and the physical prototype aligned so they converge into one AMR instead of becoming three unrelated demos.

## Shared Parameters

The following values are controlled project-wide and must be recorded in `docs/DECISIONS.md` once frozen:

- chassis length / width / height,
- wheel radius and width,
- wheelbase,
- track width / wheel separation,
- base mass assumption,
- LiDAR XYZ + orientation,
- IMU XYZ + orientation,
- battery position,
- controller position,
- module-interface footprint,
- module attachment height,
- prototype payload,
- target industrial payload.

## Integration Flow

```text
Tarun / Fusion
  |
  | dimensions + mass assumptions + meshes
  v
Yashraj / URDF-Xacro-Gazebo
  |
  | validated frames + motion + sensor requirements
  v
Aaditya / Physical Prototype
  |
  | measured hardware constraints + real test results
  +---------------------------------------------+
                                                |
                         feedback to CAD/model <-+
```

## CAD -> ROS / Gazebo Handoff

Tarun should provide:

1. overall dimensions,
2. wheel centers and wheel geometry,
3. sensor mount transforms,
4. attachment mount transform,
5. simplified collision geometry,
6. visual mesh exports where useful,
7. expected mass and center-of-gravity assumptions.

Yashraj should not infer dimensions from screenshots once these values are available.

## ROS -> Hardware Handoff

Yashraj should provide:

- expected `/cmd_vel` convention,
- wheel velocity mapping,
- frame names,
- encoder / odometry expectations,
- sensor topic requirements,
- update-rate expectations,
- command timeout / watchdog behaviour.

Aaditya should provide:

- actual motor and driver limits,
- actual wheel dimensions,
- encoder counts / revolution if available,
- battery voltage and current constraints,
- controller connectivity,
- physical sensor mounting constraints.

## First Integration Test

### Simulation

```text
ROS Twist
 -> bridge
 -> DiffDrive
 -> robot motion
 -> odom
 -> TF
```

### Hardware

```text
ROS Twist
 -> hardware interface / MCU
 -> motor driver
 -> motors
 -> encoder feedback
 -> odom
```

Both should use the same high-level command convention.

## Attachment Integration

Define a module API before adding many modules.

Suggested conceptual interface:

```text
module_present
module_locked
module_id
module_state
module_command
module_fault
```

For Phase 1, only the bin/pallet module needs to be functional. Future modules should reuse the same physical and software contract.

## Integration Reviews

Before a major merge or hardware change, check:

- Are shared dimensions still consistent?
- Is one canonical robot description being used?
- Do topic and frame names match documentation?
- Is the physical hardware capable of the simulated command range?
- Did a CAD change require a URDF update?
- Did a hardware change require a CAD update?

## Demo Integration Definition

The project is considered SIH-demo integrated when the team can explain and show a single chain:

```text
Fusion engineered platform
        -> same geometry in simulation
        -> autonomous mission in Gazebo
        -> same control architecture on scaled physical robot
        -> one modular payload action
```
