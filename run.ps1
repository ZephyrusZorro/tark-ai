Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  TARK.AI (तर्क) — Local-First Intelligent Code Auditor & AST Tutor" -ForegroundColor Cyan
Write-Host "  Author: Faris Ruknuddin (@ZephyrusZorro)" -ForegroundColor Yellow
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    pause
    exit 1
}

Write-Host "Launching TarkAI at http://localhost:8000 ..." -ForegroundColor Green
Start-Process "http://localhost:8000"

python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
