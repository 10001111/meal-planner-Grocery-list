#!/usr/bin/env python3
"""Main entry point with CLI interface."""

import argparse
import sys
from typing import List

from models import Recipe, RecipeIngredient, PantryItem
from database import initialize_database
from recipe_manager import (
    add_recipe, get_recipe, get_all_recipes, delete_recipe,
    update_recipe, import_recipes_from_json, export_recipes_to_json
)
from meal_planner import (
    generate_meal_plan, get_current_plan, save_meal_plan,
    swap_meal, get_swap_suggestions, clear_meal_plan
)
from grocery_generator import generate_grocery_list, export_grocery_list, get_grocery_summary
from pantry_manager import (
    add_pantry_item, get_pantry_items, update_pantry_quantity,
    remove_pantry_item, get_pantry_value_by_category
)
from utils import parse_quantity


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_section(text: str) -> None:
    """Print a section divider."""
    print(f"\n{text}")
    print("-" * len(text))


def print_success(text: str) -> None:
    """Print a success message."""
    print(f"\n✓ {text}")


def print_error(text: str) -> None:
    """Print an error message."""
    print(f"\n✗ Error: {text}", file=sys.stderr)


def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"\n⚠ Warning: {text}")


# ==================== Recipe Commands ====================

def cmd_recipe_add(args) -> None:
    """Interactive recipe addition."""
    print_header("Add New Recipe")

    try:
        # Get basic info
        name = input("Recipe Name: ").strip()
        if not name:
            print_error("Recipe name cannot be empty")
            return

        print("\nMeal Type Options: breakfast, lunch, dinner, snack")
        meal_type = input("Meal Type: ").strip().lower()
        if meal_type not in ['breakfast', 'lunch', 'dinner', 'snack']:
            print_error(f"Invalid meal type: {meal_type}")
            return

        prep_time = input("Prep Time (minutes) [0]: ").strip() or "0"
        cook_time = input("Cook Time (minutes) [0]: ").strip() or "0"
        servings = input("Servings [4]: ").strip() or "4"
        cuisine = input("Cuisine (optional): ").strip()

        # Dietary tags
        print("\nDietary Tags (comma-separated, e.g., vegetarian, gluten-free)")
        tags_input = input("Tags (optional): ").strip()
        dietary_tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []

        # Ingredients
        print("\nAdd ingredients (format: '2 cups flour' or '1 onion')")
        print("Enter blank line when done:")

        ingredients = []
        ing_count = 1
        while True:
            ing_input = input(f"  Ingredient {ing_count}: ").strip()
            if not ing_input:
                break

            try:
                from utils import parse_ingredient_string
                quantity, unit, ing_name = parse_ingredient_string(ing_input)

                # Check for preparation notes (after comma)
                preparation = ""
                if "," in ing_name:
                    parts = ing_name.split(",", 1)
                    ing_name = parts[0].strip()
                    preparation = parts[1].strip()

                ingredients.append(RecipeIngredient(
                    ingredient_name=ing_name,
                    quantity=quantity,
                    unit=unit,
                    preparation=preparation
                ))
                ing_count += 1

            except Exception as e:
                print_error(f"Could not parse ingredient: {e}")
                print("  Try format like: '2 cups flour' or '1 lb chicken breast, diced'")

        if not ingredients:
            print_error("Recipe must have at least one ingredient")
            return

        # Instructions
        print("\nInstructions (optional, enter blank line to finish):")
        instructions_lines = []
        while True:
            line = input("  > ").strip()
            if not line:
                break
            instructions_lines.append(line)

        instructions = "\n".join(instructions_lines)

        # Create recipe
        recipe = Recipe(
            name=name,
            meal_type=meal_type,
            servings=int(servings),
            ingredients=ingredients,
            prep_time=int(prep_time),
            cook_time=int(cook_time),
            cuisine=cuisine,
            instructions=instructions,
            dietary_tags=dietary_tags
        )

        recipe_id = add_recipe(recipe)
        print_success(f"Recipe '{name}' added successfully! (ID: {recipe_id})")

    except ValueError as e:
        print_error(str(e))
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print_error(f"Unexpected error: {e}")


