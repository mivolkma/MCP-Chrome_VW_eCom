#!/usr/bin/env powershell
<#
.SYNOPSIS
    GitHub Token Manager - Sichere Token-Verwaltung für Git Push/Pull
    
.DESCRIPTION
    Hilft dabei, GitHub Personal Access Tokens sicher zu speichern und zu verwalten.
    Liest Token aus .secrets/github_token und konfiguriert Git Remote.
    
.EXAMPLE
    .\setup-github-token.ps1
    
.NOTES
    - Token wird aus .secrets/github_token gelesen (wird ignoriert)
    - Remote-URL bleibt OHNE Token (kein Leak in .git/config)
    - Credentials werden im OS-Store gespeichert (Git Credential Manager)
    - Alte Token sollten regelmäßig regeneriert werden
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# Repo-Root (portabel)
$repoRoot = $null
try {
    $repoRoot = (git rev-parse --show-toplevel 2>$null)
} catch { }
if ([string]::IsNullOrWhiteSpace($repoRoot)) {
    $repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
}

$TOKEN_FILE = Join-Path $repoRoot ".secrets\github_token"
$EXAMPLE_FILE = Join-Path $repoRoot ".secrets\github_token.example"

Write-Host "`n🔐 GitHub Token Manager" -ForegroundColor Cyan
Write-Host "=" * 50

# 1. Prüfe ob Token-Datei existiert
if (-not (Test-Path $TOKEN_FILE)) {
    Write-Host "`n⚠️  Token-Datei nicht gefunden: $TOKEN_FILE" -ForegroundColor Yellow
    Write-Host "   Bitte erstelle eine .secrets/github_token Datei mit deinem Token!"
    Write-Host "`n📋 Template anschauen:" -ForegroundColor Green
    Write-Host "   cat $EXAMPLE_FILE"
    exit 1
}

# 2. Lese Token
$token = (Get-Content $TOKEN_FILE -Raw -ErrorAction Stop).Trim()
if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Host "❌ Token-Datei ist leer: $TOKEN_FILE" -ForegroundColor Red
    exit 1
}

# Token-Typen:
# - Fine-grained PAT: beginnt typischerweise mit 'github_pat_'
# - Classic PAT: beginnt typischerweise mit 'ghp_'
if ($token -like 'github_pat_*') {
    Write-Host "✅ Token geladen (Fine-grained PAT erkannt)" -ForegroundColor Green
} elseif ($token -like 'ghp_*') {
    Write-Host "✅ Token geladen (Classic PAT erkannt)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Token geladen (unbekanntes Prefix)." -ForegroundColor Yellow
    Write-Host "   Falls Push fehlschlägt: Prüfe, ob der Token gültig ist und Repo-Permissions hat (Fine-grained: Contents=Read+Write)." -ForegroundColor Gray
}

# 3. Git Konfiguration
$originUrl = $null
try {
    $originUrl = (git remote get-url origin 2>$null)
} catch { }

$repoOwner = "<GITHUB_USERNAME>"
$repoName = "<REPO_NAME>"
if (-not [string]::IsNullOrWhiteSpace($originUrl)) {
    # Unterstützt https://github.com/owner/repo(.git) und git@github.com:owner/repo(.git)
    if ($originUrl -match "github\.com[:/](?<owner>[^/]+)/(?<repo>[^/]+?)(?:\.git)?$") {
        $repoOwner = $Matches.owner
        $repoName = $Matches.repo
    }
}

$user = Read-Host "GitHub Username (für Credential Manager)" 
if ([string]::IsNullOrWhiteSpace($user)) {
    $user = $repoOwner
}

$repo = "$repoOwner/$repoName"

Write-Host "`n⚙️  Konfiguriere Git Remote..." -ForegroundColor Cyan

cd $repoRoot

