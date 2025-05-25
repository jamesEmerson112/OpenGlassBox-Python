#!/usr/bin/env python3
"""
Run script for OpenGlassBox demo using Pygame.

This script handles the setup and execution of the OpenGlassBox demo application.
It ensures pygame is installed and properly configured before running the demo.
"""

import os
import sys
import subprocess
import importlib.util

def check_package(package_name):
    """Check if a package is installed, and install it if not."""
    if importlib.util.find_spec(package_name) is None:
        print(f"{package_name} is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} has been installed successfully.")
    else:
        print(f"{package_name} is already installed.")

def main():
    """Main entry point for the run script."""
    # Add the parent directory to path so we can import from the python package
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    # Check for required packages
    check_package("pygame")

    # Import and run the demo
    print("Starting OpenGlassBox demo...")

    try:
        from python.demo import main as demo_main
        demo_main()
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
