# Meal Planner & Grocery List Generator

A comprehensive Python application with both GUI and command-line interfaces that helps you plan weekly meals from your recipe collection and automatically generates consolidated grocery lists.

## Features

- **Modern GUI Interface**: Easy-to-use graphical interface built with tkinter
- **Recipe Management**: Store and organize your personal recipe collection
- **Meal Planning**: Generate weekly meal plans with customizable options
- **Grocery Lists**: Automatically consolidate ingredients from your meal plan
- **Pantry Tracking**: Track what you have to avoid buying duplicates
- **Smart Consolidation**: Intelligently combines ingredients and converts units
- **Multiple Export Formats**: Export grocery lists as text, markdown, or JSON
- **Standalone Executable**: Build downloadable applications for Windows, macOS, and Linux
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Requirements

- Python 3.9 or higher
- No external dependencies for core functionality (uses Python standard library only)
- PyInstaller (optional, for building standalone executables)

### Quick Start

See [QUICKSTART.md](QUICKSTART.md) for the fastest way to get started!

### Option 1: Run Directly (GUI Mode - Recommended)

**Windows:**
```cmd
python gui_app.py
```

**macOS/Linux:**
```bash
python3 gui_app.py
```

### Option 2: Install as Package

**Windows:**
```cmd
install.bat
```

**macOS/Linux:**
```bash
chmod +x install.sh
./install.sh
```

After installation, you can run:
```bash
meal-planner-gui  # Start GUI
meal-planner --help  # Use CLI
```

### Option 3: Build Standalone Executable

Create a distributable application that doesn't require Python:

**Windows:**
```cmd
build.bat
```
The executable will be created in `dist\MealPlanner.exe`

**macOS/Linux:**
```bash
chmod +x build.sh
./build.sh
```
- macOS: Application bundle in `dist/MealPlanner.app`
- Linux: Executable in `dist/MealPlanner`

## Quick Start

### Using the GUI (Graphical Interface)

1. **Start the GUI**: Run `python gui_app.py` (or `meal-planner-gui` if installed)

2. **Import Sample Recipes**:
   - Go to the "Recipes" tab
   - Click "Import JSON"
   - Select `sample_recipes.json`

3. **Generate Meal Plan**:
   - Go to the "Meal Plan" tab
   - Set number of days and servings
   - Choose which meals to include
   - Click "Generate Plan"

4. **Create Grocery List**:
   - Go to the "Grocery List" tab
   - Click "Generate List"
   - Export to your preferred format (TXT, Markdown, or JSON)

5. **Manage Pantry**:
   - Go to the "Pantry" tab
   - Add items you already have at home

### Using the Command Line Interface

### 1. Import Sample Recipes

Get started quickly by importing the included sample recipes:

```bash
python main.py recipe import sample_recipes.json
```

This will add 12 sample recipes (breakfast, lunch, and dinner options).

### 2. View Your Recipes

```bash
python main.py recipe list
```

### 3. Generate a Meal Plan

```bash
python main.py plan generate --days 7 --servings 2
```

### 4. View Your Meal Plan

```bash
python main.py plan view
```

### 5. Generate a Grocery List

```bash
python main.py grocery generate
```

### 6. Export Your Grocery List

```bash
python main.py grocery export --format txt --output shopping_list.txt
```

## Usage Guide

### Recipe Management

#### Add a Recipe (Interactive)

```bash
python main.py recipe add
```

This will prompt you interactively for:
- Recipe name
- Meal type (breakfast, lunch, dinner, snack)
- Prep and cook time
- Servings
- Cuisine
- Dietary tags
- Ingredients (with quantities and units)
- Instructions

#### List All Recipes

```bash
# List all recipes
python main.py recipe list

# Filter by meal type
python main.py recipe list --meal-type dinner
```

#### View Recipe Details

```bash
python main.py recipe view "Chicken Stir Fry"
```

#### Delete a Recipe

```bash
python main.py recipe delete "Recipe Name"

# Skip confirmation prompt
python main.py recipe delete "Recipe Name" -y
```

#### Import Recipes from JSON

```bash
python main.py recipe import recipes.json
```

