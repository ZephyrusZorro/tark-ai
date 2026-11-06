@echo off
echo ===================================================================
echo   TARK.AI (तर्क) — Local-First Intelligent Code Auditor & AST Tutor
echo   Author: Faris Ruknuddin (@ZephyrusZorro)
echo ===================================================================
echo.
echo [1/2] Verifying Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.10+.
    pause
    exit /b 1
)

echo [2/2] Launching TarkAI server at http://localhost:8000 ...
start http://localhost:8000
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
