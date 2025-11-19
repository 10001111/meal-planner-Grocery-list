"""Utility functions for unit conversion and helpers."""

import re
from typing import Tuple, Optional
from fractions import Fraction

# Unit conversion factors (to base unit)
VOLUME_TO_ML = {
    "ml": 1,
    "milliliter": 1,
    "milliliters": 1,
    "l": 1000,
    "liter": 1000,
    "liters": 1000,
    "tsp": 4.929,
    "teaspoon": 4.929,
    "teaspoons": 4.929,
    "tbsp": 14.787,
    "tablespoon": 14.787,
    "tablespoons": 14.787,
    "cup": 236.588,
    "cups": 236.588,
    "fl oz": 29.574,
    "fluid ounce": 29.574,
    "fluid ounces": 29.574,
    "pint": 473.176,
    "pints": 473.176,
    "quart": 946.353,
    "quarts": 946.353,
    "gallon": 3785.41,
    "gallons": 3785.41,
}

WEIGHT_TO_G = {
    "g": 1,
    "gram": 1,
    "grams": 1,
    "kg": 1000,
    "kilogram": 1000,
    "kilograms": 1000,
    "oz": 28.3495,
    "ounce": 28.3495,
    "ounces": 28.3495,
    "lb": 453.592,
    "pound": 453.592,
    "pounds": 453.592,
}

# Count-based units (no conversion)
COUNT_UNITS = {
    "whole", "item", "items", "piece", "pieces",
    "clove", "cloves", "bunch", "bunches",
    "can", "cans", "package", "packages", "pkg",
    "dozen", "slice", "slices", "pinch", "dash",
}

# Unit normalization mapping
UNIT_ALIASES = {
    "tablespoon": "tbsp",
    "tablespoons": "tbsp",
    "teaspoon": "tsp",
    "teaspoons": "tsp",
    "ounce": "oz",
    "ounces": "oz",
    "pound": "lb",
    "pounds": "lb",
    "gram": "g",
    "grams": "g",
    "kilogram": "kg",
    "kilograms": "kg",
    "milliliter": "ml",
    "milliliters": "ml",
    "liter": "l",
    "liters": "l",
    "cup": "cup",
    "cups": "cup",
    "fluid ounce": "fl oz",
    "fluid ounces": "fl oz",
    "pint": "pint",
    "pints": "pint",
    "quart": "quart",
    "quarts": "quart",
    "gallon": "gallon",
    "gallons": "gallon",
}

# Ingredient category mappings
INGREDIENT_CATEGORIES = {
    # Produce
    "onion": "Produce",
    "onions": "Produce",
    "yellow onion": "Produce",
    "red onion": "Produce",
    "garlic": "Produce",
    "tomato": "Produce",
    "tomatoes": "Produce",
    "cherry tomatoes": "Produce",
    "bell pepper": "Produce",
    "red bell pepper": "Produce",
    "broccoli": "Produce",
    "cucumber": "Produce",
    "lettuce": "Produce",
    "romaine lettuce": "Produce",
    "spinach": "Produce",
    "carrot": "Produce",
    "carrots": "Produce",
    "celery": "Produce",
    "zucchini": "Produce",
    "potato": "Produce",
    "potatoes": "Produce",
    "lemon": "Produce",
    "lemons": "Produce",
    "lime": "Produce",
    "banana": "Produce",
    "bananas": "Produce",
    "apple": "Produce",
    "basil": "Produce",
    "cilantro": "Produce",
    "parsley": "Produce",

    # Meat & Seafood
    "chicken": "Meat & Seafood",
    "chicken breast": "Meat & Seafood",
    "chicken thighs": "Meat & Seafood",
    "beef": "Meat & Seafood",
    "ground beef": "Meat & Seafood",
    "pork": "Meat & Seafood",
    "salmon": "Meat & Seafood",
    "shrimp": "Meat & Seafood",
    "fish": "Meat & Seafood",

    # Dairy & Eggs
    "milk": "Dairy & Eggs",
    "eggs": "Dairy & Eggs",
    "egg": "Dairy & Eggs",
    "cheese": "Dairy & Eggs",
    "cheddar cheese": "Dairy & Eggs",
    "mozzarella": "Dairy & Eggs",
    "parmesan cheese": "Dairy & Eggs",
    "feta cheese": "Dairy & Eggs",
    "greek yogurt": "Dairy & Eggs",
    "yogurt": "Dairy & Eggs",
    "butter": "Dairy & Eggs",
    "cream": "Dairy & Eggs",
    "sour cream": "Dairy & Eggs",

    # Bakery
    "bread": "Bakery",
    "tortillas": "Bakery",
    "buns": "Bakery",

    # Pantry
    "rice": "Pantry",
    "pasta": "Pantry",
    "penne pasta": "Pantry",
    "spaghetti": "Pantry",
    "flour": "Pantry",
    "sugar": "Pantry",
    "salt": "Pantry",
    "black pepper": "Pantry",
    "pepper": "Pantry",
    "olive oil": "Pantry",
    "vegetable oil": "Pantry",
    "cooking oil": "Pantry",
    "honey": "Pantry",
    "oats": "Pantry",
    "rolled oats": "Pantry",
    "chia seeds": "Pantry",

    # Condiments
    "soy sauce": "Condiments",
    "ketchup": "Condiments",
    "mustard": "Condiments",
    "mayonnaise": "Condiments",
    "hot sauce": "Condiments",

    # Canned/Jarred
    "kalamata olives": "Canned Goods",
    "olives": "Canned Goods",
}