JSON format:
```json
{
  "recipes": [
    {
      "name": "Recipe Name",
      "meal_type": "dinner",
      "prep_time": 10,
      "cook_time": 20,
      "servings": 4,
      "cuisine": "Italian",
      "dietary_tags": ["vegetarian"],
      "ingredients": [
        {"item": "pasta", "quantity": 1, "unit": "lb"},
        {"item": "tomato sauce", "quantity": 2, "unit": "cup"}
      ],
      "instructions": "Cook pasta. Add sauce. Serve."
    }
  ]
}
```

#### Export Recipes to JSON

```bash
# Export all recipes
python main.py recipe export --output my_recipes.json

# Export only dinner recipes
python main.py recipe export --meal-type dinner --output dinners.json
```

### Meal Planning

#### Generate a Meal Plan

```bash
# Generate 7-day plan with 2 servings per meal
python main.py plan generate --days 7 --servings 2

# Generate 5-day plan, lunch and dinner only
python main.py plan generate --days 5 --no-breakfast

# Generate 3-day plan, all meals, 4 servings each
python main.py plan generate --days 3 --servings 4
```

Options:
- `--days N`: Number of days to plan (1-14, default: 7)
- `--servings N`: Servings per meal (default: 2)
- `--no-breakfast`: Exclude breakfast from plan
- `--no-lunch`: Exclude lunch from plan
- `--no-dinner`: Exclude dinner from plan

#### View Current Meal Plan

```bash
python main.py plan view
```

#### Swap a Meal

```bash
# Interactive swap (shows suggestions)
python main.py plan swap 3 dinner

# Direct swap to specific recipe
python main.py plan swap 3 dinner "Pasta Primavera"
```

#### Clear Meal Plan

```bash
python main.py plan clear

# Skip confirmation
python main.py plan clear -y
```

### Grocery Lists

#### Generate Grocery List

```bash
# Generate with pantry deduction (default)
python main.py grocery generate

# Generate without pantry deduction
python main.py grocery generate --no-pantry
```

The grocery list will:
- Consolidate all ingredients from your meal plan
- Combine same ingredients (e.g., multiple recipes needing onions)
- Convert units when possible (e.g., combine 2 cups + 16 oz)
- Group items by store category
- Deduct items from your pantry (if enabled)

#### Export Grocery List

```bash
# Export as plain text
python main.py grocery export --format txt --output shopping.txt

# Export as markdown with checkboxes
python main.py grocery export --format md --output shopping.md

# Export as JSON
python main.py grocery export --format json --output shopping.json
```

### Pantry Management

#### Add Items to Pantry

```bash
python main.py pantry add "olive oil" 500 ml
python main.py pantry add "rice" 2 lb
python main.py pantry add "onion" 3 whole
```

#### List Pantry Items

```bash
python main.py pantry list
```

#### Update Item Quantity

```bash
# Set to specific amount (replaces current quantity)
python main.py pantry update "olive oil" 250 ml
```

#### Remove Items from Pantry

```bash
# Remove specific unit
python main.py pantry remove "olive oil" --unit ml

# Remove all entries for ingredient
python main.py pantry remove "olive oil"
```

## Advanced Usage

### Ingredient Input Format

When adding recipes interactively, use these formats for ingredients:

```
2 cups flour
1 lb chicken breast, diced
3 cloves garlic, minced
1 onion
2 tablespoons olive oil
```

The parser will extract:
- Quantity (including fractions like "1/2")
- Unit (cups, tbsp, lb, whole, etc.)
- Ingredient name
- Preparation notes (after comma)

### Supported Units

**Volume**: cup, tbsp, tsp, ml, l, fl oz, pint, quart, gallon

**Weight**: g, kg, oz, lb

**Count**: whole, item, piece, clove, bunch, can, package, dozen, slice

The system automatically converts between compatible units when consolidating grocery lists.

### Dietary Tags

When adding recipes, you can specify dietary tags like:
- `vegetarian`
- `vegan`
- `gluten-free`
- `dairy-free`
- `keto`
- `paleo`

These can be used for filtering (future feature).

## File Structure

```
meal-planner-Grocery-list/
├── main.py                 # CLI entry point
├── database.py             # Database connection & schema
├── models.py               # Data classes
├── recipe_manager.py       # Recipe CRUD operations
├── meal_planner.py         # Meal plan generation
├── grocery_generator.py    # Grocery list creation
├── pantry_manager.py       # Pantry inventory
├── utils.py                # Unit conversion & helpers
├── data/
│   └── meal_planner.db     # SQLite database (auto-created)
├── exports/                # Generated export files
├── sample_recipes.json     # Sample recipe data
├── requirements.txt        # Dependencies (none for basic usage)
└── README.md              # This file
```

