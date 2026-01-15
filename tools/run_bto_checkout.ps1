[CmdletBinding()]
param(
    # Interaktiv nach dem dynamischen Startlink fragen (empfohlen).
    [bool]$PromptForUrl = $true,

    # Optional: Start-URL direkt übergeben (vollständig inkl. Query). Wird NICHT geprintet.
    [string]$Url,

    # Optional: Start-URL aus .secrets/start_url.txt lesen.
    [switch]$UseStartUrlFile,

    # Charter-Datei
    [string]$CharterFile = "prompts/testdata/bto/v1.0/charter.json",

    # Lauf-Optionen
    [int]$MaxSteps = 25,
    [switch]$ContinueOnFail = $true,
    [switch]$AutoAdvance = $true,
    [switch]$AutoFill = $true,

    # Debug
    [switch]$Headed,
    [int]$SlowmoMs = 0
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
    # Script liegt unter <root>/tools/
    $here = Split-Path -Parent $PSCommandPath
    return (Resolve-Path (Join-Path $here '..')).Path
}

function Redact-UrlForDisplay([string]$value) {
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
$charter = Join-Path $repoRoot $CharterFile
$startUrlFile = Join-Path $repoRoot '.secrets/start_url.txt'

if (-not (Test-Path $python)) {
    throw "Python-Env nicht gefunden: $python (erwarte .venv)."
}
if (-not (Test-Path $runner)) {
    throw "Runner nicht gefunden: $runner"
}
if (-not (Test-Path $charter)) {
    throw "Charter nicht gefunden: $charter"
}

# URL-Quelle bestimmen
$startUrl = $null
if ($UseStartUrlFile) {
    if (-not (Test-Path $startUrlFile)) {
        throw "Start-URL Datei nicht gefunden: $startUrlFile"
    }
    $startUrl = (Get-Content $startUrlFile -Raw).Trim()
}
if (-not [string]::IsNullOrWhiteSpace($Url)) {
    $startUrl = $Url.Trim()
}

# Command bauen
$cmdArgs = @(
    $runner,
    '--charter-file', $charter
)

if ($MaxSteps -ne 0) {
    $cmdArgs += @('--max-steps', $MaxSteps)
}
if ($ContinueOnFail) { $cmdArgs += '--continue-on-fail' }
if ($AutoAdvance) { $cmdArgs += '--auto-advance' }
if ($AutoFill) { $cmdArgs += '--auto-fill' }
if ($Headed) { $cmdArgs += '--headed' }
if ($SlowmoMs -gt 0) { $cmdArgs += @('--slowmo-ms', $SlowmoMs) }

if ($PromptForUrl -and [string]::IsNullOrWhiteSpace($startUrl)) {
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
    $display = Redact-UrlForDisplay $startUrl
    Write-Host ("Start-URL (redacted): {0}  (Query/Fragment ausgeblendet)" -f $display)
} else {
    Write-Host "Start-URL wird interaktiv abgefragt (nicht als CLI-Arg)."
}

Write-Host ("Runner: {0}" -f (Join-Path $repoRoot 'tools/execute_smoketest.py'))
Write-Host ("Charter: {0}" -f $CharterFile)

& $python @cmdArgs
exit $LASTEXITCODE
