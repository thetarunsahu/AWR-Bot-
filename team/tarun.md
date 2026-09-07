# Tarun — System Architecture, Fusion CAD & Integration

## Role

Primary owner of the **overall AMR architecture**, mechanical concept, Fusion CAD direction and cross-team integration.

## Current Responsibilities

- define the final SIH26112 AMR concept,
- separate scaled prototype requirements from industrial concept requirements,
- freeze shared geometry values,
- create / coordinate Fusion 360 CAD,
- design the modular top interface,
- define the bin/pallet module mechanism,
- ensure CAD, URDF and physical hardware use consistent dimensions,
- maintain architecture and decision documentation,
- coordinate the final technical story for the SIH demo.

## Immediate Work Queue

### T1 — Specification Freeze
Create the first proper specification set:

- overall length,
- overall width,
- overall height,
- wheel diameter / radius,
- wheel width,
- wheelbase,
- track width,
- prototype payload,
- industrial target payload,
- LiDAR position,
- controller / battery placement,
- modular-interface footprint.

### T2 — Fusion Base Assembly
Model:

1. lower chassis,
2. four wheels,
3. motor mounts,
4. electronics/battery packaging,
5. sensor mounts,
6. upper modular plate.

### T3 — Module Interface
Define:

- mechanical locating system,
- lock / unlock concept,
- power connection,
- data connection,
- module detection / interlock.

### T4 — Primary Attachment
Freeze a practical bin/pallet lifting mechanism and represent it in CAD.

### T5 — Engineering Validation
Later:

- structural simulation,
- stress/deformation checks,
- factor-of-safety reporting,
- weight/material optimization,
- selected topology/generative optimization.

## Inputs Needed From Team

### From Yashraj
- URDF frame requirements,
- Gazebo constraints,
- sensor field-of-view requirements,
- mesh format / simulation simplification needs.

### From Aaditya
- actual chassis measurements,
- wheel dimensions,
- motor/driver dimensions,
- battery and controller dimensions,
- sensor mounting constraints.

## Deliverables

- Fusion AMR assembly,
- modular interface CAD,
- module CAD,
- shared dimensions in `docs/DECISIONS.md`,
- renders / exploded views,
- CAD-to-URDF handoff geometry,
- architecture diagram and final integration narrative.
