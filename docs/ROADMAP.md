# Development Roadmap

This roadmap keeps the team from jumping to advanced autonomy before the base system is stable.

## Phase 0 — Repository & Baseline

- [x] create GitHub repository
- [x] preserve Yashraj handover under `legacy/`
- [x] add architecture and team ownership documents
- [ ] document existing physical hardware
- [ ] freeze first robot specification sheet

## Phase 1 — Base Motion (M1)

Goal: command the canonical AMR model reliably from ROS 2.

- [ ] choose one canonical four-wheel robot model
- [ ] make wheel radius/separation consistent
- [ ] add ROS-Gazebo bridge
- [ ] verify forward motion
- [ ] verify reverse motion
- [ ] verify left/right turning
- [ ] bridge and validate odometry
- [ ] define coherent TF tree

**Exit condition:** Gazebo robot can be driven reliably with ROS 2 velocity commands and reports sensible odometry.

## Phase 2 — Perception (M2)

- [ ] integrate LiDAR in the canonical robot model
- [ ] bridge LiDAR to ROS `/scan`
- [ ] verify ranges in RViz
- [ ] add IMU model / physical IMU plan
- [ ] verify sensor frames
- [ ] basic emergency obstacle stop

**Exit condition:** robot can perceive obstacles and ROS receives valid sensor data.

## Phase 3 — Mapping & Navigation (M3)

- [ ] integrate SLAM Toolbox
- [ ] map the warehouse world
- [ ] save/reload map
- [ ] configure Nav2
- [ ] send goal pose
- [ ] global path planning
- [ ] local obstacle avoidance
- [ ] recovery behaviours

**Exit condition:** robot autonomously reaches goals in the Gazebo warehouse world.

## Phase 4 — Fusion CAD & Modular Platform (M4)

Parallel with Phases 1–3:

- [ ] freeze target envelope and payload
- [ ] create Fusion chassis assembly
- [ ] motor mounts and wheel layout
- [ ] electronics/battery packaging
- [ ] LiDAR and sensor mounts
- [ ] universal top module interface
- [ ] bin/pallet handling module
- [ ] structural simulation
- [ ] topology / generative optimization where useful
- [ ] export simulation meshes

**Exit condition:** CAD represents a manufacturable modular AMR and supplies geometry to URDF.

## Phase 5 — Physical Prototype (M5)

- [ ] document current chassis and parts
- [ ] repair / organize wiring
- [ ] mount controller and power system
- [ ] integrate motor control
- [ ] add encoder feedback
- [ ] mount LiDAR / IMU
- [ ] ROS command to physical movement
- [ ] emergency stop / manual override
- [ ] build scaled modular attachment

**Exit condition:** physical robot executes controlled movement and at least one module action.

## Phase 6 — Warehouse Mission Demo (M6)

Target demo:

```text
Start
 -> receive destination
 -> localize
 -> navigate through warehouse
 -> avoid obstacle
 -> reach pickup point
 -> align / dock
 -> operate bin-pallet module
 -> navigate to drop point
 -> release load
 -> report mission complete
```

- [ ] mission state machine
- [ ] pickup/docking logic
- [ ] module command interface
- [ ] simulated mission
- [ ] scaled physical mission
- [ ] failure recovery tests

## Phase 7 — SIH Presentation Readiness

- [ ] Fusion renders
- [ ] simulation recording
- [ ] prototype recording
- [ ] architecture diagram
- [ ] before/after optimization evidence
- [ ] BOM and cost estimate
- [ ] innovation comparison
- [ ] demo script
- [ ] backup demo video
- [ ] final repository cleanup

## Rule

No milestone is marked complete because the code exists. It is complete only after a repeatable test passes and the result is documented.
