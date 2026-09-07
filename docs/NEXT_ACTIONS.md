# Immediate Next Actions

## Tarun
- measure/freeze shared AMR dimensions,
- start Fusion chassis assembly,
- define modular top plate,
- freeze first bin/pallet attachment mechanism.

## Yashraj
- copy useful legacy code into a clean package structure,
- consolidate to one four-wheel robot model,
- fix wheel geometry consistency,
- add ROS-Gazebo bridge,
- prove base movement + odometry.

## Aaditya
- fill `hardware/BOM.md`,
- measure current chassis/wheels,
- document motor, driver, battery and controller,
- create first wiring diagram,
- identify reusable hardware.

## Team Checkpoint

Next common checkpoint is **M1 — Base AMR Motion Ready**:

```text
canonical robot
 -> ROS /cmd_vel
 -> bridge
 -> Gazebo motion
 -> odometry
 -> TF
```

At the same time, CAD and physical measurements must converge on the same wheel/chassis parameters.
