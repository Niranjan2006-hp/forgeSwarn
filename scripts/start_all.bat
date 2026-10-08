@echo off
echo ===================================================
echo Starting ForgeSwarm Autonomous Engineering Swarm
echo ===================================================
start "ForgeSwarm Backend (API & Swarm Engine)" cmd /k "%~dp0start_backend.bat"
timeout /t 3 /nobreak >nul
start "ForgeSwarm Frontend (Cyber Dashboard)" cmd /k "%~dp0start_frontend.bat"
echo ForgeSwarm services launched!
echo Open http://localhost:5173 to access the dashboard.
