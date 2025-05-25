#!/usr/bin/env python3
"""
Script to fix import statements in the tests directory.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single test file."""
    print(f"Processing {file_path}...")

    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content

    # Fix specific import issues found in the tests
    replacements = [
        # Fix the old-style imports to src package imports
        (r'^from simulation import', 'from src.simulation import'),
        (r'^from city import', 'from src.city import'),
        (r'^from map import', 'from src.map import'),
        (r'^from path import', 'from src.path import'),
        (r'^from unit import', 'from src.unit import'),
        (r'^from agent import', 'from src.agent import'),
        (r'^from resources import', 'from src.resources import'),
        (r'^from resource import', 'from src.resource import'),
        (r'^from vector import', 'from src.vector import'),
        (r'^from node import', 'from src.node import'),
        (r'^from dijkstra import', 'from src.dijkstra import'),
        (r'^from script_parser import', 'from src.script_parser import'),
        (r'^from rule import', 'from src.rule import'),
        (r'^from rule_command import', 'from src.rule_command import'),
        (r'^from rule_value import', 'from src.rule_value import'),
        (r'^import simulation', 'from src import simulation'),
        (r'^from map_coordinates_inside_radius import', 'from src.map_coordinates_inside_radius import'),

        # Fix specific name changes
        (r'from src\.rule_value import RuleValue', 'from src.rule_value import IRuleValue as RuleValue'),
        (r'from src\.rule import RuleType', 'from src.rule import RuleMapType, RuleUnitType'),

        # Fix relative imports that shouldn't be relative in tests
        (r'^from \.debug_ui import', 'import debug_ui'),
        (r'^from \.([a-z_]+) import', r'from \1 import'),

        # Fix demo imports
        (r'^from demo import', 'from demo.src.demo import'),
        (r'GlassBoxDemo as BasicDemo', 'GlassBoxDemo as BasicDemo'),

        # Fix performance benchmark imports
        (r'^from simulation import Simulation, TICKS_PER_SECOND', 'from src.simulation import Simulation'),
    ]

    # Apply all replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Write back if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  Updated {file_path}")
        return True
    else:
        print(f"  No changes needed for {file_path}")
        return False

def main():
    """Main function to process all Python files in tests directory."""
    tests_dir = Path("tests")

    if not tests_dir.exists():
        print("tests directory not found!")
        return

    python_files = list(tests_dir.glob("test_*.py"))
    if not python_files:
        print("No test files found in tests directory!")
        return

    print(f"Found {len(python_files)} test files to process...")

    updated_count = 0
    for py_file in python_files:
        if fix_imports_in_file(py_file):
            updated_count += 1

    print(f"\nCompleted! Updated {updated_count} out of {len(python_files)} files.")

if __name__ == "__main__":
    main()
