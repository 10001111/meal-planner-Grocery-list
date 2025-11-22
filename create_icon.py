#!/usr/bin/env python3
"""Create a simple cooking icon for the application."""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os

    # Create a 256x256 image with transparent background
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a chef hat (simple representation)
    # Hat brim
    draw.ellipse([40, 120, 216, 180], fill=(255, 255, 255, 255))

    # Hat top (puffy part)
    draw.ellipse([60, 40, 140, 120], fill=(255, 255, 255, 255))
    draw.ellipse([116, 40, 196, 120], fill=(255, 255, 255, 255))
    draw.ellipse([88, 20, 168, 100], fill=(255, 255, 255, 255))

    # Add a spoon and fork outline
    # Fork (left side)
    fork_color = (139, 69, 19, 255)  # Brown color
    draw.rectangle([70, 160, 80, 220], fill=fork_color)
    draw.rectangle([65, 160, 85, 170], fill=fork_color)
    draw.line([68, 160, 68, 150], fill=fork_color, width=3)
    draw.line([72, 160, 72, 150], fill=fork_color, width=3)
    draw.line([76, 160, 76, 150], fill=fork_color, width=3)
    draw.line([80, 160, 80, 150], fill=fork_color, width=3)

    # Spoon (right side)
    draw.rectangle([176, 160, 186, 220], fill=fork_color)
    draw.ellipse([168, 145, 194, 171], fill=fork_color)

    # Save as ICO file
    img.save('cooking.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("Icon created successfully: cooking.ico")

except ImportError:
    print("PIL/Pillow not installed. Creating a simple emoji-based icon solution.")
    print("You can install Pillow with: pip install Pillow")
    print("For now, the application will use the default icon.")
except Exception as e:
    print(f"Error creating icon: {e}")
    print("The application will use the default icon.")
