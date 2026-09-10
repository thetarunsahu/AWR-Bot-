param(
    [int]$TimeoutPerMission = 240
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$EvidenceDir = Join-Path $RepoRoot 'media\evidence'
New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$Log = Join-Path $EvidenceDir "critical-validation-$Stamp.txt"

function Run-Child {
    param([string]$ScriptPath, [string[]]$Arguments = @())
    $old = $ErrorActionPreference
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
        $ErrorActionPreference = $old
    }
}

'=== SIH26112 CRITICAL VALIDATION ===' | Tee-Object -FilePath $Log -Append
'Routes: SKU006 obstacle mission, then SKU001 sequential mission through staging.' | Tee-Object -FilePath $Log -Append

$start = Run-Child (Join-Path $PSScriptRoot 'final_demo.ps1')
if ($start -ne 0) { throw 'Final stack startup failed.' }

$preflight = Run-Child (Join-Path $PSScriptRoot 'preflight.ps1')
if ($preflight -ne 0) {
    'CRITICAL VALIDATION: FAIL - PREFLIGHT' | Tee-Object -FilePath $Log -Append
    exit 2
}

$failed = @()
foreach ($sku in @('SKU006', 'SKU001')) {
    "--- $sku ---" | Tee-Object -FilePath $Log -Append
    $code = Run-Child (Join-Path $PSScriptRoot 'run_mission.ps1') @($sku, '-Timeout', "$TimeoutPerMission")
    if ($code -ne 0) {
        $failed += $sku
        "RESULT ${sku}: FAIL (exit $code)" | Tee-Object -FilePath $Log -Append
    } else {
        "RESULT ${sku}: PASS" | Tee-Object -FilePath $Log -Append
    }
    Start-Sleep -Seconds 2
}

if ($failed.Count -eq 0) {
    'CRITICAL VALIDATION: PASS' | Tee-Object -FilePath $Log -Append
    "Evidence log: $Log" | Tee-Object -FilePath $Log -Append
    exit 0
}

"CRITICAL VALIDATION: FAIL - $($failed -join ', ')" | Tee-Object -FilePath $Log -Append
"Evidence log: $Log" | Tee-Object -FilePath $Log -Append
exit 2
