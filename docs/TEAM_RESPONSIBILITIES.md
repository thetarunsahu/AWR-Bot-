# Team Responsibilities

This file defines the current ownership model for SIH26112. Ownership means **primary responsibility**, not that only one person may work on that area.

## Tarun — System Architecture, Fusion CAD & Integration

### Primary Responsibilities
- freeze the final AMR concept and system boundaries,
- define chassis dimensions and design assumptions,
- create / coordinate Fusion CAD,
- design the universal modular mounting interface,
- define the primary bin/pallet handling module,
- keep CAD dimensions synchronized with URDF and physical hardware,
- maintain project-level architecture and integration decisions,
- coordinate final technical presentation and demo flow.

### Immediate Tasks
1. Freeze prototype vs industrial target specifications.
2. Freeze wheelbase, track width, wheel radius, chassis envelope and sensor positions.
3. Create first Fusion AMR assembly.
4. Design modular top plate and attachment interface.
5. Share final geometry values with Yashraj and Aaditya.

Detailed file: [`../team/tarun.md`](../team/tarun.md)

---

## Yashraj — ROS 2, Gazebo & Autonomy

### Primary Responsibilities
- maintain the robot description and simulation,
- make ROS 2 <-> Gazebo communication reliable,
- validate wheel control and odometry,
- integrate LiDAR into ROS 2,
- build TF tree,
- add obstacle avoidance,
- add SLAM,
- integrate Nav2,
- build autonomous warehouse navigation and mission behaviour.

### Immediate Tasks
1. Consolidate the two current robot definitions into one canonical model.
2. Fix wheel-radius inconsistency.
3. Add and verify `ros_gz_bridge` for `/cmd_vel`, odometry and LiDAR.
4. Prove forward / backward / left / right motion.
5. Validate odometry and TF before SLAM.

Detailed file: [`../team/yashraj.md`](../team/yashraj.md)

---

## Aaditya — Physical Prototype & Hardware Integration

### Primary Responsibilities
- document current chassis and components,
- inspect motors, wheels, drivers and power system,
- organize wiring and electronics mounting,
- integrate required sensors on the physical prototype,
- build / support the physical modular attachment,
- validate mechanical fit and real-world movement,
- provide measured dimensions and hardware constraints to Tarun and Yashraj.

### Immediate Tasks
1. Create a hardware inventory with photos / part numbers where possible.
2. Measure the existing chassis, wheels and mounting locations.
3. Document current wiring.
4. Identify what hardware can be reused and what must be purchased.
5. Prepare a clean mounting plan for controller, battery, LiDAR and emergency stop.

Detailed file: [`../team/aaditya.md`](../team/aaditya.md)

---

## Shared Responsibilities

All three members participate in:
- integration testing,
- failure debugging,
- SIH demo rehearsals,
- documentation review,
- final presentation,
- keeping claims consistent with what has actually been tested.

## Integration Rule

No member should independently change a **shared physical parameter** such as wheel radius, wheel separation, chassis size, LiDAR pose, payload interface or attachment geometry without updating the other tracks.

Use [`DECISIONS.md`](DECISIONS.md) to record frozen values and major decisions.