def normalize_unit(unit: str) -> str:
    """
    Normalize unit string to standard abbreviation.

    Args:
        unit: Unit string to normalize

    Returns:
        Normalized unit string
    """
    unit_lower = unit.lower().strip()
    return UNIT_ALIASES.get(unit_lower, unit_lower)


def convert_units(quantity: float, from_unit: str, to_unit: str) -> float:
    """
    Convert between compatible units.

    Args:
        quantity: Amount in source unit
        from_unit: Source unit
        to_unit: Target unit

    Returns:
        Converted quantity

    Raises:
        ValueError: If units are incompatible
    """
    from_unit = normalize_unit(from_unit)
    to_unit = normalize_unit(to_unit)

    # If units are the same, no conversion needed
    if from_unit == to_unit:
        return quantity

    # Try volume conversion
    if from_unit in VOLUME_TO_ML and to_unit in VOLUME_TO_ML:
        ml = quantity * VOLUME_TO_ML[from_unit]
        return ml / VOLUME_TO_ML[to_unit]

    # Try weight conversion
    if from_unit in WEIGHT_TO_G and to_unit in WEIGHT_TO_G:
        grams = quantity * WEIGHT_TO_G[from_unit]
        return grams / WEIGHT_TO_G[to_unit]

    # Units are incompatible
    raise ValueError(f"Cannot convert from '{from_unit}' to '{to_unit}' - incompatible unit types")


def can_convert_units(from_unit: str, to_unit: str) -> bool:
    """
    Check if two units are compatible for conversion.

    Args:
        from_unit: Source unit
        to_unit: Target unit

    Returns:
        True if units can be converted, False otherwise
    """
    from_unit = normalize_unit(from_unit)
    to_unit = normalize_unit(to_unit)

    if from_unit == to_unit:
        return True

    # Check if both are volume units
    if from_unit in VOLUME_TO_ML and to_unit in VOLUME_TO_ML:
        return True

    # Check if both are weight units
    if from_unit in WEIGHT_TO_G and to_unit in WEIGHT_TO_G:
        return True

    return False


def parse_quantity(quantity_str: str) -> float:
    """
    Parse quantity string that may include fractions.

    Args:
        quantity_str: Quantity string (e.g., "1.5", "1/2", "1 1/2")

    Returns:
        Numeric quantity
    """
    quantity_str = quantity_str.strip()

    # Handle mixed fractions like "1 1/2"
    if ' ' in quantity_str:
        parts = quantity_str.split()
        if len(parts) == 2:
            try:
                whole = float(parts[0])
                frac = float(Fraction(parts[1]))
                return whole + frac
            except (ValueError, ZeroDivisionError):
                pass

    # Handle simple fractions like "1/2"
    if '/' in quantity_str:
        try:
            return float(Fraction(quantity_str))
        except (ValueError, ZeroDivisionError):
            pass

    # Handle decimal numbers
    try:
        return float(quantity_str)
    except ValueError:
        raise ValueError(f"Cannot parse quantity: {quantity_str}")


