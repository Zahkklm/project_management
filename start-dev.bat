@echo off
echo Starting Project Management System...
echo.

echo [1/3] Starting backend services (PostgreSQL, API, LocalStack)...
start cmd /k "docker-compose up db app localstack"

timeout /t 10 /nobreak >nul

echo [2/3] Installing frontend dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
)

echo [3/3] Starting frontend development server...
start cmd /k "npm run dev"

echo.
echo ========================================
echo   Project Management System Started!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul
