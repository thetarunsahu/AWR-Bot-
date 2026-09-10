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

function Invoke-LoggedPowerShell {
    param(
        [Parameter(Mandatory=$true)][string]$ScriptPath,
        [string[]]$Arguments = @()
    )

    # Windows PowerShell 5.1 converts text written by a child native process to
    # stderr into ErrorRecord objects. ROS 2 commonly writes normal [INFO]
    # messages there, so ErrorActionPreference=Stop would incorrectly abort the
    # validation. Temporarily continue, stringify every record, and preserve the
    # real child-process exit code.
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & powershell -NoProfile -ExecutionPolicy Bypass -File $ScriptPath @Arguments 2>&1 |
            ForEach-Object {
                $text = $_.ToString()
                Write-Host $text
                Add-Content -Path $Log -Value $text
            }
        return $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
}

Log-Line '=== SIH26112 FINAL VALIDATION ==='
Log-Line "Started: $(Get-Date -Format s)"
Log-Line 'Purpose: software preflight + multi-rack navigation + recovery + obstacle-route + delivery validation.'

if (-not $SkipRestart) {
    Log-Line 'Building and starting a clean release-candidate stack...'
    $startCode = Invoke-LoggedPowerShell -ScriptPath (Join-Path $PSScriptRoot 'final_demo.ps1')
    if ($startCode -ne 0) { throw 'Final demo stack did not start cleanly.' }
}

Log-Line ''
Log-Line '--- SOFTWARE PREFLIGHT ---'
$preflightCode = Invoke-LoggedPowerShell -ScriptPath (Join-Path $PSScriptRoot 'preflight.ps1')
if ($preflightCode -ne 0) {
    Log-Line 'FINAL VALIDATION RESULT: FAIL - PREFLIGHT'
    exit 2
}

# SKU006 is first from the origin because its route exercises the right-side
# warehouse corridor containing the visible LiDAR obstacle crate.
$Skus = @('SKU006', 'SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005')
$Failures = @()

foreach ($Sku in $Skus) {
    Log-Line ''
    Log-Line "--- VALIDATING $Sku ---"
    $missionCode = Invoke-LoggedPowerShell `
        -ScriptPath (Join-Path $PSScriptRoot 'run_mission.ps1') `
        -Arguments @($Sku, '-Timeout', "$TimeoutPerMission")

    if ($missionCode -ne 0) {
        $Failures += $Sku
        Log-Line "RESULT ${Sku}: FAIL (exit $missionCode)"
    } else {
        Log-Line "RESULT ${Sku}: PASS"
    }
    Start-Sleep -Seconds 2
}

Log-Line ''
Log-Line '--- ROS GRAPH SNAPSHOT ---'
$previousPreference = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
try {
    & docker exec amr-ros-jazzy bash -lc 'source /opt/ros/jazzy/setup.bash && cd /workspace/AWR-Bot-/ros2_ws && source install/setup.bash && ros2 node list && echo ---TOPICS--- && ros2 topic list' 2>&1 |
        ForEach-Object {
            $text = $_.ToString()
            Write-Host $text
            Add-Content -Path $Log -Value $text
        }
}
finally {
    $ErrorActionPreference = $previousPreference
}

Log-Line ''
if ($Failures.Count -eq 0) {
    Log-Line 'FINAL VALIDATION RESULT: PASS'
    Log-Line 'All six physical rack destinations completed rack pickup + packing delivery.'
    Log-Line 'Release candidate is eligible for merge/freeze.'
    Log-Line "Evidence log: $Log"
    exit 0
}

Log-Line "FINAL VALIDATION RESULT: FAIL - $($Failures -join ', ')"
Log-Line 'Do not merge/freeze until the failed missions are resolved.'
Log-Line "Evidence log: $Log"
exit 2