# Remote URL ohne Token erzwingen (verhindert Token-Leaks in .git/config)
$safeRemoteUrl = "https://github.com/$($repoOwner)/$($repoName).git"
git remote set-url origin $safeRemoteUrl -ErrorAction SilentlyContinue
if ($LASTEXITCODE -ne 0) {
    git remote add origin $safeRemoteUrl
}

# Verifiziere
$current = git remote get-url origin
if ($current -eq $safeRemoteUrl -or $current -like "https://github.com/*") {
    Write-Host "✅ Remote konfiguriert: $repo" -ForegroundColor Green
} else {
    Write-Host "❌ Remote-Konfiguration fehlgeschlagen!" -ForegroundColor Red
    exit 1
}

# 4. Credentials sicher im OS-Store ablegen (Git Credential Manager)
Write-Host "`n🔐 Speichere GitHub Credentials im Credential Manager..." -ForegroundColor Cyan
if (Get-Command git-credential-manager-core -ErrorAction SilentlyContinue) {
    # Input-Format: key=value, Leerzeile am Ende
    $payload = @(
        "protocol=https",
        "host=github.com",
        "username=$user",
        "password=$token",
        ""
    ) -join "`n"

    $payload | git-credential-manager-core store | Out-Null
    Write-Host "✅ Credentials gespeichert (Remote bleibt ohne Token)" -ForegroundColor Green
} else {
    Write-Host "⚠️  git-credential-manager-core nicht gefunden." -ForegroundColor Yellow
    Write-Host "   Empfehlung: Git for Windows inkl. Credential Manager installieren oder beim ersten 'git push' den Token einmalig eingeben." -ForegroundColor Gray
}

# 5. Status
Write-Host "`n📊 Status:" -ForegroundColor Cyan
Write-Host "   Repository: $repo" -ForegroundColor White
Write-Host "   Branch: $(git rev-parse --abbrev-ref HEAD)" -ForegroundColor White
Write-Host "   Commits: $(git rev-list --count HEAD)" -ForegroundColor White

# 6. Push Option
Write-Host "`n🚀 Bereit zum Pushen?" -ForegroundColor Green
$response = Read-Host "   Jetzt git push origin master ausführen? (j/n)"

if ($response -eq "j" -or $response -eq "J") {
    Write-Host "`n📤 Pushing..." -ForegroundColor Cyan
    git push origin master
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Push erfolgreich!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Push fehlgeschlagen!" -ForegroundColor Red
        Write-Host "   Häufige Ursachen:" -ForegroundColor Yellow
        Write-Host "   • Fine-grained Token: Repository access falsch oder Permission fehlt (Contents: Read and write)." -ForegroundColor Gray
        Write-Host "   • Workflows: Push/Änderung von .github/workflows/*.yml erfordert extra Rechte (Classic: scope 'workflow' / Fine-grained: Actions=Read+Write)." -ForegroundColor Gray
        Write-Host "   • Branch protection / Required reviews verhindern Push." -ForegroundColor Gray
        Write-Host "   • Falscher GitHub Username im Credential Manager (ggf. Credentials löschen und neu setzen)." -ForegroundColor Gray
        exit 1
    }
} else {
    Write-Host "`n✅ Skipped - Du kannst später manuell pushen:" -ForegroundColor Yellow
    Write-Host "   cd $repoRoot && git push origin master" -ForegroundColor White
}

Write-Host "`n" -ForegroundColor Cyan
Write-Host "🔒 Sicherheits-Tipps:" -ForegroundColor Yellow
Write-Host "   • Token wird NICHT in Git gespeichert" -ForegroundColor Gray
Write-Host "   • .secrets/github_token wird ignoriert" -ForegroundColor Gray
Write-Host "   • Remote-URL bleibt ohne Token (kein Leak in .git/config)" -ForegroundColor Gray
Write-Host "   • Token regelmäßig regenerieren" -ForegroundColor Gray
Write-Host "   • Alte Tokens auf GitHub löschen" -ForegroundColor Gray
Write-Host ""
