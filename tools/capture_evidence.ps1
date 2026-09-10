$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$EvidenceDir = Join-Path $RepoRoot 'media\evidence'
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Report = Join-Path $EvidenceDir "system-evidence-$Stamp.txt"

$running = (& docker ps --format '{{.Names}}') -contains 'amr-ros-jazzy'
if (-not $running) {
    throw "Container 'amr-ros-jazzy' is not running."
}

'=== SIH26112 SOFTWARE EVIDENCE SNAPSHOT ===' | Out-File $Report -Encoding utf8
"Captured: $(Get-Date -Format s)" | Out-File $Report -Append -Encoding utf8

$Command = @'
source /opt/ros/jazzy/setup.bash
cd /workspace/AWR-Bot-/ros2_ws
source install/setup.bash
echo '--- NODES ---'
ros2 node list
echo '--- CRITICAL TOPICS ---'
ros2 topic list | sort
echo '--- NAV2 ACTION ---'
ros2 action info /navigate_to_pose || true
echo '--- COSTMAP RECOVERY SERVICES ---'
ros2 service list | grep clear_entirely || true
echo '--- MAP ---'
timeout 3 ros2 topic echo /map --once || true
echo '--- ODOM ---'
timeout 3 ros2 topic echo /odom --once || true
echo '--- SCAN SAMPLE ---'
timeout 3 ros2 topic echo /scan --once || true
echo '--- LAST FINAL DEMO LOG ---'
tail -n 120 /tmp/amr_final.log 2>/dev/null || true
'@

& docker exec amr-ros-jazzy bash -lc $Command 2>&1 |
    Out-File $Report -Append -Encoding utf8

Write-Host "Evidence saved: $Report"
