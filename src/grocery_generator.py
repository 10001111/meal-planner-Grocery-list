"""Grocery list generation and consolidation."""

import json
from typing import List, Dict
from collections import defaultdict
from pathlib import Path

from models import MealPlan, GroceryItem, RecipeIngredient
from utils import (
    normalize_ingredient_name,
    get_ingredient_category,
    can_convert_units,
    convert_units,
    normalize_unit,
    format_quantity,
    are_same_ingredient
)
from pantry_manager import get_pantry_items, deduct_from_pantry


def generate_grocery_list(
    meal_plan: MealPlan,
    deduct_pantry: bool = True
) -> List[GroceryItem]:
    """
    Generate consolidated grocery list from meal plan.

    Process:
    1. Collect all ingredients from all meals
    2. Scale quantities by servings
    3. Consolidate same ingredients (convert units if needed)
    4. Categorize items
    5. Optionally deduct pantry quantities

    Args:
        meal_plan: MealPlan object
        deduct_pantry: Whether to subtract pantry items

    Returns:
        List of GroceryItem objects sorted by category
    """
    # Collect all ingredients with scaling
    all_ingredients: List[Dict] = []

    for meal in meal_plan.meals:
        recipe = meal.recipe
        serving_multiplier = meal.servings / recipe.servings

        for ing in recipe.ingredients:
            all_ingredients.append({
                'name': ing.ingredient_name,
                'quantity': ing.quantity * serving_multiplier,
                'unit': ing.unit,
            })

    # Consolidate ingredients
    grocery_items = consolidate_ingredients(all_ingredients)

    # Deduct pantry items if requested
    if deduct_pantry:
        grocery_items = _deduct_pantry_from_list(grocery_items)

    # Sort by category
    category_order = [
        "Produce",
        "Meat & Seafood",
        "Dairy & Eggs",
        "Bakery",
        "Pantry",
        "Canned Goods",
        "Condiments",
        "Frozen",
        "Other"
    ]

    def sort_key(item):
        try:
            return category_order.index(item.category)
        except ValueError:
            return len(category_order)

    grocery_items.sort(key=sort_key)

    return grocery_items


def consolidate_ingredients(ingredients: List[Dict]) -> List[GroceryItem]:
    """
    Combine same ingredients from multiple recipes.

    Handles:
    - Same ingredient, same unit: sum quantities
    - Same ingredient, different units: convert then sum
    - Similar names: match common variations

    Args:
        ingredients: List of dicts with 'name', 'quantity', 'unit'

    Returns:
        List of consolidated GroceryItem objects
    """
    # Group by normalized ingredient name
    grouped: Dict[str, List[Dict]] = defaultdict(list)

    for ing in ingredients:
        normalized_name = normalize_ingredient_name(ing['name'])
        grouped[normalized_name].append(ing)

    # Consolidate each group
    consolidated = []

    for normalized_name, ing_list in grouped.items():
        # Use the first occurrence's original name (for display)
        display_name = ing_list[0]['name']
        category = get_ingredient_category(normalized_name)

        # Group by unit type (volume, weight, count)
        by_unit: Dict[str, float] = defaultdict(float)

        for ing in ing_list:
            unit = normalize_unit(ing['unit'])
            by_unit[unit] += ing['quantity']

        # Try to consolidate different units of same type
        if len(by_unit) > 1:
            # Try to convert all to a common unit
            units = list(by_unit.keys())
            base_unit = units[0]
            consolidated_quantity = by_unit[base_unit]

            for other_unit in units[1:]:
                if can_convert_units(other_unit, base_unit):
                    try:
                        converted = convert_units(by_unit[other_unit], other_unit, base_unit)
                        consolidated_quantity += converted
                        del by_unit[other_unit]
                    except ValueError:
                        pass  # Keep separate if conversion fails

            by_unit[base_unit] = consolidated_quantity

        # Create GroceryItem for each remaining unit
        for unit, quantity in by_unit.items():
            if quantity > 0:  # Only include if quantity is positive
                consolidated.append(GroceryItem(
                    ingredient_name=display_name,
                    quantity=quantity,
                    unit=unit,
                    category=category
                ))

    return consolidated


