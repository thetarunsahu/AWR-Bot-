param(
    [switch]$NoBuild
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Container = 'amr-ros-jazzy'
$Image = 'amr-ros-jazzy-ready'

function Test-DockerEngine {
    # Run through cmd.exe so PowerShell 5.1 does not convert Docker's stderr
    # into a terminating NativeCommandError while Docker Desktop is starting.
    & cmd.exe /d /c "docker info >nul 2>nul"
    return ($LASTEXITCODE -eq 0)
}

Write-Host '=== SIH26112 FINAL AMR DEMO ==='

if (-not (Test-DockerEngine)) {
    $desktop = 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
    if (-not (Test-Path $desktop)) {
        throw 'Docker Desktop was not found.'
    }
    Write-Host 'Docker engine is offline. Starting Docker Desktop...'
    Start-Process $desktop
    $ready = $false
    for ($i = 0; $i -lt 90; $i++) {
        Start-Sleep -Seconds 2
        if (Test-DockerEngine) {
            $ready = $true
            break
        }
    }
    if (-not $ready) {
        throw 'Docker engine did not become ready within 3 minutes. Open Docker Desktop and wait until Engine is running, then rerun this script.'
    }
}

Write-Host 'Docker engine ready.'

$existing = (& docker ps -a --format '{{.Names}}') -contains $Container
if (-not $existing) {
    $imageExists = (& docker images --format '{{.Repository}}') -contains $Image
    if (-not $imageExists) {
        throw "Docker image '$Image' is missing."
    }
    Write-Host 'Creating stable ROS container...'
    & docker run -d --name $Container --restart unless-stopped -v "${RepoRoot}:/workspace/AWR-Bot-" $Image sleep infinity | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create ROS container.' }
} else {
    Write-Host 'Restarting ROS container for a clean demo...'
    & docker restart $Container | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Failed to restart ROS container.' }
}

Start-Sleep -Seconds 3

if (-not $NoBuild) {
    Write-Host 'Building ROS 2 workspace...'
    & docker exec $Container bash -lc 'source /opt/ros/jazzy/setup.bash && cd /workspace/AWR-Bot-/ros2_ws && colcon build --symlink-install'
    if ($LASTEXITCODE -ne 0) { throw 'ROS build failed.' }
}

Write-Host 'Starting Gazebo + SLAM + Nav2 + Mission Manager...'
& docker exec -d $Container bash -lc 'source /opt/ros/jazzy/setup.bash && cd /workspace/AWR-Bot-/ros2_ws && source install/setup.bash && ros2 launch amr_bringup full_demo.launch.py headless:=true rviz:=false > /tmp/amr_final.log 2>&1'
if ($LASTEXITCODE -ne 0) { throw 'Failed to start final demo stack.' }

Write-Host 'Waiting for autonomy stack...'
Start-Sleep -Seconds 15

$check = & docker exec $Container bash -lc 'source /opt/ros/jazzy/setup.bash && cd /workspace/AWR-Bot-/ros2_ws && source install/setup.bash && ros2 node list && echo ---TOPICS--- && ros2 topic list | grep -E "^/map$|^/scan$|^/odom$|^/amr/"'
$check | Write-Host

$required = @('/slam_toolbox', '/controller_server', '/planner_server', '/bt_navigator', '/mission_manager', '/target_pose_nav2_bridge')
$missing = @()
foreach ($name in $required) {
    if (-not ($check -contains $name)) { $missing += $name }
}

if ($missing.Count -gt 0) {
    Write-Host "Stack started but these nodes are missing: $($missing -join ', ')"
    Write-Host 'Last launch logs:'
    & docker exec $Container bash -lc 'tail -n 100 /tmp/amr_final.log'
    exit 2
}

Write-Host ''
Write-Host 'FINAL STACK READY.'
Write-Host 'Run a mission from another PowerShell:'
Write-Host '  powershell -ExecutionPolicy Bypass -File .\tools\run_mission.ps1 SKU004'
Write-Host 'To open Gazebo GUI:'
Write-Host '  powershell -ExecutionPolicy Bypass -File .\tools\show_gazebo.ps1'
