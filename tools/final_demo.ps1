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

function Get-RosNodes {
    $lines = @(& docker exec $Container bash -lc 'source /opt/ros/jazzy/setup.bash && cd /workspace/AWR-Bot-/ros2_ws && source install/setup.bash && ros2 node list' 2>$null)
    if ($LASTEXITCODE -ne 0) { return @() }
    return @($lines | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

function Get-RosTopics {
    $lines = @(& docker exec $Container bash -lc 'source /opt/ros/jazzy/setup.bash && cd /workspace/AWR-Bot-/ros2_ws && source install/setup.bash && ros2 topic list' 2>$null)
    if ($LASTEXITCODE -ne 0) { return @() }
    return @($lines | ForEach-Object { $_.Trim() } | Where-Object { $_ })
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
& docker exec -d $Container bash -lc 'source /opt/ros/jazzy/setup.bash && cd /workspace/AWR-Bot-/ros2_ws && source install/setup.bash && exec ros2 launch amr_bringup full_demo.launch.py headless:=true rviz:=false > /tmp/amr_final.log 2>&1'
if ($LASTEXITCODE -ne 0) { throw 'Failed to start final demo stack.' }

$required = @(
    '/slam_toolbox',
    '/controller_server',
    '/planner_server',
    '/bt_navigator',
    '/mission_manager',
    '/target_pose_nav2_bridge'
)

Write-Host 'Waiting for autonomy stack (up to 75 seconds)...'
$nodes = @()
$missing = $required
for ($attempt = 1; $attempt -le 25; $attempt++) {
    Start-Sleep -Seconds 3
    $nodes = Get-RosNodes
    $missing = @($required | Where-Object { $nodes -notcontains $_ })
    if ($missing.Count -eq 0) { break }
    if (($attempt % 5) -eq 0) {
        Write-Host "  still starting... missing: $($missing -join ', ')"
    }
}

$topics = Get-RosTopics
Write-Host ''
Write-Host '=== ROS NODES ==='
$nodes | Sort-Object | Write-Host
Write-Host '=== CRITICAL TOPICS ==='
@($topics | Where-Object { $_ -in @('/map','/scan','/odom','/cmd_vel') -or $_ -like '/amr/*' } | Sort-Object) | Write-Host

if ($missing.Count -gt 0) {
    Write-Host ''
    Write-Host "Stack did not become ready. Missing nodes: $($missing -join ', ')"
    Write-Host 'Last launch logs:'
    & docker exec $Container bash -lc 'tail -n 140 /tmp/amr_final.log'
    exit 2
}

$requiredTopics = @('/map', '/scan', '/odom', '/amr/task_request', '/amr/mission_status', '/amr/navigation_status')
$missingTopics = @($requiredTopics | Where-Object { $topics -notcontains $_ })
if ($missingTopics.Count -gt 0) {
    Write-Host "Warning: core nodes are active, but these topics are not visible yet: $($missingTopics -join ', ')"
}

Write-Host ''
Write-Host 'FINAL STACK READY.'
Write-Host 'Run a mission from another PowerShell:'
Write-Host '  powershell -ExecutionPolicy Bypass -File .\tools\run_mission.ps1 SKU004'
Write-Host 'To open Gazebo GUI:'
Write-Host '  powershell -ExecutionPolicy Bypass -File .\tools\show_gazebo.ps1'
