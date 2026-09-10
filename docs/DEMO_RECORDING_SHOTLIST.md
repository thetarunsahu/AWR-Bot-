# SIH26112 Judge Demo Recording Shot List

Keep the final video short, visual and evidence-driven. A 60–90 second clean capture is better than a long terminal session.

## Recommended recording sequence

1. **Warehouse overview — 5 s**
   - Gazebo top/isometric view.
   - Show six rack zones, packing zone, centre-aisle obstacle crate and AMR.

2. **Autonomy stack — 5 s**
   - Briefly show the terminal with `FINAL STACK READY`.
   - Avoid scrolling through build logs.

3. **Mission command — 5 s**
   - Run one SKU using `judge_demo.ps1` or `run_mission.ps1`.
   - Keep the status terminal visible enough to read `SKU_RESOLVED` and the rack ID.

4. **Autonomous rack navigation — 15–25 s**
   - Focus Gazebo on the AMR.
   - Do not manually send `/cmd_vel`.
   - If using SKU006 from a clean origin, keep the obstacle crate in frame so the avoidance path is visible.

5. **RViz engineering proof — 10–15 s**
   - Show SLAM map, LiDAR points, AMR model and Nav2 planned path.
   - This is the technical proof that the robot is not following a hard-coded animation.

6. **Rack arrival + modular action — 5–10 s**
   - Show `ARRIVED_RACK` and `LOAD_ACQUIRED`.
   - Explain that `/amr/module_command` is the software interface for a real bin lift / conveyor / pallet module.

7. **Packing delivery — 10–20 s**
   - Show the AMR autonomously reaching the green packing zone.
   - End on `MISSION_COMPLETE`.

## Screenshots to keep

Store final images under `media/evidence/` or `media/screenshots/`:

- `01-final-stack-ready.png`
- `02-gazebo-warehouse-overview.png`
- `03-rviz-map-lidar-path.png`
- `04-obstacle-avoidance.png`
- `05-arrived-rack-load-acquired.png`
- `06-mission-complete.png`

## Judge narration in one sentence

> "A warehouse SKU is resolved to a rack, Nav2 autonomously plans through LiDAR-derived costmaps, the modular payload interface performs pickup, and the same AMR then delivers the load to the packing zone without manual driving."

## One-command presentation

Normal Gazebo demo:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\judge_demo.ps1 SKU004
```

Gazebo + RViz engineering demo:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\judge_demo.ps1 SKU006 -WithRViz
```

Before recording the final submission, run `tools/final_validation.ps1` and keep the generated evidence log.
