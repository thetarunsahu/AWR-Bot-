# ROS 2 Workspace

Clean development target for the canonical AMR software stack.

Planned packages:

```text
src/
├── amr_description/
├── amr_bringup/
├── amr_simulation/
├── amr_navigation/
├── amr_control/
└── amr_missions/
```

Do not copy legacy files blindly. First fix the canonical robot model and shared geometry, then migrate useful parts from `legacy/yashraj-handover/`.
