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
    - Remote wird mit Token konfiguriert für sichere Push/Pull
    - Alte Token sollten regelmäßig regeneriert werden
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# Pfade
$WORKSPACE = "$env:USERPROFILE\Documents\AI_WorkDir"
$TOKEN_FILE = "$WORKSPACE\.secrets\github_token"
$EXAMPLE_FILE = "$WORKSPACE\.secrets\github_token.example"

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
$token = Get-Content $TOKEN_FILE -Raw -ErrorAction Stop
if ($token -match "github_pat_") {
    Write-Host "✅ Token geladen (github_pat_...)" -ForegroundColor Green
} else {
    Write-Host "❌ Token-Format ungültig! Muss mit 'github_pat_' starten" -ForegroundColor Red
    exit 1
}

# 3. Git Konfiguration
$user = "mivolkma"
$repo = "MCP-Chrome_VW_eCom"

Write-Host "`n⚙️  Konfiguriere Git Remote..." -ForegroundColor Cyan

cd $WORKSPACE

# Remote URL setzen
$remoteUrl = "https://$($user):$($token)@github.com/$($user)/$($repo).git"
git remote set-url origin $remoteUrl -ErrorAction SilentlyContinue
if ($LASTEXITCODE -ne 0) {
    git remote add origin $remoteUrl
}

# Verifiziere
$current = git remote get-url origin
if ($current -like "*github.com*") {
    Write-Host "✅ Remote konfiguriert: $repo" -ForegroundColor Green
} else {
    Write-Host "❌ Remote-Konfiguration fehlgeschlagen!" -ForegroundColor Red
    exit 1
}

# 4. Git Config Defaults
Write-Host "`n⚙️  Setze Git-Konfiguration..." -ForegroundColor Cyan
git config user.name "mivolkma" -ErrorAction SilentlyContinue
git config user.email "mivolkma@github.com" -ErrorAction SilentlyContinue
Write-Host "✅ Git Config aktualisiert" -ForegroundColor Green

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
        exit 1
    }
} else {
    Write-Host "`n✅ Skipped - Du kannst später manuell pushen:" -ForegroundColor Yellow
    Write-Host "   cd $WORKSPACE && git push origin master" -ForegroundColor White
}

Write-Host "`n" -ForegroundColor Cyan
Write-Host "🔒 Sicherheits-Tipps:" -ForegroundColor Yellow
Write-Host "   • Token wird NICHT in Git gespeichert" -ForegroundColor Gray
Write-Host "   • .secrets/github_token wird ignoriert" -ForegroundColor Gray
Write-Host "   • Token regelmäßig regenerieren" -ForegroundColor Gray
Write-Host "   • Alte Tokens auf GitHub löschen" -ForegroundColor Gray
Write-Host ""
