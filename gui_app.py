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
    add_recipe, get_recipe, get_all_recipes, delete_recipe
)
from pdf_exporter import export_recipes_to_pdf
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

    # Cream theme color palette
    COLORS = {
        'bg_dark': '#FFF8E7',        # Light cream background
        'bg_medium': "#F5ECD7",      # Medium cream
        'bg_light': "#FEFBF3",       # Lighter cream
        'fg_primary': "#3E3022",     # Dark brown text
        'fg_secondary': "#6B5D4F",   # Medium brown text
        'accent': "#D4C4A8",         # Accent tan
        'button': "#E8DCC8",         # Button background (cream)
        'button_hover': "#D4C4A8",   # Button hover (darker tan)
        'button_active': "#C9B697",  # Button active/pressed (darker tan)
        'selected': "#D4C4A8",       # Selection color (tan)
        'border': "#C9B697",         # Border color (tan)
    }

    def __init__(self, root):
        self.root = root
        self.root.title("👨‍🍳 Meal Planner & Grocery List Generator")
        self.root.geometry("950x700")

        # Try to set cooking icon if available
        try:
            import os
            icon_path = os.path.join(os.path.dirname(__file__), 'cooking.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(default=icon_path)
        except:
            pass  # Icon file not found or not supported, will use default

        # Apply cream theme to root window
        self.root.configure(bg=self.COLORS['bg_dark'])

        # Initialize database
        initialize_database()

        # Configure cream theme styles
        self.configure_dark_theme()

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.create_recipes_tab()
        self.create_meal_plan_tab()
        self.create_grocery_tab()
        self.create_pantry_tab()
        self.create_help_tab()

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
        """Configure ttk styles for cream theme."""
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

        ttk.Label(left_frame, text="📖 Your Recipe Collection", font=('Arial', 14, 'bold')).pack(pady=10)

        # Filter frame
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=8)

        ttk.Label(filter_frame, text="Filter by Meal Type:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
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
            font=('Arial', 11),
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
        btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="➕ Add New Recipe", command=self.add_recipe_dialog).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="🗑 Delete Recipe", command=self.delete_recipe).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="📄 Export to PDF", command=self.export_recipes_pdf).pack(side=tk.LEFT, padx=3)

        # Right panel - Recipe details
        right_frame = ttk.Frame(tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(right_frame, text="📄 Recipe Details", font=('Arial', 14, 'bold')).pack(pady=10)

        self.recipe_details = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=50,
            height=30,
            font=('Arial', 11),
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

    def export_recipes_pdf(self):
        """Export recipes to PDF file."""
        # Get current filter
        filter_val = self.recipe_filter.get()
        meal_type = None if filter_val == "All" else filter_val

        # Get recipes to export
        recipes = get_all_recipes(meal_type=meal_type)

        if not recipes:
            messagebox.showwarning("Warning", "No recipes to export")
            return

        # Ask for save location
        filename = filedialog.asksaveasfilename(
            title="Save recipes as PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if filename:
            try:
                export_recipes_to_pdf(recipes, filename)
                messagebox.showinfo("Success", f"Exported {len(recipes)} recipes to PDF:\n{filename}")
            except ImportError as e:
                messagebox.showerror("Error",
                    "PDF export requires the 'reportlab' library.\n\n"
                    "Please install it with:\npip install reportlab")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")

    # ==================== Meal Plan Tab ====================

    def create_meal_plan_tab(self):
        """Create the meal planning tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Meal Plan")

        # Top controls
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Label(control_frame, text="📅 Number of Days:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=8)
        self.days_spin = ttk.Spinbox(control_frame, from_=1, to=14, width=5)
        self.days_spin.set(7)
        self.days_spin.pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="🍽 Servings per Meal:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=8)
        self.servings_spin = ttk.Spinbox(control_frame, from_=1, to=10, width=5)
        self.servings_spin.set(2)
        self.servings_spin.pack(side=tk.LEFT, padx=5)

        self.breakfast_var = tk.BooleanVar(value=True)
        self.lunch_var = tk.BooleanVar(value=True)
        self.dinner_var = tk.BooleanVar(value=True)

        ttk.Label(control_frame, text="Include:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(control_frame, text="🍳 Breakfast", variable=self.breakfast_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="🥗 Lunch", variable=self.lunch_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(control_frame, text="🍽 Dinner", variable=self.dinner_var).pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="✨ Generate Meal Plan", command=self.generate_plan).pack(side=tk.LEFT, padx=15)
        ttk.Button(control_frame, text="🗑 Clear Plan", command=self.clear_plan).pack(side=tk.LEFT, padx=5)

        # Meal plan display
        plan_frame = ttk.Frame(tab)
        plan_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.plan_text = scrolledtext.ScrolledText(
            plan_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('Arial', 11),
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
        control_frame.pack(fill=tk.X, padx=15, pady=15)

        self.deduct_pantry_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="✓ Deduct items already in pantry",
                       variable=self.deduct_pantry_var).pack(side=tk.LEFT, padx=8)

        ttk.Button(control_frame, text="🛒 Generate Shopping List", command=self.generate_grocery_list).pack(side=tk.LEFT, padx=15)

        # Export section
        ttk.Label(control_frame, text="Export as:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=8)
        ttk.Button(control_frame, text="📄 Text", command=lambda: self.export_grocery('txt')).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="📝 Markdown", command=lambda: self.export_grocery('md')).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="📋 JSON", command=lambda: self.export_grocery('json')).pack(side=tk.LEFT, padx=2)

        # Grocery list display
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.grocery_text = scrolledtext.ScrolledText(
            list_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=('Arial', 11),
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
        left_frame = ttk.LabelFrame(tab, text="➕ Add or Update Item", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(left_frame, text="Ingredient Name:", font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=8)
        self.pantry_ingredient = ttk.Entry(left_frame, width=30)
        self.pantry_ingredient.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(left_frame, text="Quantity:", font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=8)
        self.pantry_quantity = ttk.Entry(left_frame, width=15)
        self.pantry_quantity.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(left_frame, text="Unit (e.g., cups, lbs):", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=8)
        self.pantry_unit = ttk.Entry(left_frame, width=15)
        self.pantry_unit.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=15)

        ttk.Button(btn_frame, text="➕ Add to Pantry", command=self.add_pantry).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Update Quantity", command=self.update_pantry).pack(side=tk.LEFT, padx=5)

        # Right panel - Pantry list
        right_frame = ttk.Frame(tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(right_frame, text="🏺 Your Pantry Inventory", font=('Arial', 14, 'bold')).pack(pady=10)

        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.pantry_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=('Arial', 11),
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

        ttk.Button(right_frame, text="🗑 Remove Selected Item", command=self.remove_pantry).pack(pady=5)
        ttk.Button(right_frame, text="🔄 Refresh List", command=self.refresh_pantry).pack(pady=5)

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

    # ==================== Help & Info Tab ====================

    def create_help_tab(self):
        """Create the help and information tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ℹ️ Help & Info")

        # Content
        content = scrolledtext.ScrolledText(
            tab,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['fg_primary'],
            padx=20,
            pady=20,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.COLORS['border']
        )
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Help text content
        help_text = """👨‍🍳 MEAL PLANNER & GROCERY LIST GENERATOR - USER GUIDE

═══════════════════════════════════════════════════════════════════════

📖 WHAT THIS APP DOES

This application helps you:
  ✓ Store and organize your favorite recipes
  ✓ Generate weekly meal plans automatically
  ✓ Create shopping lists based on your meal plan
  ✓ Track your pantry inventory
  ✓ Export recipes to PDF for easy sharing and printing
  ✓ Organize recipes by meal type (breakfast, lunch, dinner, snack)
  ✓ Filter recipes by dietary preferences


═══════════════════════════════════════════════════════════════════════

📚 RECIPES TAB - How to Use

ADD NEW RECIPES:
  1. Click "➕ Add New Recipe" button
  2. Fill in recipe details (name, meal type, servings, etc.)
  3. Add ingredients one per line (e.g., "2 cups flour" or "1 lb chicken, diced")
  4. Add cooking instructions
  5. Click "Save Recipe"

VIEW RECIPE DETAILS:
  • Click on any recipe in the list to see full details
  • Use the filter dropdown to show only specific meal types

DELETE RECIPES:
  1. Select a recipe from the list
  2. Click "🗑 Delete Recipe"
  3. Confirm deletion

EXPORT RECIPES TO PDF:
  • Click "📄 Export to PDF" to save recipes as a PDF file
  • The export will include all recipes shown in the current filter
  • PDFs are perfect for printing or sharing with friends!


═══════════════════════════════════════════════════════════════════════

📅 MEAL PLAN TAB - How to Use

GENERATE A MEAL PLAN:
  1. Set the number of days (1-14 days)
  2. Set servings per meal
  3. Check which meals to include (Breakfast, Lunch, Dinner)
  4. Click "✨ Generate Meal Plan"

The app will:
  • Randomly select recipes from your collection
  • Create a balanced meal plan with variety
  • Show total cooking time for each meal
  • Display all meals organized by day

CLEAR MEAL PLAN:
  • Click "🗑 Clear Plan" to start over


═══════════════════════════════════════════════════════════════════════

🛒 GROCERY LIST TAB - How to Use

GENERATE SHOPPING LIST:
  1. First, create a meal plan in the Meal Plan tab
  2. Go to Grocery List tab
  3. Check "✓ Deduct items already in pantry" if you want to subtract pantry items
  4. Click "🛒 Generate Shopping List"

The app will:
  • Combine all ingredients from your meal plan
  • Group items by category (Produce, Dairy, Meat, etc.)
  • Show quantities needed for each item
  • Subtract items you already have in your pantry (if checked)

EXPORT GROCERY LIST:
  • 📄 Text - Plain text file for printing
  • 📝 Markdown - Formatted markdown file
  • 📋 JSON - Structured data file


═══════════════════════════════════════════════════════════════════════

🏺 PANTRY TAB - How to Use

ADD ITEMS TO PANTRY:
  1. Enter ingredient name
  2. Enter quantity
  3. Enter unit (cups, lbs, oz, etc.)
  4. Click "➕ Add to Pantry"

UPDATE QUANTITIES:
  • Use the same form to update existing items
  • Click "🔄 Update Quantity"

REMOVE ITEMS:
  1. Select an item from the list
  2. Click "🗑 Remove Selected Item"

WHY USE PANTRY?
  • Track what you already have
  • Avoid buying duplicate items
  • Reduce food waste
  • Save money on groceries


═══════════════════════════════════════════════════════════════════════

✅ WHAT THIS APP HAS

  ✓ 8 Pre-loaded everyday recipes (breakfast, lunch, dinner, snacks)
  ✓ Beautiful cream-themed interface
  ✓ Recipe management (add, view, delete, export)
  ✓ Automatic meal planning for up to 14 days
  ✓ Smart grocery list generation
  ✓ Pantry inventory tracking
  ✓ PDF export for recipes
  ✓ Multiple export formats for grocery lists
  ✓ Recipe filtering by meal type
  ✓ Dietary tags support (vegetarian, vegan, etc.)
  ✓ Ingredient categorization
  ✓ Local database storage (all data saved on your computer)


═══════════════════════════════════════════════════════════════════════

❌ WHAT THIS APP DOES NOT HAVE

  ✗ Internet/cloud sync - All data is stored locally on your computer
  ✗ Recipe sharing between users - PDF export only
  ✗ Nutrition calculations - No calorie or macro tracking
  ✗ Recipe import from websites - Manual entry only
  ✗ Mobile app - Desktop application only
  ✗ Barcode scanning for pantry items
  ✗ Price tracking or budget features
  ✗ Integration with online grocery stores
  ✗ Recipe rating or reviews
  ✗ Cooking timers or reminders
  ✗ Photo uploads for recipes
  ✗ Meal prep scheduling
  ✗ PDF import for recipes (PDF export only)


═══════════════════════════════════════════════════════════════════════

💡 TIPS & BEST PRACTICES

RECIPE TIPS:
  • Be specific with ingredient quantities and units
  • Include preparation notes (e.g., "diced", "chopped", "sliced")
  • Write clear, numbered instructions
  • Add dietary tags to make filtering easier

MEAL PLANNING TIPS:
  • Start with 7 days for a weekly plan
  • Add more recipes to get more variety in meal plans
  • Adjust servings based on household size
  • Review your pantry before generating grocery lists

PANTRY TIPS:
  • Keep pantry updated for accurate grocery lists
  • Use consistent units (don't mix cups and ounces for same item)
  • Remove expired items regularly
  • Add common staples (flour, sugar, oil, etc.)

GROCERY LIST TIPS:
  • Always generate a new list after changing your meal plan
  • Check pantry items before shopping
  • Export to Text format for easy printing
  • Export to Markdown for digital note-taking apps


═══════════════════════════════════════════════════════════════════════

🔧 TECHNICAL INFORMATION

DATA STORAGE:
  • All recipes, meal plans, and pantry items are stored in a local SQLite database
  • Database location: data/meal_planner.db (in application folder)
  • Your data is private and never leaves your computer

REQUIREMENTS:
  • Python 3.7 or higher
  • reportlab library (for PDF export)
  • SQLite (included with Python)

BACKUP YOUR DATA:
  • Copy the entire "data" folder to backup your recipes
  • Export recipes to PDF for additional backup


═══════════════════════════════════════════════════════════════════════

❓ FREQUENTLY ASKED QUESTIONS

Q: Why can't I import recipes from PDF files?
A: PDF is designed for viewing, not for importing structured data. You can only export
   to PDF. To add recipes, use the "➕ Add New Recipe" button.

Q: Can I share my recipes with friends?
A: Yes! Export your recipes to PDF and share the PDF file. Recipients can read the
   recipes but will need to manually add them to their own app.

Q: How do I backup my recipes?
A: Copy the "data" folder from the application directory, or export all recipes to
   PDF for a readable backup.

Q: Can I use this app on multiple computers?
A: The app doesn't sync automatically. You can copy the "data" folder to move your
   recipes between computers.

Q: Why isn't my grocery list showing all ingredients?
A: Make sure you've generated a meal plan first. The grocery list is based on your
   current meal plan.

Q: How do I add recipes from websites?
A: Currently, you need to manually copy and paste recipe information into the
   "Add New Recipe" form. There's no automatic import feature.


═══════════════════════════════════════════════════════════════════════

📞 NEED HELP?

If you encounter any issues or have questions:
  • Review this Help & Info tab
  • Check that all required libraries are installed
  • Verify your database file exists in the data folder
  • Make sure you have write permissions in the application folder


═══════════════════════════════════════════════════════════════════════

🎉 ENJOY YOUR MEAL PLANNING!

This app is designed to make meal planning and grocery shopping easier. Start by
exploring the 8 pre-loaded recipes, add your own favorites, and generate your first
meal plan. Happy cooking! 👨‍🍳

"""

        content.insert(1.0, help_text)
        content.config(state='disabled')  # Make it read-only


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    app = MealPlannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