## Examples

### Complete Workflow

```bash
# 1. Import sample recipes
python main.py recipe import sample_recipes.json

# 2. Add items you have at home to pantry
python main.py pantry add "olive oil" 500 ml
python main.py pantry add "salt" 1 lb
python main.py pantry add "rice" 2 lb

# 3. Generate a week's meal plan for 2 people
python main.py plan generate --days 7 --servings 2

# 4. View your plan
python main.py plan view

# 5. Don't like Wednesday's dinner? Swap it
python main.py plan swap 3 dinner

# 6. Generate grocery list (pantry items deducted)
python main.py grocery generate

# 7. Export for shopping
python main.py grocery export --format txt --output my_list.txt

# 8. View the exported file
cat my_list.txt
```

### Adding Your Own Recipe

```bash
python main.py recipe add

# Follow the prompts:
Recipe Name: My Special Pasta
Meal Type: dinner
Prep Time (minutes): 10
Cook Time (minutes): 20
Servings: 4
Cuisine: Italian
Tags: vegetarian

# Add ingredients:
Ingredient 1: 1 lb pasta
Ingredient 2: 2 cups marinara sauce
Ingredient 3: 1 cup mozzarella cheese, shredded
Ingredient 4: 2 cloves garlic, minced
Ingredient 5: (press Enter when done)

# Add instructions:
> Cook pasta according to package directions.
> Heat marinara with garlic.
> Toss pasta with sauce and top with cheese.
> (press Enter when done)
```

## Tips and Best Practices

1. **Start with Sample Recipes**: Import `sample_recipes.json` to get started quickly
2. **Keep Pantry Updated**: Add staples to your pantry to get accurate grocery lists
3. **Use Descriptive Names**: Make recipe names clear and searchable
4. **Include Prep Notes**: Add preparation details in ingredients (e.g., "diced", "minced")
5. **Tag Dietary Restrictions**: Use tags to track vegetarian, vegan, etc.
6. **Export Regularly**: Back up your recipes with `recipe export`
7. **Adjust Servings**: Generate meal plans with appropriate servings for your household

## Troubleshooting

### "Recipe already exists" error

Each recipe must have a unique name. Delete the old recipe first or use a different name.

### Unit conversion errors

The system can only convert between compatible units (e.g., cups to ml, but not cups to pounds). If you get conversion errors, the grocery list will keep items separate.

### Empty grocery list

If your pantry has everything you need, the grocery list may be empty! Use `--no-pantry` to see the full list.

### Database issues

If you encounter database errors, the database file is located at `data/meal_planner.db`. You can delete it to start fresh (you'll lose all data).

## Data Storage

All data is stored locally in a SQLite database. The location depends on how you run the application:

**When running as script (development mode):**
- `data/meal_planner.db` in the project folder

**When running as standalone executable:**
- Windows: `%APPDATA%\MealPlanner\meal_planner.db`
- macOS: `~/Library/Application Support/MealPlanner/meal_planner.db`
- Linux: `~/.local/share/mealplanner/meal_planner.db`

The database contains:
- All your recipes
- Current meal plan
- Pantry inventory
- Ingredient catalog

**Backup**: Export your recipes regularly (using GUI "Export JSON" button or CLI `python main.py recipe export`) to back up your collection.

## Future Enhancements

Planned features for future versions:
- Recipe import from URLs
- Nutritional information tracking
- Cost/budget tracking
- Advanced recipe search and filtering
- Shopping list history
- Meal plan templates
- Recipe ratings and favorites
- Print support for meal plans and grocery lists
- Custom recipe categories
- Meal plan calendar view

## Contributing

This is an MVP (Minimum Viable Product). Contributions and suggestions are welcome!

## License

This project is provided as-is for personal use.

## Support

For issues or questions, please refer to the PRD and MVP specification documents included with this project.

---

**Version**: 2.0.0
**Python**: 3.9+
**Dependencies**: None for core functionality (standard library only)
**Optional**: PyInstaller 5.0+ for building executables

## What's New in Version 2.0

- Added modern GUI interface using tkinter
- Standalone executable builds for Windows, macOS, and Linux
- Improved data persistence with platform-specific storage
- Better error handling and user feedback
- Easy installation and build scripts
- Quick start guide for beginners
