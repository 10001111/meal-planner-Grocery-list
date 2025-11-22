#!/usr/bin/env python3
"""PDF export functionality for recipes."""

from typing import List, Optional
from pathlib import Path
from models import Recipe
from utils import format_quantity


def export_recipes_to_pdf(recipes: List[Recipe], output_path: str) -> bool:
    """
    Export recipes to a PDF file.

    Args:
        recipes: List of Recipe objects to export
        output_path: Path where PDF should be saved

    Returns:
        True if successful, False otherwise
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        # Container for PDF elements
        story = []

        # Get styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#3E3022',
            spaceAfter=30,
            alignment=TA_CENTER
        )

        recipe_title_style = ParagraphStyle(
            'RecipeTitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor='#3E3022',
            spaceAfter=12,
            spaceBefore=12
        )

        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading3'],
            fontSize=14,
            textColor='#6B5D4F',
            spaceAfter=6,
            spaceBefore=10
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            textColor='#3E3022',
            spaceAfter=6
        )

        # Add document title
        story.append(Paragraph("Recipe Collection", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Add each recipe
        for i, recipe in enumerate(recipes):
            # Recipe title
            story.append(Paragraph(recipe.name, recipe_title_style))

            # Basic info
            info_text = f"<b>Type:</b> {recipe.meal_type.capitalize()} | "
            info_text += f"<b>Servings:</b> {recipe.servings} | "
            info_text += f"<b>Total Time:</b> {recipe.total_time()} minutes"
            if recipe.cuisine:
                info_text += f" | <b>Cuisine:</b> {recipe.cuisine}"
            story.append(Paragraph(info_text, body_style))

            # Dietary tags
            if recipe.dietary_tags:
                tags_text = f"<b>Tags:</b> {', '.join(recipe.dietary_tags)}"
                story.append(Paragraph(tags_text, body_style))

            story.append(Spacer(1, 0.15 * inch))

            # Ingredients section
            story.append(Paragraph("Ingredients", section_style))
            for ing in recipe.ingredients:
                qty = format_quantity(ing.quantity)
                prep = f", {ing.preparation}" if ing.preparation else ""
                ing_text = f"• {qty} {ing.unit} {ing.ingredient_name}{prep}"
                story.append(Paragraph(ing_text, body_style))

            story.append(Spacer(1, 0.15 * inch))

            # Instructions section
            if recipe.instructions:
                story.append(Paragraph("Instructions", section_style))
                # Split instructions by newlines and format
                for line in recipe.instructions.split('\n'):
                    if line.strip():
                        story.append(Paragraph(line, body_style))

            # Add page break between recipes (except for last one)
            if i < len(recipes) - 1:
                story.append(PageBreak())

        # Build PDF
        doc.build(story)
        return True

    except ImportError:
        # reportlab not installed
        raise ImportError(
            "PDF export requires the 'reportlab' library. "
            "Please install it with: pip install reportlab"
        )
    except Exception as e:
        raise Exception(f"Failed to create PDF: {str(e)}")


def export_single_recipe_to_pdf(recipe: Recipe, output_path: str) -> bool:
    """
    Export a single recipe to PDF.

    Args:
        recipe: Recipe object to export
        output_path: Path where PDF should be saved

    Returns:
        True if successful
    """
    return export_recipes_to_pdf([recipe], output_path)
