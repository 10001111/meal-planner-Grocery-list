#!/bin/bash
# Build script for Unix-like systems (Linux/macOS)
# This script creates a standalone executable for the Meal Planner GUI application

set -e  # Exit on error

echo "============================================"
echo "Meal Planner - Build Script"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "Python found. Checking version..."
python3 --version

echo ""
echo "Installing required dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller

echo ""
echo "Cleaning previous builds..."
rm -rf build dist

echo ""
echo "Building executable with PyInstaller..."
python3 -m PyInstaller meal_planner_gui.spec

echo ""
echo "============================================"
echo "Build completed successfully!"
echo "============================================"
echo ""

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Application bundle: dist/MealPlanner.app"
    echo "Data will be stored in: ~/Library/Application Support/MealPlanner"
else
    echo "Executable: dist/MealPlanner"
    echo "Data will be stored in: ~/.local/share/mealplanner"
fi

echo ""
echo "You can now distribute the application in the dist folder."
echo ""
