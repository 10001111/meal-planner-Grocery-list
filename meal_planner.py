"""Meal plan generation logic."""

import random
from typing import List, Dict, Optional

from models import Recipe, PlannedMeal, MealPlan
from database import get_connection
from recipe_manager import get_all_recipes, get_recipe


def generate_meal_plan(
    days: int = 7,
    meals: List[str] = None,
    servings: int = 2,
    dietary_tags: Optional[List[str]] = None
) -> MealPlan:
    """
    Generate a randomized meal plan.

    Algorithm:
    1. Fetch all recipes, filter by constraints
    2. Group by meal type
    3. For each day and meal slot:
       - Select random recipe not used recently
       - If insufficient variety, allow repeats
    4. Return MealPlan object

    Args:
        days: Number of days to plan (1-14)
        meals: Which meals to include (default: ['breakfast', 'lunch', 'dinner'])
        servings: Servings per meal for grocery calculation
        dietary_tags: Required tags (e.g., ['vegetarian'])

    Returns:
        MealPlan object with planned meals

    Raises:
        ValueError: If invalid parameters or not enough recipes
    """
    if days < 1 or days > 14:
        raise ValueError("Days must be between 1 and 14")

    if servings < 1:
        raise ValueError("Servings must be at least 1")

    if meals is None:
        meals = ['breakfast', 'lunch', 'dinner']

    # Validate meal types
    valid_meals = {'breakfast', 'lunch', 'dinner', 'snack'}
    for meal in meals:
        if meal not in valid_meals:
            raise ValueError(f"Invalid meal type: {meal}")

    # Get all recipes with filters
    all_recipes = get_all_recipes(dietary_tags=dietary_tags)

    if not all_recipes:
        raise ValueError("No recipes available. Please add some recipes first.")

    # Group recipes by meal type
    recipes_by_type: Dict[str, List[Recipe]] = {}
    for meal_type in meals:
        recipes_by_type[meal_type] = [r for r in all_recipes if r.meal_type == meal_type]

        if not recipes_by_type[meal_type]:
            raise ValueError(f"No {meal_type} recipes available")

    # Generate meal plan
    planned_meals = []
    recent_recipes = []  # Track recently used recipes to avoid repetition

    for day in range(1, days + 1):
        for meal_type in meals:
            available_recipes = recipes_by_type[meal_type]

            # Try to avoid recipes used in the last 7 meals of this type
            max_lookback = min(7, len(available_recipes) - 1)
            recent_to_avoid = [r for r in recent_recipes[-max_lookback:] if r.meal_type == meal_type]

            # Get candidates (prefer recipes not recently used)
            candidates = [r for r in available_recipes if r not in recent_to_avoid]

            # If no candidates (too few recipes), use all available
            if not candidates:
                candidates = available_recipes

            # Select random recipe
            selected_recipe = random.choice(candidates)

            # Create planned meal
            planned_meal = PlannedMeal(
                day_number=day,
                meal_type=meal_type,
                recipe=selected_recipe,
                servings=servings
            )

            planned_meals.append(planned_meal)
            recent_recipes.append(selected_recipe)

    return MealPlan(meals=planned_meals, days=days)


def get_current_plan() -> Optional[MealPlan]:
    """
    Get the current meal plan from database.

    Returns:
        MealPlan object or None if no plan exists
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT day_number, meal_type, recipe_id, servings
        FROM current_meal_plan
        ORDER BY day_number, meal_type
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    planned_meals = []
    max_day = 0

    for row in rows:
        day_number, meal_type, recipe_id, servings = row
        max_day = max(max_day, day_number)

        # Get recipe details
        cursor = get_connection().cursor()
        cursor.execute("SELECT name FROM recipes WHERE id = ?", (recipe_id,))
        recipe_row = cursor.fetchone()
        cursor.connection.close()

        if recipe_row:
            recipe = get_recipe(recipe_row[0])
            if recipe:
                planned_meals.append(PlannedMeal(
                    day_number=day_number,
                    meal_type=meal_type,
                    recipe=recipe,
                    servings=servings
                ))

    return MealPlan(meals=planned_meals, days=max_day) if planned_meals else None


def save_meal_plan(plan: MealPlan) -> None:
    """
    Save meal plan to database (replaces current plan).

    Args:
        plan: MealPlan object to save
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Clear existing plan
        cursor.execute("DELETE FROM current_meal_plan")

        # Insert new plan
        for meal in plan.meals:
            cursor.execute("""
                INSERT INTO current_meal_plan (day_number, meal_type, recipe_id, servings)
                VALUES (?, ?, ?, ?)
            """, (meal.day_number, meal.meal_type, meal.recipe.id, meal.servings))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def clear_meal_plan() -> None:
    """Clear the current meal plan."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM current_meal_plan")
    conn.commit()
    conn.close()


def swap_meal(day: int, meal_type: str, new_recipe_name: str) -> bool:
    """
    Swap a specific meal in the current plan.

    Args:
        day: Day number (1-7)
        meal_type: Type of meal to swap
        new_recipe_name: Name of new recipe

    Returns:
        True if swapped successfully, False if meal not found

    Raises:
        ValueError: If recipe doesn't exist or wrong meal type
    """
    # Get the new recipe
    new_recipe = get_recipe(new_recipe_name)
    if not new_recipe:
        raise ValueError(f"Recipe '{new_recipe_name}' not found")

    if new_recipe.meal_type != meal_type:
        raise ValueError(f"Recipe '{new_recipe_name}' is a {new_recipe.meal_type} recipe, not {meal_type}")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Check if meal exists in plan
        cursor.execute("""
            SELECT servings FROM current_meal_plan
            WHERE day_number = ? AND meal_type = ?
        """, (day, meal_type))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return False

        servings = row[0]

        # Update the meal
        cursor.execute("""
            UPDATE current_meal_plan
            SET recipe_id = ?
            WHERE day_number = ? AND meal_type = ?
        """, (new_recipe.id, day, meal_type))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_swap_suggestions(meal_type: str, exclude: List[str] = None) -> List[Recipe]:
    """
    Get recipe suggestions for swapping, excluding already-used recipes.

    Args:
        meal_type: Type of meal
        exclude: List of recipe names to exclude

    Returns:
        List of suggested Recipe objects
    """
    all_recipes = get_all_recipes(meal_type=meal_type)

    if exclude:
        exclude_lower = [name.lower() for name in exclude]
        all_recipes = [r for r in all_recipes if r.name.lower() not in exclude_lower]

    return all_recipes


def get_recipes_in_plan() -> List[str]:
    """
    Get list of recipe names in the current meal plan.

    Returns:
        List of recipe names
    """
    plan = get_current_plan()
    if not plan:
        return []

    recipe_names = list(set(meal.recipe.name for meal in plan.meals))
    return recipe_names


def update_meal_servings(day: int, meal_type: str, new_servings: int) -> bool:
    """
    Update the servings for a specific meal in the plan.

    Args:
        day: Day number
        meal_type: Type of meal
        new_servings: New servings count

    Returns:
        True if updated, False if meal not found
    """
    if new_servings < 1:
        raise ValueError("Servings must be at least 1")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE current_meal_plan
        SET servings = ?
        WHERE day_number = ? AND meal_type = ?
    """, (new_servings, day, meal_type))

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return updated
