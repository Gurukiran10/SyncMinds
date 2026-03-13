@echo off
REM Meeting Intelligence Agent - Windows Launch Script

setlocal enabledelayedexpansion
set PROJECT_DIR=%~dp0
set BACKEND_DIR=%PROJECT_DIR%backend

echo.
echo ============================================================
echo Meeting Intelligence Agent - Local Launch
echo ============================================================
echo.

REM Check Python
echo [1] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found Python %PYTHON_VERSION%

REM Check FastAPI
echo.
echo [2] Checking FastAPI installation...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Installing FastAPI and dependencies...
    python -m pip install -q fastapi uvicorn sqlalchemy pydantic python-dotenv
    echo [OK] Dependencies installed
) else (
    echo [OK] FastAPI is installed
)

REM Setup environment
echo.
echo [3] Setting up environment...
if not exist "%BACKEND_DIR%\.env" (
    echo [WARN] Creating .env file...
    (
        echo # Application Settings
        echo APP_NAME=Meeting Intelligence Agent
        echo ENVIRONMENT=development
        echo DEBUG=True
        echo.
        echo # Security
        echo SECRET_KEY=dev-key-change-in-production-minimum-32-char
        echo JWT_SECRET_KEY=jwt-dev-key-change-in-production-32-char
        echo DATABASE_URL=sqlite:///./app.db
        echo ENVIRONMENT=development
        echo DEBUG=True
    ) > "%BACKEND_DIR%\.env"
    echo [OK] .env file created
) else (
    echo [OK] .env file exists
)

REM Setup database
echo.
echo [4] Initializing database...
if not exist "%BACKEND_DIR%\uploads" (
    mkdir "%BACKEND_DIR%\uploads"
)
echo [OK] Database setup complete

REM Start application
echo.
echo ============================================================
echo Starting application...
echo ============================================================
echo.
echo [INFO] Application will run on: http://localhost:8000
echo [INFO] API Docs: http://localhost:8000/docs
echo.
echo [INFO] Default credentials:
echo   Admin: admin@meetingintel.ai / admin123
echo   Demo: demo@meetingintel.ai / demo123
echo.
echo [INFO] Press Ctrl+C to stop the server
echo ============================================================
echo.

cd /d "%BACKEND_DIR%"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
