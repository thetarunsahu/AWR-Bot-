param(
    [int]$TimeoutPerMission = 210,
    [switch]$SkipRestart
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$EvidenceDir = Join-Path $RepoRoot 'media\evidence'
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Log = Join-Path $EvidenceDir "final-validation-$Stamp.txt"

function Log-Line([string]$Text) {
    $Text | Tee-Object -FilePath $Log -Append
}

Log-Line '=== SIH26112 FINAL VALIDATION ==='
Log-Line "Started: $(Get-Date -Format s)"
Log-Line 'Purpose: multi-rack navigation + recovery + obstacle-route + delivery validation.'

if (-not $SkipRestart) {
    Log-Line 'Starting a clean release-candidate stack...'
    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'final_demo.ps1') -NoBuild 2>&1 |
        Tee-Object -FilePath $Log -Append
    if ($LASTEXITCODE -ne 0) { throw 'Final demo stack did not start cleanly.' }
}

# SKU006 is first from the origin because its route exercises the right-side
# warehouse corridor containing the visible LiDAR obstacle crate.
$Skus = @('SKU006', 'SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005')
$Failures = @()

foreach ($Sku in $Skus) {
    Log-Line ''
    Log-Line "--- VALIDATING $Sku ---"
    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'run_mission.ps1') $Sku -Timeout $TimeoutPerMission 2>&1 |
        Tee-Object -FilePath $Log -Append
    if ($LASTEXITCODE -ne 0) {
        $Failures += $Sku
        Log-Line "RESULT $Sku: FAIL (exit $LASTEXITCODE)"
    } else {
        Log-Line "RESULT $Sku: PASS"
    }
    Start-Sleep -Seconds 3
}

Log-Line ''
Log-Line '--- ROS GRAPH SNAPSHOT ---'
& docker exec amr-ros-jazzy bash -lc 'source /opt/ros/jazzy/setup.bash && cd /workspace/AWR-Bot-/ros2_ws && source install/setup.bash && ros2 node list && echo ---TOPICS--- && ros2 topic list' 2>&1 |
    Tee-Object -FilePath $Log -Append

Log-Line ''
if ($Failures.Count -eq 0) {
    Log-Line 'FINAL VALIDATION RESULT: PASS'
    Log-Line 'All six physical rack destinations completed rack pickup + packing delivery.'
    Log-Line 'Release candidate is eligible for merge/freeze.'
    exit 0
}

Log-Line "FINAL VALIDATION RESULT: FAIL - $($Failures -join ', ')"
Log-Line 'Do not merge/freeze until the failed missions are resolved.'
exit 2
