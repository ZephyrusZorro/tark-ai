@echo off
setlocal
cd /d "%~dp0"

echo ===================================================================
echo   TARK.AI (तर्क) — Local-First Intelligent Code Auditor & AST Tutor
echo   Author: Faris Ruknuddin (@ZephyrusZorro)
echo ===================================================================
echo.
echo [1/2] Verifying Python 3 environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not found in your PATH.
    echo Please ensure Python 3.10+ is installed and accessible.
    pause
    exit /b 1
)

echo [2/2] Launching TarkAI Studio at http://127.0.0.1:8000 ...
start "" "http://127.0.0.1:8000"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
if errorlevel 1 (
    echo.
    echo [FALLBACK] Attempting direct backend/main.py launcher...
    python backend\main.py
)
pause
