param(
    [int]$Timeout = 210
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$EvidenceDir = Join-Path $RepoRoot 'media\evidence'
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Log = Join-Path $EvidenceDir "obstacle-demo-$Stamp.txt"

Write-Host '=== SIH26112 OBSTACLE AVOIDANCE DEMO ==='
Write-Host 'Resetting the robot to the warehouse origin for a repeatable route...'
& powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'final_demo.ps1') -NoBuild 2>&1 |
    Tee-Object -FilePath $Log -Append
if ($LASTEXITCODE -ne 0) { throw 'Could not start clean demo stack.' }

Write-Host 'Opening Gazebo so the obstacle crate and AMR path are visible...'
& powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'show_gazebo.ps1') 2>&1 |
    Tee-Object -FilePath $Log -Append
Start-Sleep -Seconds 3

Write-Host 'Sending SKU006 -> RACK_F. The centre-aisle crate is detected through /scan and represented in Nav2 costmaps.'
& powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'run_mission.ps1') SKU006 -Timeout $Timeout 2>&1 |
    Tee-Object -FilePath $Log -Append
$Result = $LASTEXITCODE

Write-Host "Evidence log: $Log"
if ($Result -eq 0) {
    Write-Host 'OBSTACLE DEMO PASS: autonomous rack pickup and packing delivery completed.'
    exit 0
}

Write-Host "OBSTACLE DEMO FAIL: mission exit code $Result"
exit $Result
