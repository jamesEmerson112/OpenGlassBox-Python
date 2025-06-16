#!/usr/bin/env python3
"""
Main entry point for the OpenGlassBox Python demo.
This file mirrors the functionality of demo/src/main.cpp in the C++ implementation.
"""

import sys
import os
import argparse

def main():
    """Main entry point for the OpenGlassBox demo."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='OpenGlassBox Simulation Demo')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging for agents and other components')
    args = parser.parse_args()

    # Set global debug flag
    if args.debug:
        os.environ['OPENGLASSBOX_DEBUG'] = '1'
        print("🐛 Debug mode enabled - agent debug logging activated")

    # Set up paths
    # 1. Add the current directory (demo/src) to path for local imports
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    # 2. Add the project root to path for src package imports
    python_root = os.path.abspath(os.path.join(script_dir, '../../'))
    if python_root not in sys.path:
        sys.path.insert(0, python_root)

    # Import the demo using direct import (not package import)
    print("Starting OpenGlassBox Demo...")
    from demo import GlassBoxDemo

    # Create the demo object
    demo = GlassBoxDemo(1024, 768, "OpenGlassBox Simulation")

    # Try to initialize with TestCity.txt using absolute path
    simfile = os.path.abspath(os.path.join(script_dir, "../data/Simulations/TestCity.txt"))
    print(f"Attempting to initialize simulation with {simfile}")
    if not demo.init_demo_cities(simfile):
        print(f"Failed to initialize simulation with {simfile}")
        print("Exiting (no fallback to hardcoded setup).")
        sys.exit(1)

    # Run the demo
    demo.run()


if __name__ == "__main__":
    main()
