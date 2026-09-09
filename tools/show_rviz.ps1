$ErrorActionPreference = 'Stop'
$Container = 'amr-ros-jazzy'

$running = (& docker ps --format '{{.Names}}') -contains $Container
if (-not $running) {
    throw "Container '$Container' is not running. Start .\tools\final_demo.ps1 first."
}

if (-not (Get-Process vcxsrv -ErrorAction SilentlyContinue)) {
    $candidates = @(
        'C:\Program Files\VcXsrv\vcxsrv.exe',
        'C:\Program Files (x86)\VcXsrv\vcxsrv.exe'
    )
    $vcxsrv = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $vcxsrv) {
        throw 'VcXsrv not found. Install/start XLaunch first.'
    }
    Write-Host 'Starting VcXsrv display :0...'
    Start-Process $vcxsrv -ArgumentList ':0','-multiwindow','-clipboard','-ac'
    Start-Sleep -Seconds 2
}

Write-Host 'Opening RViz2 with SIH26112 judge view...'
& docker exec -d $Container bash -lc 'source /opt/ros/jazzy/setup.bash; cd /workspace/AWR-Bot-/ros2_ws; source install/setup.bash; export DISPLAY=host.docker.internal:0.0; export QT_X11_NO_MITSHM=1; export LIBGL_ALWAYS_SOFTWARE=1; CFG=$(ros2 pkg prefix amr_navigation)/share/amr_navigation/rviz/amr_demo.rviz; rviz2 -d "$CFG" > /tmp/rviz.log 2>&1'
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to start RViz2.'
}

Write-Host 'RViz2 launch requested.'
Write-Host 'Judge view shows: SLAM map + LiDAR + AMR model + global path + costmap.'
