@echo off
REM Compatibility wrapper
REM The actual launcher scripts live in tools/.

call "%~dp0tools\chrome-mcp-start.bat" %*
