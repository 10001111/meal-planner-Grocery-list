@echo off
REM Installation script for Windows
REM This installs the Meal Planner application in development mode

echo ============================================
echo Meal Planner - Installation Script
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org
    pause
    exit /b 1
)

echo Python found. Installing application...
echo.

REM Install in development mode
python -m pip install --upgrade pip
python -m pip install -e .

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Installation completed successfully!
echo ============================================
echo.
echo You can now run the application using:
echo   - GUI mode: meal-planner-gui
echo   - CLI mode: meal-planner --help
echo.
echo To import sample recipes:
echo   meal-planner recipe import sample_recipes.json
echo.
pause
