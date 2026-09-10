# ROS 2 Workspace

Clean development target for the canonical AMR software stack.

Available package:

- [`amr_mission_manager`](src/amr_mission_manager/README.md): standalone warehouse
  inventory, SKU resolution, and map-frame target publication for later Nav2
  integration. Its README includes build, launch, demo, and test commands.

Package layout (all packages except `amr_mission_manager` are planned):

```text
src/
├── amr_description/
├── amr_bringup/
├── amr_simulation/
├── amr_navigation/
├── amr_control/
└── amr_mission_manager/
```

Do not copy legacy files blindly. First fix the canonical robot model and shared geometry, then migrate useful parts from `legacy/yashraj-handover/`.
