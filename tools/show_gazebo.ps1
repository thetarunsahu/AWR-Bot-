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

Write-Host 'Opening Gazebo GUI...'
# Gazebo Harmonic is provided through the ROS Jazzy vendor environment in this
# container, so source ROS before invoking the `gz` CLI.
& docker exec -d $Container bash -lc 'source /opt/ros/jazzy/setup.bash; export DISPLAY=host.docker.internal:0.0; export QT_X11_NO_MITSHM=1; export LIBGL_ALWAYS_SOFTWARE=1; gz sim -g > /tmp/gz_gui.log 2>&1'
if ($LASTEXITCODE -ne 0) {
    throw 'Failed to start Gazebo GUI.'
}

Start-Sleep -Seconds 2
Write-Host 'Gazebo GUI launch requested. Keep VcXsrv running.'
