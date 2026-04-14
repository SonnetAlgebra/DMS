@echo off
echo Starting DMS Data Monitoring System...
echo ========================================

echo [1/2] Starting backend service...
start cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload"

timeout /t 3 /nobreak >nul

echo [2/2] Starting frontend service...
start cmd /k "cd frontend && bun run dev"

echo.
echo Services started!
echo - Frontend: http://localhost:5173
echo - API Docs: http://127.0.0.1:8000/docs
echo.
pause