def cmd_recipe_list(args) -> None:
    """List all recipes."""
    try:
        recipes = get_all_recipes(meal_type=args.meal_type)

        if not recipes:
            filter_msg = f" ({args.meal_type})" if args.meal_type else ""
            print(f"\nNo recipes found{filter_msg}.")
            return

        print_header(f"Your Recipes ({len(recipes)})")

        # Group by meal type
        by_type = {}
        for recipe in recipes:
            if recipe.meal_type not in by_type:
                by_type[recipe.meal_type] = []
            by_type[recipe.meal_type].append(recipe)

        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            if meal_type in by_type:
                print_section(meal_type.upper())
                for recipe in sorted(by_type[meal_type], key=lambda r: r.name):
                    tags = f" [{', '.join(recipe.dietary_tags)}]" if recipe.dietary_tags else ""
                    print(f"  • {recipe.name} ({recipe.total_time()} min){tags}")

    except Exception as e:
        print_error(f"Failed to list recipes: {e}")


def cmd_recipe_view(args) -> None:
    """View recipe details."""
    try:
        recipe = get_recipe(args.name)

        if not recipe:
            print_error(f"Recipe '{args.name}' not found")
            return

        print_header(recipe.name)

        print(f"\nMeal Type: {recipe.meal_type.capitalize()}")
        print(f"Servings: {recipe.servings}")
        print(f"Prep Time: {recipe.prep_time} min")
        print(f"Cook Time: {recipe.cook_time} min")
        print(f"Total Time: {recipe.total_time()} min")

        if recipe.cuisine:
            print(f"Cuisine: {recipe.cuisine}")

        if recipe.dietary_tags:
            print(f"Tags: {', '.join(recipe.dietary_tags)}")

        print_section("Ingredients")
        for ing in recipe.ingredients:
            from utils import format_quantity
            qty = format_quantity(ing.quantity)
            prep = f", {ing.preparation}" if ing.preparation else ""
            print(f"  • {qty} {ing.unit} {ing.ingredient_name}{prep}")

        if recipe.instructions:
            print_section("Instructions")
            for line in recipe.instructions.split('\n'):
                print(f"  {line}")

    except Exception as e:
        print_error(f"Failed to view recipe: {e}")


def cmd_recipe_delete(args) -> None:
    """Delete a recipe."""
    try:
        # Confirm deletion
        if not args.yes:
            confirm = input(f"Delete recipe '{args.name}'? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Cancelled.")
                return

        if delete_recipe(args.name):
            print_success(f"Recipe '{args.name}' deleted")
        else:
            print_error(f"Recipe '{args.name}' not found")

    except Exception as e:
        print_error(f"Failed to delete recipe: {e}")


def cmd_recipe_import(args) -> None:
    """Import recipes from JSON."""
    try:
        print(f"Importing recipes from {args.file}...")

        results = import_recipes_from_json(args.file)

        print_header("Import Results")
        print(f"  Success: {results['success']}")
        print(f"  Skipped: {results['skipped']}")
        print(f"  Failed:  {results['failed']}")

        if results['errors']:
            print_section("Details")
            for error in results['errors']:
                print(f"  {error}")

    except FileNotFoundError:
        print_error(f"File not found: {args.file}")
    except Exception as e:
        print_error(f"Import failed: {e}")


def cmd_recipe_export(args) -> None:
    """Export recipes to JSON."""
    try:
        count = export_recipes_to_json(args.output, meal_type=args.meal_type)
        print_success(f"Exported {count} recipes to {args.output}")

    except Exception as e:
        print_error(f"Export failed: {e}")


# ==================== Plan Commands ====================

def cmd_plan_generate(args) -> None:
    """Generate meal plan."""
    try:
        print("Generating meal plan...")

        # Build meals list
        meals = []
        if not args.no_breakfast:
            meals.append('breakfast')
        if not args.no_lunch:
            meals.append('lunch')
        if not args.no_dinner:
            meals.append('dinner')

        if not meals:
            print_error("At least one meal type must be selected")
            return

        # Generate plan
        plan = generate_meal_plan(
            days=args.days,
            meals=meals,
            servings=args.servings
        )

        # Save plan
        save_meal_plan(plan)

        # Display plan
        _display_meal_plan(plan)

        print_success(f"Meal plan generated and saved!")

    except ValueError as e:
        print_error(str(e))
    except Exception as e:
        print_error(f"Failed to generate plan: {e}")


def cmd_plan_view(args) -> None:
    """View current meal plan."""
    try:
        plan = get_current_plan()

        if not plan:
            print("No meal plan found. Generate one with: python main.py plan generate")
            return

        _display_meal_plan(plan)

    except Exception as e:
        print_error(f"Failed to view plan: {e}")


def _display_meal_plan(plan) -> None:
    """Display a meal plan."""
    print_header(f"Meal Plan ({plan.days} days)")

    for day in range(1, plan.days + 1):
        meals = plan.get_meals_for_day(day)
        if not meals:
            continue

        day_name = meals[0].day_name() if meals else f"Day {day}"
        print_section(day_name)

        meal_icons = {
            'breakfast': '🍳',
            'lunch': '🥗',
            'dinner': '🍽️',
            'snack': '🍪'
        }

        for meal in sorted(meals, key=lambda m: ['breakfast', 'lunch', 'dinner', 'snack'].index(m.meal_type)):
            icon = meal_icons.get(meal.meal_type, '•')
            print(f"  {icon} {meal.meal_type.capitalize()}: {meal.recipe.name} ({meal.recipe.total_time()} min, {meal.servings} servings)")


def cmd_plan_swap(args) -> None:
    """Swap a meal in the plan."""
    try:
        # Get current plan to show context
        plan = get_current_plan()
        if not plan:
            print_error("No meal plan found. Generate one first.")
            return

        # Show current meal
        current_meals = [m for m in plan.meals if m.day_number == args.day and m.meal_type == args.meal_type]
        if not current_meals:
            print_error(f"No {args.meal_type} found for day {args.day}")
            return

        current_meal = current_meals[0]
        print(f"\nCurrent {args.meal_type} for {current_meal.day_name()}: {current_meal.recipe.name}")

        # Get suggestions
        used_recipes = [m.recipe.name for m in plan.meals]
        suggestions = get_swap_suggestions(args.meal_type, exclude=used_recipes)

        if not suggestions:
            print_warning("No other recipes available for swapping")
            return

        print_section("Available Alternatives")
        for i, recipe in enumerate(suggestions[:10], 1):
            print(f"  {i}. {recipe.name} ({recipe.total_time()} min)")

        # Get user choice
        if args.recipe:
            new_recipe_name = args.recipe
        else:
            choice = input("\nEnter recipe name or number: ").strip()

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(suggestions):
                    new_recipe_name = suggestions[idx].name
                else:
                    print_error("Invalid selection")
                    return
            else:
                new_recipe_name = choice

        # Perform swap
        if swap_meal(args.day, args.meal_type, new_recipe_name):
            print_success(f"Swapped to '{new_recipe_name}'")
        else:
            print_error("Swap failed")

    except ValueError as e:
        print_error(str(e))
    except Exception as e:
        print_error(f"Failed to swap meal: {e}")


def cmd_plan_clear(args) -> None:
    """Clear current meal plan."""
    try:
        if not args.yes:
            confirm = input("Clear current meal plan? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Cancelled.")
                return

        clear_meal_plan()
        print_success("Meal plan cleared")

    except Exception as e:
        print_error(f"Failed to clear plan: {e}")


# ==================== Grocery Commands ====================

def cmd_grocery_generate(args) -> None:
    """Generate grocery list."""
    try:
        plan = get_current_plan()

        if not plan:
            print_error("No meal plan found. Generate one first with: python main.py plan generate")
            return

        print("Generating grocery list...")

        deduct_pantry = not args.no_pantry
        items = generate_grocery_list(plan, deduct_pantry=deduct_pantry)

        if not items:
            print("\nNo items needed - pantry covers everything!")
            return

        _display_grocery_list(items)

    except Exception as e:
        print_error(f"Failed to generate grocery list: {e}")


def cmd_grocery_export(args) -> None:
    """Export grocery list."""
    try:
        plan = get_current_plan()

        if not plan:
            print_error("No meal plan found")
            return

        deduct_pantry = not args.no_pantry
        items = generate_grocery_list(plan, deduct_pantry=deduct_pantry)

        if not items:
            print_warning("No items to export")
            return

        output_path = export_grocery_list(items, format=args.format, output_path=args.output)
        print_success(f"Exported to {output_path}")

    except Exception as e:
        print_error(f"Failed to export grocery list: {e}")


