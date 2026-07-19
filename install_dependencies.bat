@echo off
REM SNOP Data Generator - Dependency Installer (Windows)

echo =========================================
echo SNOP Data Generator - Installing Dependencies
echo =========================================
echo.

REM Check Python version
echo [1/4] Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Install Python 3.9+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version

REM Check pip
echo.
echo [2/4] Checking pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip not found. Install pip first.
    pause
    exit /b 1
)

REM Install Python packages
echo.
echo [3/4] Installing Python packages from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Check Kaggle API setup
echo.
echo [4/4] Checking Kaggle API setup...
set KAGGLE_CONFIG=%USERPROFILE%\.kaggle\kaggle.json

if exist "%KAGGLE_CONFIG%" (
    echo ✓ Kaggle API credentials found at %KAGGLE_CONFIG%
) else (
    echo ⚠️  WARNING: Kaggle API credentials not found
    echo.
    echo    Phase 4 (Historical Data) requires Kaggle API.
    echo    To set up:
    echo    1. Go to https://www.kaggle.com/account
    echo    2. Click 'Create New API Token'
    echo    3. Move downloaded kaggle.json to: %KAGGLE_CONFIG%
    echo.
    echo    You can skip this if you won't run Phase 4.
)

echo.
echo =========================================
echo ✓ Installation Complete
echo =========================================
echo.
echo Next steps:
echo   1. Copy .env.example to .env
echo   2. Edit .env with your PostgreSQL credentials
echo   3. Run: run_all_phases.bat
echo.
pause
