param(
    [Parameter(Position=0)]
    [ValidatePattern('^SKU\d{3}$')]
    [string]$Sku = 'SKU004',

    [int]$Timeout = 180
)

$ErrorActionPreference = 'Stop'
$Container = 'amr-ros-jazzy'

$running = (& docker ps --format '{{.Names}}') -contains $Container
if (-not $running) {
    throw "Container '$Container' is not running. Start .\tools\final_demo.ps1 first."
}

Write-Host "=== AUTONOMOUS DELIVERY: $Sku ==="
& docker exec $Container bash -lc "source /opt/ros/jazzy/setup.bash && cd /workspace/AWR-Bot-/ros2_ws && source install/setup.bash && ros2 run amr_mission_manager warehouse_demo $Sku --timeout $Timeout"
exit $LASTEXITCODE
