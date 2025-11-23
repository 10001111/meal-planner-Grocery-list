@echo off
REM Build script for Meal Planner & Grocery List Generator
REM This creates a standalone Windows executable

echo ========================================
echo Building Meal Planner Executable
echo ========================================
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo.

REM Build executable
echo Building executable with PyInstaller...
python -m PyInstaller MealPlanner.spec --clean
echo.

REM Check if build was successful
if exist "dist\MealPlanner.exe" (
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable created at: dist\MealPlanner.exe
    echo.
    echo You can now:
    echo 1. Run the executable directly from dist\MealPlanner.exe
    echo 2. Copy the dist folder to distribute your app
    echo 3. Create an installer using the Inno Setup script
    echo.
) else (
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
