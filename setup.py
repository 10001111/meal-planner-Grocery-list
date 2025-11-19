#!/usr/bin/env python3
"""Setup script for Meal Planner & Grocery List Generator."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="meal-planner-grocery-list",
    version="2.1.0",
    author="Meal Planner Team",
    description="A comprehensive meal planning and grocery list generator with dark theme GUI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/meal-planner-grocery-list",
    py_modules=[
        'main',
        'gui_app',
        'database',
        'models',
        'recipe_manager',
        'meal_planner',
        'grocery_generator',
        'pantry_manager',
        'utils'
    ],
    python_requires=">=3.9",
    install_requires=[
        # No external dependencies required for basic functionality
        # All features use Python standard library
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=0.990',
        ],
        'build': [
            'pyinstaller>=5.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'meal-planner=main:main',
            'meal-planner-gui=gui_app:main',
        ],
        'gui_scripts': [
            'meal-planner-app=gui_app:main',
        ]
    },
    include_package_data=True,
    package_data={
        '': ['sample_recipes.json', 'README.md'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Home Automation",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="meal planning grocery list recipes cooking food",
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/meal-planner-grocery-list/issues',
        'Source': 'https://github.com/yourusername/meal-planner-grocery-list',
    },
)
