[CmdletBinding()]
param(
    # Interaktiv nach dem dynamischen Startlink fragen (empfohlen).
    [switch]$PromptForUrl,

    # Optional: Start-URL direkt übergeben (vollständig inkl. Query). Wird NICHT geprintet.
    [string]$Url,

    # Optional: Start-URL aus .secrets/start_url.txt lesen.
    [switch]$UseStartUrlFile,

    # Charter-Datei
    [string]$CharterFile = "prompts/testdata/bto/v1.0/charter.json",

    # Lauf-Optionen
    [int]$MaxSteps = 25,

    # Debug
    [switch]$Headed,
    [int]$SlowmoMs = 0,

    # Post-Run Agent
    [bool]$PostAnalyze,
    [string]$ResultsRoot = "results/bto-checkout/runs",

    # Quality Gate (keep it green): fail if any atomic bullet is not PASS
    [switch]$QualityGate
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
    # Script liegt unter <root>/tools/
    $here = Split-Path -Parent $PSCommandPath
    return (Resolve-Path (Join-Path $here '..')).Path
}

function ConvertTo-RedactedUrlForDisplay([string]$value) {
    if ([string]::IsNullOrWhiteSpace($value)) { return "" }
    try {
        $uri = [System.Uri]::new($value)
        # Query/Fragment bewusst weglassen
        return "{0}://{1}{2}" -f $uri.Scheme, $uri.Authority, $uri.AbsolutePath
    } catch {
        # Best-effort fallback
        $noFrag = $value.Split('#')[0]
        return $noFrag.Split('?')[0]
    }
}

$repoRoot = Get-RepoRoot
$python = Join-Path $repoRoot '.venv/Scripts/python.exe'
$runner = Join-Path $repoRoot 'tools/execute_smoketest.py'
$analyzer = Join-Path $repoRoot 'tools/analyze_bto_run.py'
$supervisor = Join-Path $repoRoot 'tools/supervise_bto_run.py'
$charter = Join-Path $repoRoot $CharterFile
$startUrlFile = Join-Path $repoRoot '.secrets/start_url.txt'

if (-not (Test-Path $python)) {
    throw "Python-Env nicht gefunden: $python (erwarte .venv)."
}
if (-not (Test-Path $runner)) {
    throw "Runner nicht gefunden: $runner"
}
if ($PostAnalyze -and (-not (Test-Path $analyzer))) {
    throw "Analyzer nicht gefunden: $analyzer"
}
if ($QualityGate -and (-not (Test-Path $supervisor))) {
    throw "Supervisor nicht gefunden: $supervisor"
}
if (-not (Test-Path $charter)) {
    throw "Charter nicht gefunden: $charter"
}

$resultsRootAbs = Join-Path $repoRoot $ResultsRoot
$runId = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$runDir = Join-Path $resultsRootAbs $runId

# Default behavior (keep previous)
$ContinueOnFail = $true
$AutoAdvance = $true
$AutoFill = $true
if (-not $PSBoundParameters.ContainsKey('PostAnalyze')) { $PostAnalyze = $true }

# URL-Quelle bestimmen
$startUrl = $null
if (-not $PromptForUrl) {
    if ($UseStartUrlFile) {
        if (-not (Test-Path $startUrlFile)) {
            throw "Start-URL Datei nicht gefunden: $startUrlFile"
        }
        $startUrl = (Get-Content $startUrlFile -Raw).Trim()
    }
    if (-not [string]::IsNullOrWhiteSpace($Url)) {
        $startUrl = $Url.Trim()
    }
}

# Command bauen
$cmdArgs = @(
    $runner,
    '--charter-file', $charter,
    '--results-root', $resultsRootAbs,
    '--run-id', $runId
)

if ($MaxSteps -ne 0) {
    $cmdArgs += @('--max-steps', $MaxSteps)
}
if ($ContinueOnFail) { $cmdArgs += '--continue-on-fail' }
if ($AutoAdvance) { $cmdArgs += '--auto-advance' }
if ($AutoFill) { $cmdArgs += '--auto-fill' }
if ($Headed) { $cmdArgs += '--headed' }
if ($SlowmoMs -gt 0) { $cmdArgs += @('--slowmo-ms', $SlowmoMs) }

if ($PromptForUrl -or [string]::IsNullOrWhiteSpace($startUrl)) {
    # URL NICHT als CLI-Arg übergeben (History/Logs), sondern im Runner prompten lassen.
    $cmdArgs += '--prompt-for-url'
} else {
    if ([string]::IsNullOrWhiteSpace($startUrl)) {
        throw "Keine Start-URL gesetzt. Nutze -PromptForUrl oder -UseStartUrlFile oder -Url <...>."
    }
    $cmdArgs += @('--url', $startUrl)
}

# Minimaler, redacted Status-Print
if (-not [string]::IsNullOrWhiteSpace($startUrl)) {
    $display = ConvertTo-RedactedUrlForDisplay $startUrl
    Write-Host ("Start-URL (redacted): {0}  (Query/Fragment ausgeblendet)" -f $display)
} else {
    Write-Host "Start-URL wird interaktiv abgefragt (nicht als CLI-Arg)."
}

Write-Host ("Runner: {0}" -f (Join-Path $repoRoot 'tools/execute_smoketest.py'))
Write-Host ("Charter: {0}" -f $CharterFile)
Write-Host ("Run-ID: {0}" -f $runId)

& $python @cmdArgs
$exitCode = $LASTEXITCODE

if ($PostAnalyze) {
    try {
        if (Test-Path $runDir) {
            Write-Host ("Post-Run Agent: Analysiere Run und aktualisiere Report (Checklist) …")
            & $python $analyzer --run-dir $runDir --update-report
        } else {
            Write-Host ("⚠️ Post-Run Agent übersprungen: Run-Ordner nicht gefunden: {0}" -f $runDir)
        }
    } catch {
        Write-Host ("⚠️ Post-Run Agent Fehler: {0}" -f $_.Exception.Message)
    }
}

if ($QualityGate) {
    try {
        if (Test-Path $runDir) {
            Write-Host ("Quality-Gate: Prüfe atomare Checklist (strict) …")
            & $python $supervisor --run-dir $runDir --strict
            $gateExit = $LASTEXITCODE
            if ($gateExit -ne 0) {
                Write-Host ("❌ Quality-Gate FAILED. Siehe supervisor_summary.md im Run-Ordner.")
                exit $gateExit
            }
            Write-Host ("✅ Quality-Gate PASSED")
        }
    } catch {
        Write-Host ("⚠️ Quality-Gate Fehler: {0}" -f $_.Exception.Message)
        exit 2
    }
}

exit $exitCode
