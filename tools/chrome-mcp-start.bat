@echo off
REM Chrome MCP Remote Debugging Server
REM Port: 9333
REM Erstellt: 13. Januar 2026

setlocal enabledelayedexpansion

REM Definiere Chrome Profil-Verzeichnis
set "CHROME_PROFILE=%USERPROFILE%\.cache\chrome-devtools-mcp"

REM Erstelle Verzeichnis falls nicht vorhanden
if not exist "%CHROME_PROFILE%" (
    mkdir "%CHROME_PROFILE%"
    echo [INFO] Profil-Verzeichnis erstellt: %CHROME_PROFILE%
)

REM Starte Chrome mit Remote Debugging Port
echo [INFO] Starte Chrome mit Remote Debugging Port 9333...
echo [INFO] Profil: %CHROME_PROFILE%

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
    --remote-debugging-port=9333 ^
    --user-data-dir="%CHROME_PROFILE%" ^
    --disable-extensions ^
    --disable-plugins

echo.
echo [OK] Chrome wurde gestartet
echo [INFO] Remote Debugging verfügbar unter: http://localhost:9333
echo.
timeout /t 3 /nobreak
