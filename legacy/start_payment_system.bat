@echo off
echo ========================================
echo   Starting Agentic Commerce Payment System
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Starting FastAPI backend on http://127.0.0.1:8000
echo.
start cmd /k "uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Opening frontend in browser...
echo.
start "" "http://127.0.0.1:8000"
start "" "http://127.0.0.1:8000/docs"

echo.
echo ========================================
echo   System is ready!
echo   - Backend: http://127.0.0.1:8000
echo   - API Docs: http://127.0.0.1:8000/docs
echo   - Frontend: Check your browser
echo ========================================
echo.
pause