def _deduct_pantry_from_list(grocery_items: List[GroceryItem]) -> List[GroceryItem]:
    """
    Deduct pantry quantities from grocery list.

    Args:
        grocery_items: Original grocery list

    Returns:
        Updated grocery list with pantry items deducted
    """
    pantry_items = get_pantry_items()

    if not pantry_items:
        return grocery_items

    # Create a map of pantry items by normalized name
    pantry_map = {}
    for item in pantry_items:
        normalized = normalize_ingredient_name(item.ingredient_name)
        if normalized not in pantry_map:
            pantry_map[normalized] = []
        pantry_map[normalized].append(item)

    # Process each grocery item
    updated_items = []

    for grocery_item in grocery_items:
        normalized = normalize_ingredient_name(grocery_item.ingredient_name)

        if normalized in pantry_map:
            pantry_entries = pantry_map[normalized]
            remaining_needed = grocery_item.quantity

            # Try to deduct from pantry
            for pantry_item in pantry_entries:
                if remaining_needed <= 0:
                    break

                # Try to convert units if different
                pantry_qty = pantry_item.quantity
                if pantry_item.unit != grocery_item.unit:
                    if can_convert_units(pantry_item.unit, grocery_item.unit):
                        try:
                            pantry_qty = convert_units(
                                pantry_item.quantity,
                                pantry_item.unit,
                                grocery_item.unit
                            )
                        except ValueError:
                            continue  # Can't convert, skip this pantry item
                    else:
                        continue  # Incompatible units

                # Deduct what we can from pantry
                deduction = min(remaining_needed, pantry_qty)
                remaining_needed -= deduction

            # Only add to list if we still need some
            if remaining_needed > 0.01:  # Small threshold to avoid floating point issues
                updated_items.append(GroceryItem(
                    ingredient_name=grocery_item.ingredient_name,
                    quantity=remaining_needed,
                    unit=grocery_item.unit,
                    category=grocery_item.category
                ))
        else:
            # No pantry item, add as-is
            updated_items.append(grocery_item)

    return updated_items


def export_grocery_list(
    items: List[GroceryItem],
    format: str = "txt",
    output_path: str = None
) -> str:
    """
    Export grocery list to file.

    Formats:
    - txt: Plain text with categories
    - md: Markdown with checkboxes
    - json: Structured data

    Args:
        items: List of GroceryItem objects
        format: Export format (txt, md, json)
        output_path: Output file path (default: exports/grocery_list.{format})

    Returns:
        Path to exported file
    """
    if output_path is None:
        output_path = f"exports/grocery_list.{format}"

    # Ensure exports directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if format == "txt":
        _export_txt(items, output_path)
    elif format == "md":
        _export_markdown(items, output_path)
    elif format == "json":
        _export_json(items, output_path)
    else:
        raise ValueError(f"Unsupported format: {format}")

    return output_path


def _export_txt(items: List[GroceryItem], output_path: str) -> None:
    """Export as plain text."""
    with open(output_path, 'w') as f:
        f.write("=" * 50 + "\n")
        f.write("GROCERY LIST\n")
        f.write("=" * 50 + "\n\n")

        current_category = None
        for item in items:
            if item.category != current_category:
                current_category = item.category
                f.write(f"\n{current_category.upper()}\n")
                f.write("-" * len(current_category) + "\n")

            qty_str = format_quantity(item.quantity)
            f.write(f"  [ ] {item.ingredient_name} - {qty_str} {item.unit}\n")

        f.write("\n" + "=" * 50 + "\n")
        f.write(f"Total Items: {len(items)}\n")


def _export_markdown(items: List[GroceryItem], output_path: str) -> None:
    """Export as markdown with checkboxes."""
    with open(output_path, 'w') as f:
        f.write("# Grocery List\n\n")

        current_category = None
        for item in items:
            if item.category != current_category:
                current_category = item.category
                f.write(f"\n## {current_category}\n\n")

            qty_str = format_quantity(item.quantity)
            f.write(f"- [ ] {item.ingredient_name} - {qty_str} {item.unit}\n")

        f.write(f"\n---\n**Total Items:** {len(items)}\n")


def _export_json(items: List[GroceryItem], output_path: str) -> None:
    """Export as JSON."""
    data = {
        'items': [
            {
                'ingredient': item.ingredient_name,
                'quantity': item.quantity,
                'unit': item.unit,
                'category': item.category
            }
            for item in items
        ],
        'total_items': len(items)
    }

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


def get_grocery_summary(items: List[GroceryItem]) -> Dict[str, int]:
    """
    Get summary statistics for grocery list.

    Args:
        items: List of GroceryItem objects

    Returns:
        Dict with category counts
    """
    summary = defaultdict(int)

    for item in items:
        summary[item.category] += 1

    summary['total'] = len(items)

    return dict(summary)
