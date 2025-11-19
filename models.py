"""Data classes for application entities."""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class Ingredient:
    """Represents an ingredient in the system."""
    name: str
    category: str = "Other"
    id: Optional[int] = None

    def __str__(self) -> str:
        return self.name


@dataclass
class RecipeIngredient:
    """Represents an ingredient as part of a recipe."""
    ingredient_name: str
    quantity: float
    unit: str
    preparation: str = ""
    ingredient_id: Optional[int] = None

    def __str__(self) -> str:
        prep = f", {self.preparation}" if self.preparation else ""
        return f"{self.quantity} {self.unit} {self.ingredient_name}{prep}"


@dataclass
class Recipe:
    """Represents a recipe with all details."""
    name: str
    meal_type: str
    servings: int
    ingredients: List[RecipeIngredient]
    prep_time: int = 0
    cook_time: int = 0
    cuisine: str = ""
    instructions: str = ""
    dietary_tags: List[str] = field(default_factory=list)
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def total_time(self) -> int:
        """Calculate total cooking time."""
        return self.prep_time + self.cook_time

    def __str__(self) -> str:
        tags_str = f" [{', '.join(self.dietary_tags)}]" if self.dietary_tags else ""
        return f"{self.name} ({self.meal_type}, {self.total_time()} min){tags_str}"


@dataclass
class PantryItem:
    """Represents an item in the pantry."""
    ingredient_name: str
    quantity: float
    unit: str
    ingredient_id: Optional[int] = None
    id: Optional[int] = None
    updated_at: Optional[datetime] = None

    def __str__(self) -> str:
        return f"{self.ingredient_name}: {self.quantity} {self.unit}"


@dataclass
class PlannedMeal:
    """Represents a meal in a meal plan."""
    day_number: int  # 1-7 for Monday-Sunday
    meal_type: str
    recipe: Recipe
    servings: int
    id: Optional[int] = None

    def day_name(self) -> str:
        """Get day name from day number."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if 1 <= self.day_number <= 7:
            return days[self.day_number - 1]
        return f"Day {self.day_number}"

    def __str__(self) -> str:
        return f"{self.day_name()} - {self.meal_type.capitalize()}: {self.recipe.name} ({self.servings} servings)"


@dataclass
class GroceryItem:
    """Represents an item on the grocery list."""
    ingredient_name: str
    quantity: float
    unit: str
    category: str = "Other"

    def __str__(self) -> str:
        return f"{self.ingredient_name} - {self.quantity} {self.unit}"


@dataclass
class MealPlan:
    """Represents a complete meal plan."""
    meals: List[PlannedMeal]
    start_day: int = 1
    days: int = 7

    def get_meals_for_day(self, day_number: int) -> List[PlannedMeal]:
        """Get all meals for a specific day."""
        return [meal for meal in self.meals if meal.day_number == day_number]

    def get_meals_by_type(self, meal_type: str) -> List[PlannedMeal]:
        """Get all meals of a specific type."""
        return [meal for meal in self.meals if meal.meal_type == meal_type]

    def __str__(self) -> str:
        return f"Meal Plan: {len(self.meals)} meals across {self.days} days"
