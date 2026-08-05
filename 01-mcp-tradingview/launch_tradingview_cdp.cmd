@echo off
REM Doble clic para lanzar TradingView Desktop con depuracion remota (CDP :9222) para el MCP.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launch_tradingview_cdp.ps1"
echo.
pause
