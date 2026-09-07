# Branch Workflow

Recommended working model for the three-person team:

| Branch | Primary Use |
|---|---|
| `main` | stable, reviewed project state |
| `simulation` | Yashraj — ROS 2, Gazebo, navigation |
| `hardware` | Aaditya — hardware docs / firmware integration |
| `cad` | Tarun — CAD-related exports / design notes |
| `integration` | combined cross-track testing |

## Rule

Do not develop directly on `legacy/yashraj-handover/`. That directory is the preserved baseline.

Feature work should be tested on the relevant branch and moved to `main` after it is understandable, reproducible and documented.