def _display_grocery_list(items) -> None:
    """Display grocery list."""
    print_header(f"Grocery List ({len(items)} items)")

    current_category = None
    for item in items:
        if item.category != current_category:
            current_category = item.category
            print_section(current_category)

        from utils import format_quantity
        qty = format_quantity(item.quantity)
        print(f"  [ ] {item.ingredient_name} - {qty} {item.unit}")

    summary = get_grocery_summary(items)
    print(f"\n{'=' * 60}")
    print(f"Total Items: {summary['total']}")


# ==================== Pantry Commands ====================

def cmd_pantry_add(args) -> None:
    """Add item to pantry."""
    try:
        item = PantryItem(
            ingredient_name=args.ingredient,
            quantity=args.quantity,
            unit=args.unit
        )

        item_id = add_pantry_item(item)
        print_success(f"Added {args.quantity} {args.unit} of {args.ingredient} to pantry")

    except ValueError as e:
        print_error(str(e))
    except Exception as e:
        print_error(f"Failed to add pantry item: {e}")


def cmd_pantry_list(args) -> None:
    """List pantry items."""
    try:
        items = get_pantry_items()

        if not items:
            print("\nPantry is empty.")
            return

        print_header(f"Pantry Inventory ({len(items)} items)")

        # Group by category
        from utils import get_ingredient_category
        by_category = {}
        for item in items:
            category = get_ingredient_category(item.ingredient_name)
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)

        for category in sorted(by_category.keys()):
            print_section(category)
            for item in sorted(by_category[category], key=lambda x: x.ingredient_name):
                from utils import format_quantity
                qty = format_quantity(item.quantity)
                print(f"  • {item.ingredient_name}: {qty} {item.unit}")

    except Exception as e:
        print_error(f"Failed to list pantry: {e}")


def cmd_pantry_remove(args) -> None:
    """Remove item from pantry."""
    try:
        if remove_pantry_item(args.ingredient, unit=args.unit):
            unit_str = f" ({args.unit})" if args.unit else ""
            print_success(f"Removed {args.ingredient}{unit_str} from pantry")
        else:
            print_error(f"Item '{args.ingredient}' not found in pantry")

    except Exception as e:
        print_error(f"Failed to remove pantry item: {e}")


def cmd_pantry_update(args) -> None:
    """Update pantry item quantity."""
    try:
        if update_pantry_quantity(args.ingredient, args.quantity, args.unit):
            print_success(f"Updated {args.ingredient} to {args.quantity} {args.unit}")
        else:
            print_error(f"Item '{args.ingredient}' not found in pantry")

    except ValueError as e:
        print_error(str(e))
    except Exception as e:
        print_error(f"Failed to update pantry item: {e}")


