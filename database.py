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
