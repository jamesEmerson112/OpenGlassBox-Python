#!/usr/bin/env python3
"""
Main entry point for the OpenGlassBox Python demo.
This file mirrors the functionality of demo/src/main.cpp in the C++ implementation.
"""

import sys
import os

def main():
    """Main entry point for the OpenGlassBox demo."""
    # Set up paths - add the main python directory to sys.path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_root = os.path.abspath(os.path.join(script_dir, '../../'))
    if python_root not in sys.path:
        sys.path.insert(0, python_root)

    # Import the demo
    print("Starting OpenGlassBox Demo...")
    from demo.src.demo import GlassBoxDemo

    # Create the demo object
    demo = GlassBoxDemo(1024, 768, "OpenGlassBox Simulation")

    # Try to initialize with TestCity.txt, matching C++ logic
    simfile = "demo/data/Simulations/TestCity.txt"
    print(f"Attempting to initialize simulation with {simfile}")
    if not demo.init_demo_cities(simfile):
        print(f"Failed to initialize simulation with {simfile}")
        print("Exiting (no fallback to hardcoded setup).")
        sys.exit(1)

    # Run the demo
    demo.run()


if __name__ == "__main__":
    main()
