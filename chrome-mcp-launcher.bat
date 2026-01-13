@echo off
REM Launcher für Chrome MCP mit erhöhten Rechten
REM Dieser Launcher startet das eigentliche Script mit Admin-Rechten wenn nötig

setlocal

REM Pfad zum Script
set "SCRIPT_PATH=%~dp0chrome-mcp-start.bat"

REM Prüfe ob bereits mit Admin-Rechten laufen
net.exe session 1>nul 2>&1
if %errorlevel% neq 0 (
    REM Starte mit Admin-Rechten
    powershell -Command "Start-Process '%SCRIPT_PATH%' -Verb RunAs" -Wait
) else (
    REM Bereits mit Admin-Rechten
    call "%SCRIPT_PATH%"
)
