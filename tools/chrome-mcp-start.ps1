# Chrome MCP Remote Debugging Server - robust starter

$chromeProfile = Join-Path $env:USERPROFILE ".cache\chrome-devtools-mcp"
$chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$debugPort = 9333

Write-Host "-----------------------------------------------------------" -ForegroundColor Cyan
Write-Host "  Chrome MCP Remote Debugging Server (robust)" -ForegroundColor Yellow
Write-Host "-----------------------------------------------------------" -ForegroundColor Cyan

function Test-PortOpen {
    param(
        [int]$Port = 9333,
        [string]$RemoteHost = '127.0.0.1'
    )
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $async = $tcp.BeginConnect($RemoteHost, $Port, $null, $null)
        if (-not $async.AsyncWaitHandle.WaitOne(500)) { # 500ms timeout
            $tcp.Close()
            return $false
        }
        $tcp.EndConnect($async)
        $tcp.Close()
        return $true
    } catch {
        return $false
    }
}

# Prüfe ob Chrome installiert ist
if (-not (Test-Path $chromeExe)) {
    Write-Host "ERROR: Chrome nicht gefunden unter: $chromeExe" -ForegroundColor Red
    exit 1
}

# Erstelle Profil-Verzeichnis falls nicht vorhanden
if (-not (Test-Path $chromeProfile)) {
    Write-Host "Erstelle Profil-Verzeichnis..." -ForegroundColor Green
    New-Item -ItemType Directory -Path $chromeProfile -Force | Out-Null
    Write-Host "Profil erstellt: $chromeProfile" -ForegroundColor Green
}

# Prüfe Schreibrechte
Write-Host "`nÜberprüfe Schreibrechte..." -ForegroundColor Cyan
try {
    [System.IO.File]::WriteAllText((Join-Path $chromeProfile 'test.tmp'), "test")
    Remove-Item (Join-Path $chromeProfile 'test.tmp') -Force
    Write-Host "Schreibrechte OK" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Keine Schreibrechte auf $chromeProfile" -ForegroundColor Red
    Write-Host "  Lösung: Führe PowerShell als Administrator aus" -ForegroundColor Yellow
    exit 1
}

# Wenn Port bereits offen ist, verwende bestehenden MCP
# Wenn Port bereits offen ist, verwende bestehenden MCP
if (Test-PortOpen -Port $debugPort) {
    Write-Host "Remote Debugging Port $debugPort ist bereits verfügbar." -ForegroundColor Green
    Write-Host "Verwende bestehenden MCP: http://localhost:$debugPort" -ForegroundColor Yellow
    exit 0
}

# Starte Chrome robust mit Start-Process
Write-Host "`nVersuche Chrome zu starten..." -ForegroundColor Green
Write-Host "   Port: $debugPort" -ForegroundColor Cyan
Write-Host "   Profil: $chromeProfile" -ForegroundColor Cyan
Write-Host "`n"

$chromeArgs = @(
    "--remote-debugging-port=$debugPort",
    "--user-data-dir=$chromeProfile",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-default-apps"
)

try {
    Start-Process -FilePath $chromeExe -ArgumentList $chromeArgs -WindowStyle Hidden | Out-Null
    Start-Sleep -Milliseconds 500
    # Warte kurz bis Port offen ist
    $retries = 10
    for ($i=0; $i -lt $retries; $i++) {
        if (Test-PortOpen -Port $debugPort) { break }
        Start-Sleep -Milliseconds 300
    }
    if (Test-PortOpen -Port $debugPort) {
        Write-Host "`nChrome wurde gestartet" -ForegroundColor Green
        Write-Host "Remote Debugging: http://localhost:$debugPort" -ForegroundColor Yellow
        Write-Host "-----------------------------------------------------------" -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host "ERROR: Chrome gestartet, aber Port $debugPort nicht erreichbar." -ForegroundColor Red
        Write-Host "Prüfe laufende Chrome-Instanzen oder starte mit sauberem Profil." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ERROR: Konnte Chrome nicht starten:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
