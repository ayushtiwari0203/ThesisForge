@echo off
title Push ThesisForge to GitHub
cd /d "%~dp0"
echo ========================================================
echo   Pushing ThesisForge AI to GitHub Repository
echo   Remote: https://github.com/ayushtiwari0203/ThesisForge
echo ========================================================
echo.
git push origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================================
    echo   [SUCCESS] Repository pushed successfully to GitHub!
    echo ========================================================
) else (
    echo ========================================================
    echo   [NOTICE] Authentication required.
    echo   Please sign in via the browser prompt if it appears.
    echo ========================================================
)
echo.
pause
