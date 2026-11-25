@echo off
title ThesisForge AI Web Application
cd /d "%~dp0web-app"
echo Starting ThesisForge AI...
echo Web UI will be available at http://localhost:8000
python run_app.py
pause
