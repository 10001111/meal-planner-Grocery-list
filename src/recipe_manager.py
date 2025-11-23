"""Recipe CRUD operations."""

import json
from typing import List, Optional, Dict
from pathlib import Path

from models import Recipe, RecipeIngredient, Ingredient
from database import execute_query, execute_command, get_connection
from utils import normalize_ingredient_name, get_ingredient_category


def _get_or_create_ingredient(conn, ingredient_name: str) -> int:
    """
    Get ingredient ID or create if it doesn't exist.

    Args:
        conn: Database connection
        ingredient_name: Name of the ingredient

    Returns:
        Ingredient ID
    """
    normalized_name = normalize_ingredient_name(ingredient_name)
    category = get_ingredient_category(normalized_name)

    cursor = conn.cursor()

    # Try to get existing ingredient
    cursor.execute("SELECT id FROM ingredients WHERE name = ?", (normalized_name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    # Create new ingredient
    cursor.execute(
        "INSERT INTO ingredients (name, category) VALUES (?, ?)",
        (normalized_name, category)
    )
    conn.commit()
    return cursor.lastrowid


def add_recipe(recipe: Recipe) -> int:
    """
    Add a new recipe to the database.

    Args:
        recipe: Recipe object with all details

    Returns:
        ID of created recipe

    Raises:
        ValueError: If recipe name already exists or recipe is invalid
    """
    if not recipe.name or not recipe.name.strip():
        raise ValueError("Recipe name cannot be empty")

    if not recipe.ingredients:
        raise ValueError("Recipe must have at least one ingredient")

    if recipe.servings <= 0:
        raise ValueError("Servings must be positive")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if recipe already exists
        cursor.execute("SELECT id FROM recipes WHERE LOWER(name) = LOWER(?)", (recipe.name,))
        if cursor.fetchone():
            raise ValueError(f"Recipe '{recipe.name}' already exists")

        # Insert recipe
        cursor.execute("""
            INSERT INTO recipes (name, meal_type, prep_time, cook_time, servings, cuisine, instructions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            recipe.name,
            recipe.meal_type,
            recipe.prep_time,
            recipe.cook_time,
            recipe.servings,
            recipe.cuisine,
            recipe.instructions
        ))
        recipe_id = cursor.lastrowid

        # Insert ingredients
        for ing in recipe.ingredients:
            ingredient_id = _get_or_create_ingredient(conn, ing.ingredient_name)

            cursor.execute("""
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation)
                VALUES (?, ?, ?, ?, ?)
            """, (recipe_id, ingredient_id, ing.quantity, ing.unit, ing.preparation))

        # Insert dietary tags
        for tag in recipe.dietary_tags:
            cursor.execute("""
                INSERT INTO dietary_tags (recipe_id, tag)
                VALUES (?, ?)
            """, (recipe_id, tag))

        conn.commit()
        return recipe_id

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_recipe(name: str) -> Optional[Recipe]:
    """
    Get recipe by name.

    Args:
        name: Recipe name

    Returns:
        Recipe object or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get recipe details
    cursor.execute("""
        SELECT id, name, meal_type, prep_time, cook_time, servings, cuisine, instructions, created_at, updated_at
        FROM recipes
        WHERE LOWER(name) = LOWER(?)
    """, (name,))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    recipe_id = row[0]

    # Get ingredients
    cursor.execute("""
        SELECT i.name, ri.quantity, ri.unit, ri.preparation, i.id
        FROM recipe_ingredients ri
        JOIN ingredients i ON ri.ingredient_id = i.id
        WHERE ri.recipe_id = ?
    """, (recipe_id,))

    ingredients = [
        RecipeIngredient(
            ingredient_name=row[0],
            quantity=row[1],
            unit=row[2],
            preparation=row[3],
            ingredient_id=row[4]
        )
        for row in cursor.fetchall()
    ]

    # Get dietary tags
    cursor.execute("""
        SELECT tag
        FROM dietary_tags
        WHERE recipe_id = ?
    """, (recipe_id,))

    dietary_tags = [row[0] for row in cursor.fetchall()]

    conn.close()

    return Recipe(
        id=row[0],
        name=row[1],
        meal_type=row[2],
        prep_time=row[3],
        cook_time=row[4],
        servings=row[5],
        cuisine=row[6],
        instructions=row[7],
        ingredients=ingredients,
        dietary_tags=dietary_tags,
        created_at=row[8],
        updated_at=row[9]
    )


def get_all_recipes(meal_type: Optional[str] = None, dietary_tags: Optional[List[str]] = None) -> List[Recipe]:
    """
    Get all recipes, optionally filtered by meal type and dietary tags.

    Args:
        meal_type: Filter by meal type (breakfast, lunch, dinner, snack)
        dietary_tags: Filter by dietary tags (must have ALL specified tags)

    Returns:
        List of Recipe objects
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Build query
    query = "SELECT DISTINCT r.name FROM recipes r"
    params = []

    if dietary_tags:
        query += " JOIN dietary_tags dt ON r.id = dt.recipe_id"

    where_clauses = []

    if meal_type:
        where_clauses.append("r.meal_type = ?")
        params.append(meal_type)

    if dietary_tags:
        placeholders = ','.join('?' * len(dietary_tags))
        where_clauses.append(f"dt.tag IN ({placeholders})")
        params.extend(dietary_tags)

        # Ensure recipe has ALL specified tags
        query += f" GROUP BY r.id HAVING COUNT(DISTINCT dt.tag) = {len(dietary_tags)}"

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    cursor.execute(query, params)
    recipe_names = [row[0] for row in cursor.fetchall()]

    conn.close()

    # Get full recipe details for each
    recipes = []
    for name in recipe_names:
        recipe = get_recipe(name)
        if recipe:
            recipes.append(recipe)

    return recipes


def update_recipe(name: str, updated_recipe: Recipe) -> bool:
    """
    Update existing recipe.

    Args:
        name: Current recipe name
        updated_recipe: Updated recipe data

    Returns:
        True if updated successfully, False if recipe not found

    Raises:
        ValueError: If updated recipe is invalid
    """
    if not updated_recipe.name or not updated_recipe.name.strip():
        raise ValueError("Recipe name cannot be empty")

    if not updated_recipe.ingredients:
        raise ValueError("Recipe must have at least one ingredient")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if original recipe exists
        cursor.execute("SELECT id FROM recipes WHERE LOWER(name) = LOWER(?)", (name,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        recipe_id = row[0]

        # If name is changing, check for conflicts
        if name.lower() != updated_recipe.name.lower():
            cursor.execute("SELECT id FROM recipes WHERE LOWER(name) = LOWER(?)", (updated_recipe.name,))
            if cursor.fetchone():
                raise ValueError(f"Recipe '{updated_recipe.name}' already exists")

        # Update recipe
        cursor.execute("""
            UPDATE recipes
            SET name = ?, meal_type = ?, prep_time = ?, cook_time = ?,
                servings = ?, cuisine = ?, instructions = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            updated_recipe.name,
            updated_recipe.meal_type,
            updated_recipe.prep_time,
            updated_recipe.cook_time,
            updated_recipe.servings,
            updated_recipe.cuisine,
            updated_recipe.instructions,
            recipe_id
        ))

        # Delete old ingredients and tags
        cursor.execute("DELETE FROM recipe_ingredients WHERE recipe_id = ?", (recipe_id,))
        cursor.execute("DELETE FROM dietary_tags WHERE recipe_id = ?", (recipe_id,))

        # Insert new ingredients
        for ing in updated_recipe.ingredients:
            ingredient_id = _get_or_create_ingredient(conn, ing.ingredient_name)

            cursor.execute("""
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, preparation)
                VALUES (?, ?, ?, ?, ?)
            """, (recipe_id, ingredient_id, ing.quantity, ing.unit, ing.preparation))

        # Insert new dietary tags
        for tag in updated_recipe.dietary_tags:
            cursor.execute("""
                INSERT INTO dietary_tags (recipe_id, tag)
                VALUES (?, ?)
            """, (recipe_id, tag))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_recipe(name: str) -> bool:
    """
    Delete recipe by name.

    Args:
        name: Recipe name

    Returns:
        True if deleted, False if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM recipes WHERE LOWER(name) = LOWER(?)", (name,))
    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()

    return deleted


def import_recipes_from_json(file_path: str) -> Dict[str, int]:
    """
    Import recipes from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Dict with 'success', 'failed', 'skipped' counts and 'errors' list
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, 'r') as f:
        data = json.load(f)

    recipes_data = data.get('recipes', [])
    if not recipes_data:
        raise ValueError("No recipes found in JSON file")

    results = {'success': 0, 'failed': 0, 'skipped': 0, 'errors': []}

    for recipe_data in recipes_data:
        try:
            # Check if recipe already exists
            if get_recipe(recipe_data['name']):
                results['skipped'] += 1
                results['errors'].append(f"Skipped '{recipe_data['name']}' - already exists")
                continue

            # Parse ingredients
            ingredients = []
            for ing_data in recipe_data.get('ingredients', []):
                ingredients.append(RecipeIngredient(
                    ingredient_name=ing_data['item'],
                    quantity=ing_data['quantity'],
                    unit=ing_data['unit'],
                    preparation=ing_data.get('preparation', '')
                ))

            # Create recipe
            recipe = Recipe(
                name=recipe_data['name'],
                meal_type=recipe_data['meal_type'],
                servings=recipe_data.get('servings', 4),
                ingredients=ingredients,
                prep_time=recipe_data.get('prep_time', 0),
                cook_time=recipe_data.get('cook_time', 0),
                cuisine=recipe_data.get('cuisine', ''),
                instructions=recipe_data.get('instructions', ''),
                dietary_tags=recipe_data.get('dietary_tags', [])
            )

            add_recipe(recipe)
            results['success'] += 1

        except Exception as e:
            results['failed'] += 1
            results['errors'].append(f"Failed '{recipe_data.get('name', 'unknown')}': {str(e)}")

    return results


def export_recipes_to_json(file_path: str, meal_type: Optional[str] = None) -> int:
    """
    Export recipes to JSON file.

    Args:
        file_path: Output file path
        meal_type: Optional filter by meal type

    Returns:
        Number of recipes exported
    """
    recipes = get_all_recipes(meal_type=meal_type)

    recipes_data = []
    for recipe in recipes:
        recipe_dict = {
            'name': recipe.name,
            'meal_type': recipe.meal_type,
            'prep_time': recipe.prep_time,
            'cook_time': recipe.cook_time,
            'servings': recipe.servings,
            'cuisine': recipe.cuisine,
            'dietary_tags': recipe.dietary_tags,
            'ingredients': [
                {
                    'item': ing.ingredient_name,
                    'quantity': ing.quantity,
                    'unit': ing.unit,
                    'preparation': ing.preparation
                }
                for ing in recipe.ingredients
            ],
            'instructions': recipe.instructions
        }
        recipes_data.append(recipe_dict)

    output = {'recipes': recipes_data}

    with open(file_path, 'w') as f:
        json.dump(output, f, indent=2)

    return len(recipes_data)
