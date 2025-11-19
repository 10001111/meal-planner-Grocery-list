#!/bin/bash
# Installation script for Unix-like systems (Linux/macOS)
# This installs the Meal Planner application in development mode

set -e  # Exit on error

echo "============================================"
echo "Meal Planner - Installation Script"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "Python found. Installing application..."
echo ""

# Install in development mode
python3 -m pip install --upgrade pip
python3 -m pip install -e .

echo ""
echo "============================================"
echo "Installation completed successfully!"
echo "============================================"
echo ""
echo "You can now run the application using:"
echo "  - GUI mode: meal-planner-gui"
echo "  - CLI mode: meal-planner --help"
echo ""
echo "To import sample recipes:"
echo "  meal-planner recipe import sample_recipes.json"
echo ""
