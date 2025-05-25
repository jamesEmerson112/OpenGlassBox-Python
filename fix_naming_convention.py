#!/usr/bin/env python3
"""
Script to convert camelCase method names to snake_case in Python files.
This addresses the C++ naming convention that was ported directly.
"""

import os
import re
from pathlib import Path

def camel_to_snake(name):
    """Convert camelCase to snake_case."""
    # Insert an underscore before any uppercase letter that follows a lowercase letter
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return s1.lower()

def fix_method_calls_in_file(file_path):
    """Fix camelCase method calls to snake_case in a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Common camelCase method names to convert
    camel_methods = {
        'addResource': 'add_resource',
        'removeResource': 'remove_resource',
        'findResource': 'find_resource',
        'findOrAddResource': 'find_or_add_resource',
        'addResources': 'add_resources',
        'removeResources': 'remove_resources',
        'canAddSomeResources': 'can_add_some_resources',
        'transferResourcesTo': 'transfer_resources_to',
        'getAmount': 'get_amount',
        'setCapacity': 'set_capacity',
        'setCapacities': 'set_capacities',
        'getCapacity': 'get_capacity',
        'isEmpty': 'is_empty',
        'hasResource': 'has_resource',
        'hasAmount': 'has_amount',
        'transferTo': 'transfer_to',
        'addCity': 'add_city',
        'getCity': 'get_city',
        'getCityConst': 'get_city_const',
        'setListener': 'set_listener',
        'addNode': 'add_node',
        'addWay': 'add_way',
        'addUnit': 'add_unit',
        'splitWay': 'split_way',
        'hasWays': 'has_ways',
        'getWayToNode': 'get_way_to_node',
        'getMapPosition': 'get_map_position',
        'updateMagnitude': 'update_magnitude',
        'executeRules': 'execute_rules',
        'isRandom': 'is_random',
        'nextToken': 'next_token',
        'parseScript': 'parse_script',
        'parseResources': 'parse_resources',
        'parseResource': 'parse_resource',
        'parseResourcesArray': 'parse_resources_array',
        'parseCapacitiesArray': 'parse_capacities_array',
        'parsePaths': 'parse_paths',
        'parsePath': 'parse_path',
        'parseWays': 'parse_ways',
        'parseWay': 'parse_way',
        'parseAgents': 'parse_agents',
        'parseAgent': 'parse_agent',
        'parseRules': 'parse_rules',
        'parseRuleMap': 'parse_rule_map',
        'parseRuleUnit': 'parse_rule_unit',
        'parseCommand': 'parse_command',
        'parseMaps': 'parse_maps',
        'parseMap': 'parse_map',
        'parseUnits': 'parse_units',
        'parseUnit': 'parse_unit',
        'parseStringArray': 'parse_string_array',
        'parseRuleMapArray': 'parse_rule_map_array',
        'parseRuleUnitArray': 'parse_rule_unit_array',
        'getResource': 'get_resource',
        'getPathType': 'get_path_type',
        'getWayType': 'get_way_type',
        'getAgentType': 'get_agent_type',
        'getRuleMap': 'get_rule_map',
        'getRuleUnit': 'get_rule_unit',
        'getUnitType': 'get_unit_type',
        'getMapType': 'get_map_type',
        'relativeCoordinates': 'relative_coordinates',
        'gridSizeU': 'grid_size_u',
        'gridSizeV': 'grid_size_v'
    }

    # Replace method definitions (def methodName)
    for camel, snake in camel_methods.items():
        # Method definitions
        content = re.sub(rf'\bdef {camel}\b', f'def {snake}', content)

        # Method calls with dot notation (object.methodName)
        content = re.sub(rf'\.{camel}\b', f'.{snake}', content)

        # Self method calls (self.methodName)
        content = re.sub(rf'\bself\.{camel}\b', f'self.{snake}', content)

    # Write back if changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {file_path}")
        return True
    return False

def main():
    """Main function to fix naming conventions in all Python files."""
    python_src_dir = Path("src")

    if not python_src_dir.exists():
        print("Error: src directory not found. Run from python/ directory.")
        return

    files_updated = 0
    total_files = 0

    # Process all Python files in src directory
    for py_file in python_src_dir.glob("*.py"):
        total_files += 1
        if fix_method_calls_in_file(py_file):
            files_updated += 1

    # Also process demo files
    demo_dir = Path("demo/src")
    if demo_dir.exists():
        for py_file in demo_dir.glob("*.py"):
            total_files += 1
            if fix_method_calls_in_file(py_file):
                files_updated += 1

    print(f"\nSummary: Updated {files_updated} out of {total_files} Python files")

    if files_updated > 0:
        print("\nNaming convention fixes applied! You may need to:")
        print("1. Run tests to verify everything still works")
        print("2. Update any remaining method calls that weren't caught")
        print("3. Check that demos and tests use the new snake_case names")

if __name__ == "__main__":
    main()
