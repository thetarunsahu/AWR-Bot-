# Contributing Workflow

This repository is shared by Tarun, Yashraj and Aaditya.

## Branching

Recommended working branches:

- `main` — stable, reviewed project state
- `simulation` — ROS 2 / Gazebo work
- `hardware` — physical prototype notes / firmware
- `cad` — CAD exports / design documentation
- `integration` — cross-track integration tests

Short feature branches are preferred for risky changes.

## Before Pushing

1. Do not modify `legacy/yashraj-handover/` except to preserve the original handover.
2. Check whether your change modifies a shared dimension or interface.
3. If yes, update `docs/DECISIONS.md` and notify the other tracks.
4. Keep generated build folders out of Git.
5. Add a short note to documentation when a test actually becomes repeatable.

## Commit Style

Examples:

```text
sim: add ROS-Gazebo cmd_vel bridge
sim: validate four-wheel odometry
cad: add universal module mounting plate
hardware: document motor driver wiring
docs: update M1 test status
firmware: add motor command watchdog
```

## Definition of Done

A feature is not complete because the file exists. It is complete when:

- it builds / loads,
- the intended test passes,
- the result is reproducible,
- relevant documentation is updated.

## Shared Parameters

Never silently change:

- wheel radius,
- wheel separation / track width,
- wheelbase,
- chassis dimensions,
- sensor transforms,
- module mount geometry,
- motor polarity / command convention.

These affect CAD, simulation and physical hardware simultaneously.
