# Chrome MCP Remote Debugging Server
# Port: 9333
# PowerShell Alternative zum Batch-Script

$chromeProfile = "$env:USERPROFILE\.cache\chrome-devtools-mcp"
$chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$debugPort = 9333

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Chrome MCP Remote Debugging Server" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Prüfe ob Chrome installiert ist
if (-not (Test-Path $chromeExe)) {
    Write-Host "✗ FEHLER: Chrome nicht gefunden unter:" $chromeExe -ForegroundColor Red
    exit 1
}

# Erstelle Profil-Verzeichnis falls nicht vorhanden
if (-not (Test-Path $chromeProfile)) {
    Write-Host "📁 Erstelle Profil-Verzeichnis..." -ForegroundColor Green
    New-Item -ItemType Directory -Path $chromeProfile -Force | Out-Null
    Write-Host "✓ Profil erstellt: $chromeProfile" -ForegroundColor Green
}

# Gebe Berechtigungen aus
Write-Host "`n🔍 Überprüfe Schreibrechte..." -ForegroundColor Cyan
try {
    [System.IO.File]::WriteAllText("$chromeProfile\test.tmp", "test")
    Remove-Item "$chromeProfile\test.tmp" -Force
    Write-Host "✓ Schreibrechte OK" -ForegroundColor Green
} catch {
    Write-Host "✗ FEHLER: Keine Schreibrechte auf $chromeProfile" -ForegroundColor Red
    Write-Host "  Lösung: Führe PowerShell als Administrator aus" -ForegroundColor Yellow
    exit 1
}

# Starte Chrome
Write-Host "`n🚀 Starte Chrome..." -ForegroundColor Green
Write-Host "   Port: $debugPort" -ForegroundColor Cyan
Write-Host "   Profil: $chromeProfile" -ForegroundColor Cyan
Write-Host "`n"

& $chromeExe `
    --remote-debugging-port=$debugPort `
    --user-data-dir="$chromeProfile" `
    --disable-extensions `
    --disable-plugins `
    --disable-default-apps

Write-Host "`n✓ Chrome wurde gestartet" -ForegroundColor Green
Write-Host "  Remote Debugging: http://localhost:$debugPort" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
