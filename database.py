"""Database connection and query utilities."""

import sqlite3
from pathlib import Path
from typing import Optional, List, Any, Tuple
import os
import sys

# Determine data directory based on whether app is frozen (packaged)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    if sys.platform == 'win32':
        DATA_DIR = Path(os.environ.get('APPDATA', Path.home())) / 'MealPlanner'
    elif sys.platform == 'darwin':
        DATA_DIR = Path.home() / 'Library' / 'Application Support' / 'MealPlanner'
    else:
        DATA_DIR = Path.home() / '.local' / 'share' / 'mealplanner'
else:
    # Running as script - use local data folder
    DATA_DIR = Path(__file__).parent / "data"

DATABASE_PATH = DATA_DIR / "meal_planner.db"


def get_connection() -> sqlite3.Connection:
    """
    Get database connection with row factory.

    Returns:
        sqlite3.Connection: Database connection with row factory enabled
    """
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def load_default_recipes() -> None:
    """Load default everyday recipes if database is empty."""
    from models import Recipe, RecipeIngredient
    from recipe_manager import add_recipe, get_all_recipes

    # Check if there are already recipes
    existing_recipes = get_all_recipes()
    if existing_recipes:
        return  # Don't add defaults if recipes already exist

    default_recipes = [
        # Breakfast Recipes
        Recipe(
            name="Scrambled Eggs with Toast",
            meal_type="breakfast",
            servings=2,
            prep_time=5,
            cook_time=10,
            cuisine="American",
            ingredients=[
                RecipeIngredient(ingredient_name="eggs", quantity=4, unit="whole"),
                RecipeIngredient(ingredient_name="butter", quantity=1, unit="tbsp"),
                RecipeIngredient(ingredient_name="bread", quantity=4, unit="slices"),
                RecipeIngredient(ingredient_name="milk", quantity=2, unit="tbsp"),
                RecipeIngredient(ingredient_name="salt", quantity=0.25, unit="tsp"),
                RecipeIngredient(ingredient_name="black pepper", quantity=0.125, unit="tsp"),
            ],
            instructions="1. Beat eggs with milk, salt, and pepper.\n2. Melt butter in pan over medium heat.\n3. Pour in eggs and gently stir until cooked.\n4. Toast bread and serve with eggs.",
            dietary_tags=["vegetarian"]
        ),
        Recipe(
            name="Oatmeal with Berries",
            meal_type="breakfast",
            servings=2,
            prep_time=5,
            cook_time=10,
            cuisine="American",
            ingredients=[
                RecipeIngredient(ingredient_name="rolled oats", quantity=1, unit="cup"),
                RecipeIngredient(ingredient_name="water", quantity=2, unit="cups"),
                RecipeIngredient(ingredient_name="blueberries", quantity=0.5, unit="cup"),
                RecipeIngredient(ingredient_name="strawberries", quantity=0.5, unit="cup", preparation="sliced"),
                RecipeIngredient(ingredient_name="honey", quantity=2, unit="tbsp"),
                RecipeIngredient(ingredient_name="cinnamon", quantity=0.5, unit="tsp"),
            ],
            instructions="1. Bring water to boil in a pot.\n2. Add oats and reduce heat to medium.\n3. Cook for 5-7 minutes, stirring occasionally.\n4. Remove from heat and stir in cinnamon.\n5. Top with berries and drizzle with honey.",
            dietary_tags=["vegetarian", "vegan"]
        ),
        # Lunch Recipes
        Recipe(
            name="Grilled Cheese Sandwich",
            meal_type="lunch",
            servings=2,
            prep_time=5,
            cook_time=10,
            cuisine="American",
            ingredients=[
                RecipeIngredient(ingredient_name="bread", quantity=4, unit="slices"),
                RecipeIngredient(ingredient_name="cheddar cheese", quantity=4, unit="slices"),
                RecipeIngredient(ingredient_name="butter", quantity=2, unit="tbsp"),
            ],
            instructions="1. Butter one side of each bread slice.\n2. Place cheese between bread slices, butter side out.\n3. Heat skillet over medium heat.\n4. Cook sandwich until golden brown on each side and cheese is melted, about 3-4 minutes per side.",
            dietary_tags=["vegetarian"]
        ),
        Recipe(
            name="Chicken Caesar Salad",
            meal_type="lunch",
            servings=2,
            prep_time=15,
            cook_time=15,
            cuisine="American",
            ingredients=[
                RecipeIngredient(ingredient_name="chicken breast", quantity=1, unit="lb"),
                RecipeIngredient(ingredient_name="romaine lettuce", quantity=1, unit="head", preparation="chopped"),
                RecipeIngredient(ingredient_name="parmesan cheese", quantity=0.5, unit="cup", preparation="grated"),
                RecipeIngredient(ingredient_name="Caesar dressing", quantity=0.5, unit="cup"),
                RecipeIngredient(ingredient_name="croutons", quantity=1, unit="cup"),
                RecipeIngredient(ingredient_name="olive oil", quantity=1, unit="tbsp"),
            ],
            instructions="1. Season chicken with salt and pepper.\n2. Heat olive oil in pan and cook chicken 6-7 minutes per side.\n3. Let chicken rest 5 minutes, then slice.\n4. Toss lettuce with dressing and parmesan.\n5. Top with sliced chicken and croutons.",
            dietary_tags=[]
        ),
        # Dinner Recipes
        Recipe(
            name="Spaghetti with Marinara",
            meal_type="dinner",
            servings=4,
            prep_time=10,
            cook_time=25,
            cuisine="Italian",
            ingredients=[
                RecipeIngredient(ingredient_name="spaghetti", quantity=1, unit="lb"),
                RecipeIngredient(ingredient_name="crushed tomatoes", quantity=28, unit="oz"),
                RecipeIngredient(ingredient_name="garlic", quantity=4, unit="cloves", preparation="minced"),
                RecipeIngredient(ingredient_name="olive oil", quantity=3, unit="tbsp"),
                RecipeIngredient(ingredient_name="basil", quantity=0.25, unit="cup", preparation="fresh, chopped"),
                RecipeIngredient(ingredient_name="salt", quantity=1, unit="tsp"),
                RecipeIngredient(ingredient_name="black pepper", quantity=0.5, unit="tsp"),
            ],
            instructions="1. Cook spaghetti according to package directions.\n2. Heat olive oil in large pan over medium heat.\n3. Add garlic and cook until fragrant, about 1 minute.\n4. Add crushed tomatoes, salt, pepper, and half the basil.\n5. Simmer for 15 minutes.\n6. Toss pasta with sauce and garnish with remaining basil.",
            dietary_tags=["vegetarian", "vegan"]
        ),
        Recipe(
            name="Baked Chicken with Vegetables",
            meal_type="dinner",
            servings=4,
            prep_time=15,
            cook_time=40,
            cuisine="American",
            ingredients=[
                RecipeIngredient(ingredient_name="chicken thighs", quantity=2, unit="lbs"),
                RecipeIngredient(ingredient_name="potatoes", quantity=1, unit="lb", preparation="cubed"),
                RecipeIngredient(ingredient_name="carrots", quantity=3, unit="whole", preparation="sliced"),
                RecipeIngredient(ingredient_name="onion", quantity=1, unit="whole", preparation="quartered"),
                RecipeIngredient(ingredient_name="olive oil", quantity=3, unit="tbsp"),
                RecipeIngredient(ingredient_name="garlic powder", quantity=1, unit="tsp"),
                RecipeIngredient(ingredient_name="paprika", quantity=1, unit="tsp"),
                RecipeIngredient(ingredient_name="salt", quantity=1, unit="tsp"),
                RecipeIngredient(ingredient_name="black pepper", quantity=0.5, unit="tsp"),
            ],
            instructions="1. Preheat oven to 425°F (220°C).\n2. Arrange vegetables in large baking dish.\n3. Drizzle with 2 tbsp olive oil and season with salt and pepper.\n4. Place chicken on top of vegetables.\n5. Rub chicken with remaining oil and season with garlic powder, paprika, salt, and pepper.\n6. Bake for 35-40 minutes until chicken reaches 165°F internal temperature.",
            dietary_tags=[]
        ),
        # Snack Recipes
        Recipe(
            name="Fruit Smoothie",
            meal_type="snack",
            servings=2,
            prep_time=5,
            cook_time=0,
            cuisine="American",
            ingredients=[
                RecipeIngredient(ingredient_name="banana", quantity=1, unit="whole"),
                RecipeIngredient(ingredient_name="strawberries", quantity=1, unit="cup"),
                RecipeIngredient(ingredient_name="yogurt", quantity=1, unit="cup"),
                RecipeIngredient(ingredient_name="milk", quantity=0.5, unit="cup"),
                RecipeIngredient(ingredient_name="honey", quantity=1, unit="tbsp"),
            ],
            instructions="1. Add all ingredients to blender.\n2. Blend until smooth.\n3. Pour into glasses and serve immediately.",
            dietary_tags=["vegetarian"]
        ),
        Recipe(
            name="Hummus with Veggies",
            meal_type="snack",
            servings=4,
            prep_time=10,
            cook_time=0,
            cuisine="Mediterranean",
            ingredients=[
                RecipeIngredient(ingredient_name="chickpeas", quantity=15, unit="oz", preparation="drained"),
                RecipeIngredient(ingredient_name="tahini", quantity=0.25, unit="cup"),
                RecipeIngredient(ingredient_name="lemon juice", quantity=3, unit="tbsp"),
                RecipeIngredient(ingredient_name="garlic", quantity=2, unit="cloves"),
                RecipeIngredient(ingredient_name="olive oil", quantity=2, unit="tbsp"),
                RecipeIngredient(ingredient_name="carrots", quantity=2, unit="whole", preparation="cut into sticks"),
                RecipeIngredient(ingredient_name="celery", quantity=3, unit="stalks", preparation="cut into sticks"),
            ],
            instructions="1. In food processor, combine chickpeas, tahini, lemon juice, garlic, and olive oil.\n2. Blend until smooth, adding water if needed.\n3. Transfer to serving bowl.\n4. Serve with carrot and celery sticks.",
            dietary_tags=["vegetarian", "vegan"]
        ),
    ]

    # Add each default recipe
    for recipe in default_recipes:
        try:
            add_recipe(recipe)
        except Exception as e:
            print(f"Warning: Could not add default recipe '{recipe.name}': {e}")


