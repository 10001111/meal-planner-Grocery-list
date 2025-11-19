# Quick Start Guide - Meal Planner & Grocery List Generator

## Option 1: Run the GUI Application (Recommended for Most Users)

### Windows
1. Simply run the GUI application directly:
   ```cmd
   python gui_app.py
   ```

### macOS/Linux
1. Run the GUI application:
   ```bash
   python3 gui_app.py
   ```

## Option 2: Install and Use Command Line Interface

### Windows
1. Double-click `install.bat` or run in command prompt:
   ```cmd
   install.bat
   ```

2. After installation, use the CLI:
   ```cmd
   meal-planner recipe import sample_recipes.json
   meal-planner plan generate --days 7 --servings 2
   meal-planner grocery generate
   ```

### macOS/Linux
1. Make the script executable and run:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

2. After installation, use the CLI:
   ```bash
   meal-planner recipe import sample_recipes.json
   meal-planner plan generate --days 7 --servings 2
   meal-planner grocery generate
   ```

## Option 3: Build Standalone Executable (For Distribution)

### Windows
1. Double-click `build.bat` or run:
   ```cmd
   build.bat
   ```

2. Find the executable in `dist\MealPlanner.exe`
3. You can now copy and run this executable on any Windows computer without Python installed!

### macOS/Linux
1. Make the script executable and run:
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

2. Find the application in:
   - macOS: `dist/MealPlanner.app`
   - Linux: `dist/MealPlanner`

3. You can now distribute this application!

## First Steps After Running

1. **Import Sample Recipes**: Click on "Import JSON" in the Recipes tab and select `sample_recipes.json`

2. **Generate a Meal Plan**: Go to the "Meal Plan" tab, set your preferences, and click "Generate Plan"

3. **Create Grocery List**: Go to the "Grocery List" tab and click "Generate List"

4. **Manage Pantry**: Add items you already have in the "Pantry" tab

## Features Overview

### Recipes Tab
- View all your recipes
- Add new recipes with ingredients and instructions
- Filter by meal type
- Import/Export recipes as JSON

### Meal Plan Tab
- Generate weekly meal plans (1-14 days)
- Choose which meals to include (breakfast, lunch, dinner)
- Set servings per meal
- View your complete meal plan

### Grocery List Tab
- Generate consolidated shopping list from your meal plan
- Automatically deducts items from your pantry
- Export to TXT, Markdown, or JSON format

### Pantry Tab
- Track what ingredients you have at home
- Add/update/remove pantry items
- Organized by category

## Data Storage

- **When running as script**: Data is stored in the `data/` folder
- **When running as executable**:
  - Windows: `%APPDATA%\MealPlanner`
  - macOS: `~/Library/Application Support/MealPlanner`
  - Linux: `~/.local/share/mealplanner`

## Need Help?

See the full README.md for detailed documentation and advanced features.
