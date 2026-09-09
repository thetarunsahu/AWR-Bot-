param(
    [ValidatePattern('^SKU\d{3}$')]
    [string]$Sku = 'SKU004',
    [switch]$WithRViz,
    [int]$Timeout = 210
)

$ErrorActionPreference = 'Stop'

Write-Host '=== SIH26112 JUDGE DEMO ==='
Write-Host '1/4 Starting clean autonomous stack...'
& powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'final_demo.ps1') -NoBuild
if ($LASTEXITCODE -ne 0) { throw 'Final stack failed to start.' }

Write-Host '2/4 Opening Gazebo warehouse view...'
& powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'show_gazebo.ps1')
Start-Sleep -Seconds 3

if ($WithRViz) {
    Write-Host '3/4 Opening RViz sensor/navigation view...'
    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'show_rviz.ps1')
    Start-Sleep -Seconds 3
} else {
    Write-Host '3/4 RViz skipped. Use -WithRViz when a second visualization is wanted.'
}

Write-Host "4/4 Running autonomous warehouse mission for $Sku..."
Write-Host 'Start screen recording now if this is the judge capture.'
& powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'run_mission.ps1') $Sku -Timeout $Timeout
$Result = $LASTEXITCODE

if ($Result -eq 0) {
    Write-Host 'JUDGE DEMO COMPLETE: rack pickup + packing-zone delivery succeeded.'
} else {
    Write-Host "JUDGE DEMO FAILED with exit code $Result."
}
exit $Result
