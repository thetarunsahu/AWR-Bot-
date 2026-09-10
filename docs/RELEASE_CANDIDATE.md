# SIH26112 Software Release Candidate

## Scope freeze

The `feature/amr-mission-manager` branch is now the **final software/simulation release candidate** for the SIH demo. New feature work is frozen. From this point, only changes required to make the final validation pass should be accepted.

## Included in the release candidate

- ROS 2 Jazzy + Gazebo warehouse simulation
- four-wheel AMR model and ROS-Gazebo bridge
- LiDAR `/scan`, odometry `/odom`, TF and SLAM map `/map`
- lean Nav2 navigation stack
- Nav2 collision-aware local/global costmaps
- bounded abort recovery with costmap clearing and retries
- SKU inventory and six physical rack destinations
- rack pickup -> packing-zone delivery Mission Manager
- modular `/amr/module_command` PICKUP / DROP interface
- visible centre-aisle obstacle scenario
- custom RViz judge visualization
- one-command Windows startup and mission scripts
- final multi-rack validation harness
- obstacle demo harness
- evidence capture tooling
- judge recording shot list and final test checklist

## Known historical validation

Before this release-candidate reliability update, SKU004 successfully completed the full sequence:

`SKU004 -> RACK_D -> PICKUP -> PACKING_ZONE -> DROP -> MISSION_COMPLETE`

SKU001 and SKU006 previously reached Nav2 and then aborted. The release candidate adds bounded recovery and Nav2 reliability tuning specifically so these and the other rack destinations can be retested under one controlled final validation run.

## Merge gate

Do **not** merge/freeze into the final integration/main target merely because the code is committed. First run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\final_validation.ps1
```

The branch is eligible for final merge only when the generated evidence report ends with:

```text
FINAL VALIDATION RESULT: PASS
```

After a pass, record the exact commit SHA used for the demo and stop feature development.