def parse_ingredient_string(text: str) -> Tuple[float, str, str]:
    """
    Parse ingredient string like '2 cups flour, sifted'.

    Args:
        text: Ingredient string

    Returns:
        Tuple of (quantity, unit, ingredient_name)

    Raises:
        ValueError: If string cannot be parsed
    """
    # Pattern: optional quantity, optional unit, ingredient name
    # Examples: "2 cups flour", "flour", "1 onion", "salt"

    text = text.strip()

    # Try to match "quantity unit ingredient"
    pattern = r'^([\d\s./]+)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)\s+(.+)$'
    match = re.match(pattern, text)

    if match:
        quantity_str, unit, ingredient = match.groups()
        try:
            quantity = parse_quantity(quantity_str)
            return quantity, unit.strip(), ingredient.strip()
        except ValueError:
            pass

    # Try to match "quantity ingredient" (no unit)
    pattern = r'^([\d\s./]+)\s+(.+)$'
    match = re.match(pattern, text)

    if match:
        quantity_str, ingredient = match.groups()
        try:
            quantity = parse_quantity(quantity_str)
            return quantity, "whole", ingredient.strip()
        except ValueError:
            pass

    # If no quantity found, assume 1 whole
    return 1.0, "whole", text.strip()


def get_ingredient_category(ingredient_name: str) -> str:
    """
    Determine store category for ingredient.

    Args:
        ingredient_name: Name of the ingredient

    Returns:
        Category name
    """
    ingredient_lower = ingredient_name.lower().strip()
    return INGREDIENT_CATEGORIES.get(ingredient_lower, "Other")


def format_quantity(quantity: float) -> str:
    """
    Format quantity for display (e.g., 0.5 -> '1/2').

    Args:
        quantity: Numeric quantity

    Returns:
        Formatted string
    """
    # If it's a whole number, return as is
    if quantity == int(quantity):
        return str(int(quantity))

    # Common fractions
    fractions = {
        0.125: "1/8",
        0.25: "1/4",
        0.333: "1/3",
        0.5: "1/2",
        0.667: "2/3",
        0.75: "3/4",
    }

    # Check if quantity is close to a common fraction
    for val, frac_str in fractions.items():
        if abs(quantity - val) < 0.01:
            return frac_str

    # Check for mixed numbers
    whole = int(quantity)
    remainder = quantity - whole

    if whole > 0:
        for val, frac_str in fractions.items():
            if abs(remainder - val) < 0.01:
                return f"{whole} {frac_str}"

    # Default to decimal with 2 places
    return f"{quantity:.2f}".rstrip('0').rstrip('.')


def normalize_ingredient_name(name: str) -> str:
    """
    Normalize ingredient name for consistency.

    Args:
        name: Ingredient name

    Returns:
        Normalized name (lowercase, stripped)
    """
    return name.lower().strip()


def are_same_ingredient(name1: str, name2: str) -> bool:
    """
    Check if two ingredient names refer to the same ingredient.

    Args:
        name1: First ingredient name
        name2: Second ingredient name

    Returns:
        True if they're the same ingredient
    """
    normalized1 = normalize_ingredient_name(name1)
    normalized2 = normalize_ingredient_name(name2)

    # Exact match
    if normalized1 == normalized2:
        return True

    # Check for common variations
    variations = {
        "onion": ["onions", "yellow onion", "white onion"],
        "tomato": ["tomatoes"],
        "bell pepper": ["bell peppers", "red bell pepper", "green bell pepper"],
        "garlic": ["garlic cloves", "garlic clove"],
    }

    for base, variants in variations.items():
        if normalized1 == base and normalized2 in variants:
            return True
        if normalized2 == base and normalized1 in variants:
            return True
        if normalized1 in variants and normalized2 in variants:
            return True

    return False