def initialize_database() -> None:
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create recipes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
            prep_time INTEGER DEFAULT 0,
            cook_time INTEGER DEFAULT 0,
            servings INTEGER NOT NULL DEFAULT 4,
            cuisine TEXT DEFAULT '',
            instructions TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create ingredients table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT DEFAULT 'Other'
        )
    """)

    # Create recipe_ingredients junction table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            preparation TEXT DEFAULT '',
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
        )
    """)

    # Create pantry table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pantry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id),
            UNIQUE(ingredient_id, unit)
        )
    """)

    # Create current_meal_plan table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS current_meal_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_number INTEGER NOT NULL CHECK(day_number BETWEEN 1 AND 7),
            meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
            recipe_id INTEGER NOT NULL,
            servings INTEGER NOT NULL DEFAULT 2,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id),
            UNIQUE(day_number, meal_type)
        )
    """)

    # Create dietary_tags table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dietary_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
            UNIQUE(recipe_id, tag)
        )
    """)

    # Create indexes for performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_recipe_meal_type
        ON recipes(meal_type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe
        ON recipe_ingredients(recipe_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pantry_ingredient
        ON pantry(ingredient_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_dietary_tags_recipe
        ON dietary_tags(recipe_id)
    """)

    conn.commit()
    conn.close()

    # Load default recipes if database is empty
    load_default_recipes()


def execute_query(query: str, params: tuple = ()) -> List[sqlite3.Row]:
    """
    Execute SELECT query and return results.

    Args:
        query: SQL SELECT query
        params: Query parameters

    Returns:
        List of Row objects
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results


def execute_command(query: str, params: tuple = ()) -> int:
    """
    Execute INSERT/UPDATE/DELETE and return affected rows or last ID.

    Args:
        query: SQL command
        params: Query parameters

    Returns:
        Last inserted row ID for INSERT, affected rows for UPDATE/DELETE
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

    # Return lastrowid for INSERT, rowcount for UPDATE/DELETE
    result = cursor.lastrowid if cursor.lastrowid > 0 else cursor.rowcount
    conn.close()
    return result


def execute_many(query: str, params_list: List[tuple]) -> int:
    """
    Execute multiple commands with different parameters.

    Args:
        query: SQL command
        params_list: List of parameter tuples

    Returns:
        Number of affected rows
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany(query, params_list)
    conn.commit()
    result = cursor.rowcount
    conn.close()
    return result


def transaction(func):
    """
    Decorator for database transactions.
    Automatically commits on success and rolls back on error.
    """
    def wrapper(*args, **kwargs):
        conn = get_connection()
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    return wrapper
