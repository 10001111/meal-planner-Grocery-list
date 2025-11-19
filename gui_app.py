#!/usr/bin/env python3
"""GUI Application for Meal Planner & Grocery List Generator."""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from typing import Optional, List
import sys
from pathlib import Path

from models import Recipe, RecipeIngredient, PantryItem
from database import initialize_database
from recipe_manager import (
    add_recipe, get_recipe, get_all_recipes, delete_recipe,
    import_recipes_from_json, export_recipes_to_json
)
from meal_planner import (
    generate_meal_plan, get_current_plan, save_meal_plan,
    swap_meal, get_swap_suggestions, clear_meal_plan
)
from grocery_generator import generate_grocery_list, export_grocery_list
from pantry_manager import (
    add_pantry_item, get_pantry_items, update_pantry_quantity,
    remove_pantry_item
)
from utils import parse_ingredient_string, format_quantity, get_ingredient_category


class MealPlannerGUI:
    """Main GUI application class."""

    # Dark theme color palette
    COLORS = {
        'bg_dark': '#1a1a1a',        # Very dark gray (almost black)
        'bg_medium': '#2d2d2d',      # Medium dark gray
        'bg_light': '#3d3d3d',       # Lighter dark gray
        'fg_primary': "#242222",     # Light gray text
        'fg_secondary': "#292727",   # Dimmer gray text
        'accent': '#4a4a4a',         # Accent gray
        'button': '#4a4a4a',         # Button background (pure gray)
        'button_hover': "#352929",   # Button hover (lighter gray)
        'button_active': "#231b1b",  # Button active/pressed (darker gray)
        'selected': '#505050',       # Selection color
        'border': '#555555',         # Border color
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Meal Planner & Grocery List Generator")
        self.root.geometry("1000x700")

        # Apply dark theme to root window
        self.root.configure(bg=self.COLORS['bg_dark'])

        # Initialize database
        initialize_database()

        # Configure dark theme styles
        self.configure_dark_theme()

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.create_recipes_tab()
        self.create_meal_plan_tab()
        self.create_grocery_tab()
        self.create_pantry_tab()

        # Status bar
        self.status_bar = tk.Label(
            root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['fg_primary']
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def configure_dark_theme(self):
        """Configure ttk styles for dark theme."""
        style = ttk.Style()

        # Configure Notebook (tabs)
        style.configure('TNotebook', background=self.COLORS['bg_dark'], borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=self.COLORS['bg_medium'],
                       foreground=self.COLORS['fg_primary'],
                       padding=[20, 10],
                       borderwidth=0)
        style.map('TNotebook.Tab',
                 background=[('selected', self.COLORS['bg_light'])],
                 foreground=[('selected', self.COLORS['fg_primary'])])

        # Configure Frame
        style.configure('TFrame', background=self.COLORS['bg_dark'])
        style.configure('TLabelframe',
                       background=self.COLORS['bg_dark'],
                       foreground=self.COLORS['fg_primary'],
                       borderwidth=1,
                       relief='solid')
        style.configure('TLabelframe.Label',
                       background=self.COLORS['bg_dark'],
                       foreground=self.COLORS['fg_primary'])

        # Configure Labels
        style.configure('TLabel',
                       background=self.COLORS['bg_dark'],
                       foreground=self.COLORS['fg_primary'])

        # Configure Buttons with gradient effect
        style.configure('TButton',
                       background=self.COLORS['button'],
                       foreground=self.COLORS['fg_primary'],
                       borderwidth=1,
                       focuscolor=self.COLORS['button_hover'],
                       padding=[10, 5],
                       relief='raised')
        style.map('TButton',
                 background=[
                     ('active', self.COLORS['button_hover']),      # Hover - lighter
                     ('pressed', self.COLORS['button_active']),    # Pressed - darker
                     ('!active', self.COLORS['button'])            # Normal state
                 ],
                 foreground=[('active', self.COLORS['fg_primary'])],
                 relief=[
                     ('pressed', 'sunken'),
                     ('!pressed', 'raised')
                 ])

        # Configure Combobox
        style.configure('TCombobox',
                       fieldbackground=self.COLORS['bg_medium'],
                       background=self.COLORS['bg_medium'],
                       foreground=self.COLORS['fg_primary'],
                       arrowcolor=self.COLORS['fg_primary'],
                       borderwidth=1)

        # Configure Entry
        style.configure('TEntry',
                       fieldbackground=self.COLORS['bg_medium'],
                       foreground=self.COLORS['fg_primary'],
                       borderwidth=1)

        # Configure Checkbutton
        style.configure('TCheckbutton',
                       background=self.COLORS['bg_dark'],
                       foreground=self.COLORS['fg_primary'])

        # Configure Spinbox
        style.configure('TSpinbox',
                       fieldbackground=self.COLORS['bg_medium'],
                       foreground=self.COLORS['fg_primary'],
                       arrowcolor=self.COLORS['fg_primary'],
                       borderwidth=1)

    def set_status(self, message: str):
        """Update status bar message."""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    # ==================== Recipes Tab ====================

    def create_recipes_tab(self):
        """Create the recipes management tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Recipes")

        # Left panel - Recipe list
        left_frame = ttk.Frame(tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(left_frame, text="Your Recipes", font=('Arial', 12, 'bold')).pack(pady=5)

        # Filter frame
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
        self.recipe_filter = ttk.Combobox(filter_frame, values=["All", "breakfast", "lunch", "dinner", "snack"], state='readonly')
        self.recipe_filter.set("All")
        self.recipe_filter.pack(side=tk.LEFT, padx=5)
        self.recipe_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_recipes())

        # Recipe listbox
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.recipe_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('Arial', 10),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['fg_primary'],
            selectbackground=self.COLORS['selected'],
            selectforeground=self.COLORS['fg_primary'],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['border']
        )
        self.recipe_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.recipe_listbox.yview)

        self.recipe_listbox.bind("<<ListboxSelect>>", self.on_recipe_select)

        # Buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="Add Recipe", command=self.add_recipe_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_recipe).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Import JSON", command=self.import_recipes).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Export JSON", command=self.export_recipes).pack(side=tk.LEFT, padx=2)

        # Right panel - Recipe details
        right_frame = ttk.Frame(tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(right_frame, text="Recipe Details", font=('Arial', 12, 'bold')).pack(pady=5)

        self.recipe_details = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=50,
            height=30,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['fg_primary'],
            insertbackground=self.COLORS['fg_primary'],
            selectbackground=self.COLORS['selected'],
            selectforeground=self.COLORS['fg_primary'],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['border']
        )
        self.recipe_details.pack(fill=tk.BOTH, expand=True)

        self.refresh_recipes()

    def refresh_recipes(self):
        """Refresh the recipe list."""
        self.recipe_listbox.delete(0, tk.END)

        filter_val = self.recipe_filter.get()
        meal_type = None if filter_val == "All" else filter_val

        recipes = get_all_recipes(meal_type=meal_type)

        for recipe in sorted(recipes, key=lambda r: r.name):
            display_text = f"{recipe.name} ({recipe.meal_type}) - {recipe.total_time()}min"
            self.recipe_listbox.insert(tk.END, display_text)

    def on_recipe_select(self, event):
        """Handle recipe selection."""
        selection = self.recipe_listbox.curselection()
        if not selection:
            return

        selected_text = self.recipe_listbox.get(selection[0])
        recipe_name = selected_text.split(" (")[0]

        recipe = get_recipe(recipe_name)
        if recipe:
            self.display_recipe_details(recipe)

    def display_recipe_details(self, recipe: Recipe):
        """Display recipe details in the text area."""
        self.recipe_details.delete(1.0, tk.END)

        details = f"{recipe.name}\n"
        details += "=" * 50 + "\n\n"
        details += f"Meal Type: {recipe.meal_type.capitalize()}\n"
        details += f"Servings: {recipe.servings}\n"
        details += f"Prep Time: {recipe.prep_time} min\n"
        details += f"Cook Time: {recipe.cook_time} min\n"
        details += f"Total Time: {recipe.total_time()} min\n"

        if recipe.cuisine:
            details += f"Cuisine: {recipe.cuisine}\n"

        if recipe.dietary_tags:
            details += f"Tags: {', '.join(recipe.dietary_tags)}\n"

        details += "\nIngredients:\n"
        details += "-" * 30 + "\n"
        for ing in recipe.ingredients:
            qty = format_quantity(ing.quantity)
            prep = f", {ing.preparation}" if ing.preparation else ""
            details += f"  • {qty} {ing.unit} {ing.ingredient_name}{prep}\n"

        if recipe.instructions:
            details += "\nInstructions:\n"
            details += "-" * 30 + "\n"
            details += recipe.instructions

        self.recipe_details.insert(1.0, details)

    def add_recipe_dialog(self):
        """Open dialog to add a new recipe."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Recipe")
        dialog.geometry("600x700")
        dialog.configure(bg=self.COLORS['bg_dark'])

        # Create scrollable frame
        canvas = tk.Canvas(
            dialog,
            bg=self.COLORS['bg_dark'],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Basic info
        row = 0
        ttk.Label(scrollable_frame, text="Recipe Name*:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        name_entry = ttk.Entry(scrollable_frame, width=40)
        name_entry.grid(row=row, column=1, padx=5, pady=2)

        row += 1
        ttk.Label(scrollable_frame, text="Meal Type*:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        meal_type_var = tk.StringVar()
        meal_type_combo = ttk.Combobox(scrollable_frame, textvariable=meal_type_var,
                                       values=["breakfast", "lunch", "dinner", "snack"], state='readonly')
        meal_type_combo.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)

        row += 1
        ttk.Label(scrollable_frame, text="Servings:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        servings_entry = ttk.Entry(scrollable_frame, width=10)
        servings_entry.insert(0, "4")
        servings_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)

        row += 1
        ttk.Label(scrollable_frame, text="Prep Time (min):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        prep_entry = ttk.Entry(scrollable_frame, width=10)
        prep_entry.insert(0, "0")
        prep_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)

        row += 1
        ttk.Label(scrollable_frame, text="Cook Time (min):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        cook_entry = ttk.Entry(scrollable_frame, width=10)
        cook_entry.insert(0, "0")
        cook_entry.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)

        row += 1
        ttk.Label(scrollable_frame, text="Cuisine:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        cuisine_entry = ttk.Entry(scrollable_frame, width=40)
        cuisine_entry.grid(row=row, column=1, padx=5, pady=2)

        row += 1
        ttk.Label(scrollable_frame, text="Tags (comma-separated):").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        tags_entry = ttk.Entry(scrollable_frame, width=40)
        tags_entry.grid(row=row, column=1, padx=5, pady=2)

        # Ingredients
        row += 1
        ttk.Label(scrollable_frame, text="Ingredients (one per line):", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)

        row += 1
        ttk.Label(scrollable_frame, text="Format: '2 cups flour' or '1 lb chicken, diced'").grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=5)

        row += 1
        ingredients_text = scrolledtext.ScrolledText(
            scrollable_frame,
            width=50,
            height=10,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['fg_primary'],
            insertbackground=self.COLORS['fg_primary'],
            selectbackground=self.COLORS['selected'],
            selectforeground=self.COLORS['fg_primary'],
            borderwidth=1,
            highlightthickness=0
        )
        ingredients_text.grid(row=row, column=0, columnspan=2, padx=5, pady=5)

        # Instructions
        row += 1
        ttk.Label(scrollable_frame, text="Instructions:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)

        row += 1
        instructions_text = scrolledtext.ScrolledText(
            scrollable_frame,
            width=50,
            height=10,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['fg_primary'],
            insertbackground=self.COLORS['fg_primary'],
            selectbackground=self.COLORS['selected'],
            selectforeground=self.COLORS['fg_primary'],
            borderwidth=1,
            highlightthickness=0
        )
        instructions_text.grid(row=row, column=0, columnspan=2, padx=5, pady=5)

        # Buttons
        def save_recipe():
            try:
                # Get basic info
                name = name_entry.get().strip()
                if not name:
                    messagebox.showerror("Error", "Recipe name is required")
                    return

                meal_type = meal_type_var.get()
                if not meal_type:
                    messagebox.showerror("Error", "Meal type is required")
                    return

                servings = int(servings_entry.get())
                prep_time = int(prep_entry.get())
                cook_time = int(cook_entry.get())
                cuisine = cuisine_entry.get().strip()

                tags_str = tags_entry.get().strip()
                dietary_tags = [t.strip() for t in tags_str.split(",")] if tags_str else []

                # Parse ingredients
                ingredients = []
                ing_lines = ingredients_text.get(1.0, tk.END).strip().split('\n')

                for line in ing_lines:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        quantity, unit, ing_name = parse_ingredient_string(line)

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
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not parse ingredient '{line}': {e}")
                        return

                if not ingredients:
                    messagebox.showerror("Error", "At least one ingredient is required")
                    return

                instructions = instructions_text.get(1.0, tk.END).strip()

                # Create recipe
                recipe = Recipe(
                    name=name,
                    meal_type=meal_type,
                    servings=servings,
                    ingredients=ingredients,
                    prep_time=prep_time,
                    cook_time=cook_time,
                    cuisine=cuisine,
                    instructions=instructions,
                    dietary_tags=dietary_tags
                )

                recipe_id = add_recipe(recipe)
                messagebox.showinfo("Success", f"Recipe '{name}' added successfully!")
                self.refresh_recipes()
                dialog.destroy()

            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save recipe: {e}")

        row += 1
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Save Recipe", command=save_recipe).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def delete_recipe(self):
        """Delete selected recipe."""
        selection = self.recipe_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a recipe to delete")
            return

        selected_text = self.recipe_listbox.get(selection[0])
        recipe_name = selected_text.split(" (")[0]

        if messagebox.askyesno("Confirm Delete", f"Delete recipe '{recipe_name}'?"):
            if delete_recipe(recipe_name):
                self.refresh_recipes()
                self.recipe_details.delete(1.0, tk.END)
                messagebox.showinfo("Success", "Recipe deleted")
            else:
                messagebox.showerror("Error", "Failed to delete recipe")

    def import_recipes(self):
        """Import recipes from JSON file."""
        filename = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                results = import_recipes_from_json(filename)
                msg = f"Success: {results['success']}\nSkipped: {results['skipped']}\nFailed: {results['failed']}"
                messagebox.showinfo("Import Results", msg)
                self.refresh_recipes()
            except Exception as e:
                messagebox.showerror("Error", f"Import failed: {e}")

    def export_recipes(self):
        """Export recipes to JSON file."""
        filename = filedialog.asksaveasfilename(
            title="Save recipes as",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                count = export_recipes_to_json(filename)
                messagebox.showinfo("Success", f"Exported {count} recipes to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    # ==================== Meal Plan Tab ====================

    def create_meal_plan_tab(self):
        """Create the meal planning tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Meal Plan")

        # Top controls
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(control_frame, text="Days:").pack(side=tk.LEFT, padx=5)
        self.days_spin = ttk.Spinbox(control_frame, from_=1, to=14, width=5)
        self.days_spin.set(7)
        self.days_spin.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Servings:").pack(side=tk.LEFT, padx=5)
        self.servings_spin = ttk.Spinbox(control_frame, from_=1, to=10, width=5)
        self.servings_spin.set(2)
        self.servings_spin.pack(side=tk.LEFT, padx=5)

        self.breakfast_var = tk.BooleanVar(value=True)
        self.lunch_var = tk.BooleanVar(value=True)
        self.dinner_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(control_frame, text="Breakfast", variable=self.breakfast_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="Lunch", variable=self.lunch_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="Dinner", variable=self.dinner_var).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Generate Plan", command=self.generate_plan).pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text="Clear Plan", command=self.clear_plan).pack(side=tk.LEFT, padx=5)

        # Meal plan display
        plan_frame = ttk.Frame(tab)
        plan_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.plan_text = scrolledtext.ScrolledText(
            plan_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['fg_primary'],
            insertbackground=self.COLORS['fg_primary'],
            selectbackground=self.COLORS['selected'],
            selectforeground=self.COLORS['fg_primary'],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['border']
        )
        self.plan_text.pack(fill=tk.BOTH, expand=True)

        self.refresh_meal_plan()

    def generate_plan(self):
        """Generate a new meal plan."""
        try:
            days = int(self.days_spin.get())
            servings = int(self.servings_spin.get())

            meals = []
            if self.breakfast_var.get():
                meals.append('breakfast')
            if self.lunch_var.get():
                meals.append('lunch')
            if self.dinner_var.get():
                meals.append('dinner')

            if not meals:
                messagebox.showwarning("Warning", "Select at least one meal type")
                return

            self.set_status("Generating meal plan...")
            plan = generate_meal_plan(days=days, meals=meals, servings=servings)
            save_meal_plan(plan)

            self.refresh_meal_plan()
            self.set_status("Meal plan generated successfully")
            messagebox.showinfo("Success", "Meal plan generated!")

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate plan: {e}")

    def refresh_meal_plan(self):
        """Refresh the meal plan display."""
        self.plan_text.delete(1.0, tk.END)

        plan = get_current_plan()

        if not plan:
            self.plan_text.insert(1.0, "No meal plan found.\n\nGenerate a plan using the controls above.")
            return

        output = f"Meal Plan ({plan.days} days)\n"
        output += "=" * 60 + "\n\n"

        meal_icons = {
            'breakfast': '🍳',
            'lunch': '🥗',
            'dinner': '🍽️',
            'snack': '🍪'
        }

        for day in range(1, plan.days + 1):
            meals = plan.get_meals_for_day(day)
            if not meals:
                continue

            day_name = meals[0].day_name() if meals else f"Day {day}"
            output += f"\n{day_name}\n"
            output += "-" * 40 + "\n"

            for meal in sorted(meals, key=lambda m: ['breakfast', 'lunch', 'dinner', 'snack'].index(m.meal_type)):
                icon = meal_icons.get(meal.meal_type, '•')
                output += f"  {icon} {meal.meal_type.capitalize()}: {meal.recipe.name}\n"
                output += f"     ({meal.recipe.total_time()} min, {meal.servings} servings)\n"

        self.plan_text.insert(1.0, output)

    def clear_plan(self):
        """Clear the current meal plan."""
        if messagebox.askyesno("Confirm", "Clear current meal plan?"):
            clear_meal_plan()
            self.refresh_meal_plan()
            messagebox.showinfo("Success", "Meal plan cleared")

    # ==================== Grocery Tab ====================

    def create_grocery_tab(self):
        """Create the grocery list tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Grocery List")

        # Controls
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        self.deduct_pantry_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Deduct pantry items",
                       variable=self.deduct_pantry_var).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Generate List", command=self.generate_grocery_list).pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text="Export TXT", command=lambda: self.export_grocery('txt')).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export Markdown", command=lambda: self.export_grocery('md')).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export JSON", command=lambda: self.export_grocery('json')).pack(side=tk.LEFT, padx=5)

        # Grocery list display
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.grocery_text = scrolledtext.ScrolledText(
            list_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['fg_primary'],
            insertbackground=self.COLORS['fg_primary'],
            selectbackground=self.COLORS['selected'],
            selectforeground=self.COLORS['fg_primary'],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['border']
        )
        self.grocery_text.pack(fill=tk.BOTH, expand=True)

    def generate_grocery_list(self):
        """Generate grocery list from current meal plan."""
        try:
            plan = get_current_plan()

            if not plan:
                messagebox.showwarning("Warning", "No meal plan found. Generate a meal plan first.")
                return

            self.set_status("Generating grocery list...")
            deduct_pantry = self.deduct_pantry_var.get()
            items = generate_grocery_list(plan, deduct_pantry=deduct_pantry)

            if not items:
                self.grocery_text.delete(1.0, tk.END)
                self.grocery_text.insert(1.0, "No items needed - pantry covers everything!")
                self.set_status("Grocery list is empty")
                return

            # Display list
            output = f"Grocery List ({len(items)} items)\n"
            output += "=" * 60 + "\n\n"

            current_category = None
            for item in items:
                if item.category != current_category:
                    current_category = item.category
                    output += f"\n{current_category}\n"
                    output += "-" * 40 + "\n"

                qty = format_quantity(item.quantity)
                output += f"  [ ] {item.ingredient_name} - {qty} {item.unit}\n"

            self.grocery_text.delete(1.0, tk.END)
            self.grocery_text.insert(1.0, output)
            self.set_status(f"Grocery list generated ({len(items)} items)")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate grocery list: {e}")

    def export_grocery(self, format_type: str):
        """Export grocery list to file."""
        try:
            plan = get_current_plan()
            if not plan:
                messagebox.showwarning("Warning", "No meal plan found")
                return

            deduct_pantry = self.deduct_pantry_var.get()
            items = generate_grocery_list(plan, deduct_pantry=deduct_pantry)

            if not items:
                messagebox.showwarning("Warning", "No items to export")
                return

            extensions = {'txt': '.txt', 'md': '.md', 'json': '.json'}
            filename = filedialog.asksaveasfilename(
                title="Save grocery list",
                defaultextension=extensions[format_type],
                filetypes=[(f"{format_type.upper()} files", f"*{extensions[format_type]}"), ("All files", "*.*")]
            )

            if filename:
                output_path = export_grocery_list(items, format=format_type, output_path=filename)
                messagebox.showinfo("Success", f"Exported to {output_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    # ==================== Pantry Tab ====================

    def create_pantry_tab(self):
        """Create the pantry management tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Pantry")

        # Left panel - Add/Update
        left_frame = ttk.LabelFrame(tab, text="Add/Update Item")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(left_frame, text="Ingredient:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.pantry_ingredient = ttk.Entry(left_frame, width=30)
        self.pantry_ingredient.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(left_frame, text="Quantity:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.pantry_quantity = ttk.Entry(left_frame, width=15)
        self.pantry_quantity.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(left_frame, text="Unit:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.pantry_unit = ttk.Entry(left_frame, width=15)
        self.pantry_unit.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Add Item", command=self.add_pantry).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update", command=self.update_pantry).pack(side=tk.LEFT, padx=5)

        # Right panel - Pantry list
        right_frame = ttk.Frame(tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(right_frame, text="Pantry Inventory", font=('Arial', 12, 'bold')).pack(pady=5)

        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.pantry_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('Arial', 10),
            width=50,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['fg_primary'],
            selectbackground=self.COLORS['selected'],
            selectforeground=self.COLORS['fg_primary'],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.COLORS['border'],
            highlightcolor=self.COLORS['border']
        )
        self.pantry_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.pantry_listbox.yview)

        ttk.Button(right_frame, text="Remove Selected", command=self.remove_pantry).pack(pady=5)
        ttk.Button(right_frame, text="Refresh", command=self.refresh_pantry).pack(pady=5)

        self.refresh_pantry()

    def add_pantry(self):
        """Add item to pantry."""
        try:
            ingredient = self.pantry_ingredient.get().strip()
            if not ingredient:
                messagebox.showwarning("Warning", "Enter ingredient name")
                return

            quantity = float(self.pantry_quantity.get())
            unit = self.pantry_unit.get().strip()

            if not unit:
                messagebox.showwarning("Warning", "Enter unit")
                return

            item = PantryItem(
                ingredient_name=ingredient,
                quantity=quantity,
                unit=unit
            )

            add_pantry_item(item)
            messagebox.showinfo("Success", f"Added {quantity} {unit} of {ingredient}")

            # Clear inputs
            self.pantry_ingredient.delete(0, tk.END)
            self.pantry_quantity.delete(0, tk.END)
            self.pantry_unit.delete(0, tk.END)

            self.refresh_pantry()

        except ValueError as e:
            messagebox.showerror("Error", "Invalid quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {e}")

    def update_pantry(self):
        """Update pantry item quantity."""
        try:
            ingredient = self.pantry_ingredient.get().strip()
            if not ingredient:
                messagebox.showwarning("Warning", "Enter ingredient name")
                return

            quantity = float(self.pantry_quantity.get())
            unit = self.pantry_unit.get().strip()

            if not unit:
                messagebox.showwarning("Warning", "Enter unit")
                return

            if update_pantry_quantity(ingredient, quantity, unit):
                messagebox.showinfo("Success", f"Updated {ingredient} to {quantity} {unit}")
                self.refresh_pantry()
            else:
                messagebox.showerror("Error", "Item not found in pantry")

        except ValueError:
            messagebox.showerror("Error", "Invalid quantity")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update: {e}")

    def remove_pantry(self):
        """Remove selected pantry item."""
        selection = self.pantry_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select an item to remove")
            return

        selected_text = self.pantry_listbox.get(selection[0])
        ingredient = selected_text.split(":")[0].strip()

        if messagebox.askyesno("Confirm", f"Remove '{ingredient}' from pantry?"):
            if remove_pantry_item(ingredient):
                self.refresh_pantry()
                messagebox.showinfo("Success", "Item removed")
            else:
                messagebox.showerror("Error", "Failed to remove item")

    def refresh_pantry(self):
        """Refresh pantry list."""
        self.pantry_listbox.delete(0, tk.END)

        items = get_pantry_items()

        if not items:
            self.pantry_listbox.insert(tk.END, "Pantry is empty")
            return

        # Group by category
        by_category = {}
        for item in items:
            category = get_ingredient_category(item.ingredient_name)
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)

        for category in sorted(by_category.keys()):
            self.pantry_listbox.insert(tk.END, f"\n--- {category} ---")
            for item in sorted(by_category[category], key=lambda x: x.ingredient_name):
                qty = format_quantity(item.quantity)
                self.pantry_listbox.insert(tk.END, f"  {item.ingredient_name}: {qty} {item.unit}")


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    app = MealPlannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
