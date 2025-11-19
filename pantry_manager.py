"""Pantry inventory management."""

from typing import List, Optional
from datetime import datetime

from models import PantryItem
from database import get_connection
from utils import normalize_ingredient_name, normalize_unit, can_convert_units, convert_units
from recipe_manager import _get_or_create_ingredient


def add_pantry_item(item: PantryItem) -> int:
    """
    Add or update pantry item.

    If item with same ingredient and unit exists, adds to existing quantity.
    If item with same ingredient but different unit exists, creates separate entry.

    Args:
        item: PantryItem to add

    Returns:
        Pantry item ID

    Raises:
        ValueError: If quantity is invalid
    """
    if item.quantity <= 0:
        raise ValueError("Quantity must be positive")

    normalized_name = normalize_ingredient_name(item.ingredient_name)
    normalized_unit = normalize_unit(item.unit)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Get or create ingredient
        ingredient_id = _get_or_create_ingredient(conn, normalized_name)

        # Check if item with same ingredient and unit already exists
        cursor.execute("""
            SELECT id, quantity
            FROM pantry
            WHERE ingredient_id = ? AND unit = ?
        """, (ingredient_id, normalized_unit))

        existing = cursor.fetchone()

        if existing:
            # Update existing quantity
            pantry_id = existing[0]
            new_quantity = existing[1] + item.quantity

            cursor.execute("""
                UPDATE pantry
                SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_quantity, pantry_id))
        else:
            # Insert new pantry item
            cursor.execute("""
                INSERT INTO pantry (ingredient_id, quantity, unit)
                VALUES (?, ?, ?)
            """, (ingredient_id, item.quantity, normalized_unit))
            pantry_id = cursor.lastrowid

        conn.commit()
        return pantry_id

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_pantry_items() -> List[PantryItem]:
    """
    Get all pantry items.

    Returns:
        List of PantryItem objects
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.id, i.name, p.quantity, p.unit, p.updated_at, i.id
        FROM pantry p
        JOIN ingredients i ON p.ingredient_id = i.id
        ORDER BY i.name
    """)

    items = []
    for row in cursor.fetchall():
        items.append(PantryItem(
            id=row[0],
            ingredient_name=row[1],
            quantity=row[2],
            unit=row[3],
            updated_at=row[4],
            ingredient_id=row[5]
        ))

    conn.close()
    return items


def get_pantry_item(ingredient_name: str, unit: Optional[str] = None) -> Optional[PantryItem]:
    """
    Get specific pantry item by ingredient name and optional unit.

    Args:
        ingredient_name: Name of ingredient
        unit: Optional unit filter

    Returns:
        PantryItem or None if not found
    """
    normalized_name = normalize_ingredient_name(ingredient_name)

    conn = get_connection()
    cursor = conn.cursor()

    if unit:
        normalized_unit = normalize_unit(unit)
        cursor.execute("""
            SELECT p.id, i.name, p.quantity, p.unit, p.updated_at, i.id
            FROM pantry p
            JOIN ingredients i ON p.ingredient_id = i.id
            WHERE i.name = ? AND p.unit = ?
        """, (normalized_name, normalized_unit))
    else:
        cursor.execute("""
            SELECT p.id, i.name, p.quantity, p.unit, p.updated_at, i.id
            FROM pantry p
            JOIN ingredients i ON p.ingredient_id = i.id
            WHERE i.name = ?
        """, (normalized_name,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return PantryItem(
        id=row[0],
        ingredient_name=row[1],
        quantity=row[2],
        unit=row[3],
        updated_at=row[4],
        ingredient_id=row[5]
    )


def update_pantry_quantity(ingredient_name: str, quantity: float, unit: str) -> bool:
    """
    Update quantity of existing pantry item (replaces current quantity).

    Args:
        ingredient_name: Name of ingredient
        quantity: New quantity (replaces existing)
        unit: Unit of measure

    Returns:
        True if updated, False if not found

    Raises:
        ValueError: If quantity is invalid
    """
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")

    normalized_name = normalize_ingredient_name(ingredient_name)
    normalized_unit = normalize_unit(unit)

    conn = get_connection()
    cursor = conn.cursor()

    # If quantity is 0, delete the item
    if quantity == 0:
        cursor.execute("""
            DELETE FROM pantry
            WHERE ingredient_id = (SELECT id FROM ingredients WHERE name = ?)
            AND unit = ?
        """, (normalized_name, normalized_unit))
    else:
        cursor.execute("""
            UPDATE pantry
            SET quantity = ?, updated_at = CURRENT_TIMESTAMP
            WHERE ingredient_id = (SELECT id FROM ingredients WHERE name = ?)
            AND unit = ?
        """, (quantity, normalized_name, normalized_unit))

    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return updated


def remove_pantry_item(ingredient_name: str, unit: Optional[str] = None) -> bool:
    """
    Remove item from pantry.

    Args:
        ingredient_name: Name of ingredient
        unit: Optional unit (if None, removes all units of this ingredient)

    Returns:
        True if removed, False if not found
    """
    normalized_name = normalize_ingredient_name(ingredient_name)

    conn = get_connection()
    cursor = conn.cursor()

    if unit:
        normalized_unit = normalize_unit(unit)
        cursor.execute("""
            DELETE FROM pantry
            WHERE ingredient_id = (SELECT id FROM ingredients WHERE name = ?)
            AND unit = ?
        """, (normalized_name, normalized_unit))
    else:
        cursor.execute("""
            DELETE FROM pantry
            WHERE ingredient_id = (SELECT id FROM ingredients WHERE name = ?)
        """, (normalized_name,))

    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()

    return deleted


def deduct_from_pantry(ingredient_name: str, quantity: float, unit: str) -> float:
    """
    Deduct quantity from pantry.

    Args:
        ingredient_name: Name of ingredient
        quantity: Amount to deduct
        unit: Unit of measure

    Returns:
        Remaining quantity needed (0 if fully covered by pantry)
    """
    normalized_name = normalize_ingredient_name(ingredient_name)
    normalized_unit = normalize_unit(unit)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Get all pantry items for this ingredient
        cursor.execute("""
            SELECT id, quantity, unit
            FROM pantry
            WHERE ingredient_id = (SELECT id FROM ingredients WHERE name = ?)
        """, (normalized_name,))

        pantry_items = cursor.fetchall()

        if not pantry_items:
            conn.close()
            return quantity  # Nothing in pantry, need full amount

        remaining_needed = quantity

        for pantry_id, pantry_qty, pantry_unit in pantry_items:
            if remaining_needed <= 0:
                break

            # Try to use this pantry item
            usable_qty = pantry_qty

            # Convert units if different
            if pantry_unit != normalized_unit:
                if can_convert_units(pantry_unit, normalized_unit):
                    try:
                        usable_qty = convert_units(pantry_qty, pantry_unit, normalized_unit)
                    except ValueError:
                        continue  # Can't convert, skip this pantry item
                else:
                    continue  # Incompatible units

            # Deduct what we can
            deduction = min(remaining_needed, usable_qty)
            remaining_needed -= deduction

            # Update pantry quantity
            if pantry_unit == normalized_unit:
                # Direct deduction
                new_pantry_qty = pantry_qty - deduction
            else:
                # Need to convert back
                deduction_in_pantry_units = convert_units(deduction, normalized_unit, pantry_unit)
                new_pantry_qty = pantry_qty - deduction_in_pantry_units

            if new_pantry_qty <= 0:
                # Remove from pantry
                cursor.execute("DELETE FROM pantry WHERE id = ?", (pantry_id,))
            else:
                # Update quantity
                cursor.execute("""
                    UPDATE pantry
                    SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_pantry_qty, pantry_id))

        conn.commit()
        return max(0, remaining_needed)

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def clear_pantry() -> int:
    """
    Clear all items from pantry.

    Returns:
        Number of items removed
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM pantry")
    count = cursor.rowcount

    conn.commit()
    conn.close()

    return count


def get_pantry_value_by_category() -> dict:
    """
    Get count of pantry items grouped by category.

    Returns:
        Dict mapping category to item count
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.category, COUNT(*) as count
        FROM pantry p
        JOIN ingredients i ON p.ingredient_id = i.id
        GROUP BY i.category
        ORDER BY count DESC
    """)

    results = {}
    for row in cursor.fetchall():
        results[row[0]] = row[1]

    conn.close()
    return results
