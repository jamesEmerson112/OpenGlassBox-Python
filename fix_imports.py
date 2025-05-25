#!/usr/bin/env python3
"""
Script to fix import statements in the src package to use relative imports.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file."""
    print(f"Processing {file_path}...")

    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content

    # List of modules that should be relative imports within src package
    src_modules = [
        'agent', 'city', 'dijkstra', 'map', 'map_coordinates_inside_radius',
        'map_random_coordinates', 'node', 'path', 'resource', 'resources',
        'rule', 'rule_command', 'rule_value', 'script_parser', 'simulation',
        'unit', 'vector'
    ]

    # Fix imports for each module
    for module in src_modules:
        # Pattern: from module import ...
        pattern1 = rf'^from {module} import'
        replacement1 = rf'from .{module} import'
        content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)

        # Pattern: import module (standalone import)
        pattern2 = rf'^import {module}$'
        replacement2 = rf'from . import {module}'
        content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)

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
    """Main function to process all Python files in src directory."""
    src_dir = Path("src")

    if not src_dir.exists():
        print("src directory not found!")
        return

    python_files = list(src_dir.glob("*.py"))
    if not python_files:
        print("No Python files found in src directory!")
        return

    print(f"Found {len(python_files)} Python files to process...")

    updated_count = 0
    for py_file in python_files:
        if fix_imports_in_file(py_file):
            updated_count += 1

    print(f"\nCompleted! Updated {updated_count} out of {len(python_files)} files.")

if __name__ == "__main__":
    main()
