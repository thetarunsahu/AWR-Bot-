# Aaditya — Physical Prototype & Hardware Integration

## Role

Primary owner of the **physical AMR prototype, hardware inventory, wiring and mechanical/electronic integration**.

## Immediate Work Queue

### A1 — Hardware Inventory
Document every available component:

- chassis,
- motors,
- wheels,
- motor drivers,
- battery / power supply,
- controller / MCU / SBC,
- encoders,
- LiDAR,
- IMU,
- ultrasonic / auxiliary sensors,
- switches / emergency stop,
- attachment hardware.

Record part number, voltage, dimensions and quantity where possible.

### A2 — Measurements
Measure and record:

- chassis length / width / height,
- wheel diameter and width,
- wheelbase,
- track width,
- motor mount locations,
- electronics mounting area,
- top plate available area.

Share measured values before CAD is frozen.

### A3 — Wiring Baseline
Create a simple wiring diagram showing:

```text
Battery
  -> protection / switch
  -> motor driver -> motors
  -> regulator(s) -> controller / sensors
```

Document actual voltage rails and current constraints.

### A4 — Clean Prototype Layout
Prepare a clean physical layout for:

- controller,
- motor driver,
- battery,
- LiDAR,
- IMU,
- emergency stop,
- cable routing,
- modular attachment plate.

### A5 — Drive Tests
With Yashraj:

- individual wheel/motor direction test,
- forward/reverse test,
- left/right turn test,
- stop test,
- encoder feedback test if available.

### A6 — Modular Attachment Prototype
Support the physical implementation of the selected bin/pallet handling attachment and its locking/mounting mechanism.

## Inputs Needed From Team

### From Tarun
- final mounting layout,
- CAD hole pattern / modular interface,
- required sensor position,
- attachment dimensions.

### From Yashraj
- motor-control command requirements,
- encoder expectations,
- ROS hardware interface expectations,
- LiDAR/IMU topic requirements.

## Deliverables

- `hardware/BOM.md`,
- measured-dimension sheet,
- wiring diagram,
- clean prototype mounting plan,
- motor and power test results,
- sensor integration notes,
- physical attachment build notes,
- photos/videos for final documentation.
