# Engineering Decision Log

Use this file for decisions that affect more than one project track.

## D-001 — Project Type

**Decision:** Build a modular indoor warehouse Autonomous Mobile Robot (AMR) platform.

**Status:** Frozen.

## D-002 — Primary Module

**Decision:** Phase-1 functional module will be a **bin / pallet handling module**.

**Status:** Direction frozen; exact mechanism is still open.

## D-003 — Drive Layout

**Decision:** Use a four-wheel differential / skid-steer AMR architecture for the main concept unless hardware measurements reveal a blocking constraint.

**Status:** Working baseline.

## D-004 — Development Representations

**Decision:** Fusion CAD, Gazebo simulation and the physical prototype are treated as representations of one system and must share geometry/configuration values.

**Status:** Frozen.

## D-005 — Yashraj Handover Preservation

**Decision:** Preserve the original handover under `legacy/yashraj-handover/` and do new clean integration work outside that directory.

**Status:** Frozen.

## D-006 — Navigation Development Order

**Decision:** Do not start full SLAM/Nav2 integration until base movement, bridge, odometry and TF are verified.

**Status:** Frozen.

---

# Parameters Awaiting Freeze

Fill this table only with measured or deliberately selected values.

| Parameter | Prototype | Industrial Concept | Status |
|---|---:|---:|---|
| Chassis length | TBD | TBD | open |
| Chassis width | TBD | TBD | open |
| Chassis height | TBD | TBD | open |
| Wheel radius | TBD | TBD | open |
| Wheel width | TBD | TBD | open |
| Wheelbase | TBD | TBD | open |
| Track width | TBD | TBD | open |
| Robot mass | TBD | TBD | open |
| Payload | TBD | TBD | open |
| Max speed | TBD | TBD | open |
| LiDAR position | TBD | TBD | open |
| Module footprint | TBD | TBD | open |
| Lift travel | TBD | TBD | open |
| Battery specification | TBD | TBD | open |

## How to Add a Decision

Use:

```text
## D-XXX — Name
Decision:
Reason:
Impact:
Status:
Date:
```

Do not silently change previously frozen cross-team parameters.