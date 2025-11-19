@echo off
REM Build script for Windows
REM This script creates a standalone executable for the Meal Planner GUI application

echo ============================================
echo Meal Planner - Build Script for Windows
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

echo Python found. Checking version...
python --version

echo.
echo Installing required dependencies...
python -m pip install --upgrade pip
python -m pip install pyinstaller

echo.
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building executable with PyInstaller...
pyinstaller meal_planner_gui.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build completed successfully!
echo ============================================
echo.
echo Executable location: dist\MealPlanner.exe
echo.
echo You can now distribute the executable in the dist folder.
echo The application will store data in: %%APPDATA%%\MealPlanner
echo.
pause
