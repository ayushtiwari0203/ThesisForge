@echo off
title ThesisForge AI — Multi-Agent Investment Committee
echo ========================================================
echo   Starting ThesisForge AI Full Stack System...
echo   - Multi-Agent Debate Engine (Research, Bull, Bear, Risk, Judge)
echo   - Web Application UI (Port 8000)
echo ========================================================

set PATH=C:\Users\91860\AppData\Local\Programs\Python\Python313;C:\Users\91860\AppData\Local\Programs\Python\Python313\Scripts;%PATH%

cd /d "%~dp0web-app"

:: Ensure seed data is ready
python -c "from database.repository import Repository; r = Repository(); exit(0 if len(r.list_assets()) > 0 else 1)" 2>nul
if %errorlevel% neq 0 (
    echo [1/3] Initializing sample filings and database...
    python -m database.seed_data
)

:: Wait 1 second then open browser
echo [2/3] Opening browser at http://localhost:8000/ ...
start "" "http://localhost:8000/"

echo [3/3] Starting ThesisForge AI Server on Port 8000...
echo.
echo ========================================================
echo   ThesisForge AI is now running!
echo   Web Interface: http://localhost:8000/
echo   API Docs:      http://localhost:8000/docs
echo   Health Check:  http://localhost:8000/health
echo ========================================================
echo Keep this window open while using ThesisForge AI.
echo Close this window or press Ctrl+C to stop.
echo.

python run_app.py
pause
