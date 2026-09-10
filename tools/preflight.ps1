$ErrorActionPreference = 'Stop'
$Container = 'amr-ros-jazzy'

$running = (& docker ps --format '{{.Names}}') -contains $Container
if (-not $running) {
    throw "Container '$Container' is not running. Start .\tools\final_demo.ps1 first."
}

Write-Host '=== SIH26112 SOFTWARE PREFLIGHT ==='

# Keep the bash payload on one physical command line. Windows PowerShell 5.1
# can mangle a multi-line native-process argument before it reaches `bash -lc`.
$Command = 'set -e; source /opt/ros/jazzy/setup.bash; cd /workspace/AWR-Bot-/ros2_ws; source install/setup.bash; echo "[1/4] Python syntax"; python3 -m py_compile src/amr_navigation/scripts/target_pose_nav2_bridge.py src/amr_mission_manager/amr_mission_manager/mission_manager.py src/amr_mission_manager/amr_mission_manager/warehouse_demo.py; echo "[2/4] URDF/Xacro"; XACRO=$(ros2 pkg prefix amr_description)/share/amr_description/urdf/amr.urdf.xacro; xacro "$XACRO" > /tmp/amr-preflight.urdf; check_urdf /tmp/amr-preflight.urdf >/dev/null; echo "[3/4] Mission manager tests"; colcon test --packages-select amr_mission_manager --event-handlers console_direct+; colcon test-result --test-result-base build/amr_mission_manager --verbose; echo "[4/4] Required ROS packages"; for pkg in nav2_msgs nav2_controller nav2_planner nav2_bt_navigator slam_toolbox ros_gz_bridge; do ros2 pkg prefix "$pkg" >/dev/null; done; echo "PREFLIGHT PASS"'

& docker exec $Container bash -lc $Command
if ($LASTEXITCODE -ne 0) {
    throw 'Software preflight failed.'
}
