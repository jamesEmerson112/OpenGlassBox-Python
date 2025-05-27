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
    parser = argparse.ArgumentParser(description='OpenGlassBox Python Demo')
    parser.add_argument('--enhanced', action='store_true',
                        help='Run the enhanced demo with more visualization features')
    args = parser.parse_args()

    # Set up paths - add the main python directory to sys.path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_root = os.path.abspath(os.path.join(script_dir, '../../'))
    if python_root not in sys.path:
        sys.path.insert(0, python_root)

    # Now import the demos after path is set up
    if args.enhanced:
        print("Starting Enhanced OpenGlassBox Demo...")
        from demo.src.demo_enhanced import GlassBoxDemo
    else:
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
