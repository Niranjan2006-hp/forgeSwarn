@echo off
echo ===================================================
echo Starting ForgeSwarm Backend on http://localhost:8002
echo ===================================================
cd /d "%~dp0\..\backend"
python start_server.py
pause
