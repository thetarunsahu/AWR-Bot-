$ErrorActionPreference = 'Stop'
$Container = 'amr-ros-jazzy'

$running = (& docker ps --format '{{.Names}}') -contains $Container
if (-not $running) {
    throw "Container '$Container' is not running. Start .\tools\final_demo.ps1 first."
}

Write-Host '=== SIH26112 SOFTWARE PREFLIGHT ==='
& docker exec $Container bash /workspace/AWR-Bot-/tools/preflight.sh
if ($LASTEXITCODE -ne 0) {
    throw 'Software preflight failed.'
}
