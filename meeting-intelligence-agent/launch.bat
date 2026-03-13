@echo off
REM Colors not available in basic batch, so we'll use simpler formatting

echo ================================
echo  Meeting Intelligence Agent
echo     Full Stack Launcher
echo ================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from python.org
    exit /b 1
)
echo [OK] Python found

REM Check npm (optional warning)
npm --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Node.js/npm not found. Install from nodejs.org
    echo Press any key to continue...
    pause
)

set PROJECT_ROOT=%cd%

if "%1"=="backend" goto backend
if "%1"=="frontend" goto frontend
if "%1"=="both" goto both
goto usage

:backend
echo.
echo Starting Backend Server...
cd /d "%PROJECT_ROOT%\backend"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /PID %%a /F
)
timeout /t 1 >nul
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
exit /b 0

:frontend
echo.
echo Starting Frontend Server...
cd /d "%PROJECT_ROOT%\frontend"
if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install npm packages
        exit /b 1
    )
)
call npm run dev
exit /b 0

:both
echo.
echo Starting both servers...
echo [WARNING] Open 2 separate command windows for proper operation
echo.
echo Terminal 1: launch.bat backend
echo Terminal 2: launch.bat frontend
echo.
pause
exit /b 0

:usage
echo Usage:
echo   launch.bat backend     - Start backend only
echo   launch.bat frontend    - Start frontend only
echo   launch.bat both        - Instructions for both
echo.
echo Quick Start:
echo   Terminal 1: cd backend ^&^& python -m uvicorn app.main:app --reload
echo   Terminal 2: cd frontend ^&^& npm install ^&^& npm run dev
exit /b 0
