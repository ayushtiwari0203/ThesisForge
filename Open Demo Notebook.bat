@echo off
title ThesisForge AI — Open Demo Notebook
echo ========================================================
echo   Launching ThesisForge AI Demo Notebook...
echo ========================================================

set PATH=C:\Users\91860\AppData\Local\Programs\Python\Python313;C:\Users\91860\AppData\Local\Programs\Python\Python313\Scripts;%PATH%

cd /d "%~dp0"

echo Opening notebooks/thesisforge_demo.ipynb in Jupyter...
jupyter notebook notebooks/thesisforge_demo.ipynb
pause