# ==================== Main CLI Setup ====================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Meal Planner & Grocery List Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Recipe commands
    recipe_parser = subparsers.add_parser("recipe", help="Manage recipes")
    recipe_sub = recipe_parser.add_subparsers(dest="action", required=True)

    # recipe add
    recipe_sub.add_parser("add", help="Add a new recipe (interactive)")

    # recipe list
    list_parser = recipe_sub.add_parser("list", help="List all recipes")
    list_parser.add_argument("--meal-type", "-m", choices=["breakfast", "lunch", "dinner", "snack"], help="Filter by meal type")

    # recipe view
    view_parser = recipe_sub.add_parser("view", help="View recipe details")
    view_parser.add_argument("name", help="Recipe name")

    # recipe delete
    delete_parser = recipe_sub.add_parser("delete", help="Delete a recipe")
    delete_parser.add_argument("name", help="Recipe name")
    delete_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")

    # recipe import
    import_parser = recipe_sub.add_parser("import", help="Import recipes from JSON")
    import_parser.add_argument("file", help="JSON file path")

    # recipe export
    export_parser = recipe_sub.add_parser("export", help="Export recipes to JSON")
    export_parser.add_argument("--output", "-o", default="exports/recipes.json", help="Output file path")
    export_parser.add_argument("--meal-type", "-m", choices=["breakfast", "lunch", "dinner", "snack"], help="Filter by meal type")

    # Plan commands
    plan_parser = subparsers.add_parser("plan", help="Meal planning")
    plan_sub = plan_parser.add_subparsers(dest="action", required=True)

    # plan generate
    gen_parser = plan_sub.add_parser("generate", help="Generate meal plan")
    gen_parser.add_argument("--days", "-d", type=int, default=7, help="Number of days (default: 7)")
    gen_parser.add_argument("--servings", "-s", type=int, default=2, help="Servings per meal (default: 2)")
    gen_parser.add_argument("--no-breakfast", action="store_true", help="Exclude breakfast")
    gen_parser.add_argument("--no-lunch", action="store_true", help="Exclude lunch")
    gen_parser.add_argument("--no-dinner", action="store_true", help="Exclude dinner")

    # plan view
    plan_sub.add_parser("view", help="View current meal plan")

    # plan swap
    swap_parser = plan_sub.add_parser("swap", help="Swap a meal in the plan")
    swap_parser.add_argument("day", type=int, help="Day number (1-7)")
    swap_parser.add_argument("meal_type", choices=["breakfast", "lunch", "dinner", "snack"], help="Meal type")
    swap_parser.add_argument("recipe", nargs="?", help="New recipe name (optional, will show options if not provided)")

    # plan clear
    clear_parser = plan_sub.add_parser("clear", help="Clear current meal plan")
    clear_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")

    # Grocery commands
    grocery_parser = subparsers.add_parser("grocery", help="Grocery list management")
    grocery_sub = grocery_parser.add_subparsers(dest="action", required=True)

    # grocery generate
    ggen_parser = grocery_sub.add_parser("generate", help="Generate grocery list from current plan")
    ggen_parser.add_argument("--no-pantry", action="store_true", help="Don't deduct pantry items")

    # grocery export
    gexport_parser = grocery_sub.add_parser("export", help="Export grocery list to file")
    gexport_parser.add_argument("--format", "-f", choices=["txt", "md", "json"], default="txt", help="Export format")
    gexport_parser.add_argument("--output", "-o", help="Output file path")
    gexport_parser.add_argument("--no-pantry", action="store_true", help="Don't deduct pantry items")

    # Pantry commands
    pantry_parser = subparsers.add_parser("pantry", help="Pantry inventory management")
    pantry_sub = pantry_parser.add_subparsers(dest="action", required=True)

    # pantry add
    padd_parser = pantry_sub.add_parser("add", help="Add item to pantry")
    padd_parser.add_argument("ingredient", help="Ingredient name")
    padd_parser.add_argument("quantity", type=float, help="Quantity")
    padd_parser.add_argument("unit", help="Unit (e.g., cups, oz, lb)")

    # pantry list
    pantry_sub.add_parser("list", help="List all pantry items")

    # pantry remove
    prem_parser = pantry_sub.add_parser("remove", help="Remove item from pantry")
    prem_parser.add_argument("ingredient", help="Ingredient name")
    prem_parser.add_argument("--unit", "-u", help="Specific unit to remove")

    # pantry update
    pupdate_parser = pantry_sub.add_parser("update", help="Update item quantity")
    pupdate_parser.add_argument("ingredient", help="Ingredient name")
    pupdate_parser.add_argument("quantity", type=float, help="New quantity")
    pupdate_parser.add_argument("unit", help="Unit")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize database on first run
    initialize_database()

    # Route to appropriate handler
    try:
        if args.command == "recipe":
            if args.action == "add":
                cmd_recipe_add(args)
            elif args.action == "list":
                cmd_recipe_list(args)
            elif args.action == "view":
                cmd_recipe_view(args)
            elif args.action == "delete":
                cmd_recipe_delete(args)
            elif args.action == "import":
                cmd_recipe_import(args)
            elif args.action == "export":
                cmd_recipe_export(args)

        elif args.command == "plan":
            if args.action == "generate":
                cmd_plan_generate(args)
            elif args.action == "view":
                cmd_plan_view(args)
            elif args.action == "swap":
                cmd_plan_swap(args)
            elif args.action == "clear":
                cmd_plan_clear(args)

        elif args.command == "grocery":
            if args.action == "generate":
                cmd_grocery_generate(args)
            elif args.action == "export":
                cmd_grocery_export(args)

        elif args.command == "pantry":
            if args.action == "add":
                cmd_pantry_add(args)
            elif args.action == "list":
                cmd_pantry_list(args)
            elif args.action == "remove":
                cmd_pantry_remove(args)
            elif args.action == "update":
                cmd_pantry_update(args)

    except KeyboardInterrupt:
        print("\n\nInterrupted.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
