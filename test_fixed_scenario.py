#!/usr/bin/env python3
"""
Test the fixed TestCity scenario with sustainable economy.
"""

import sys
import os

# Add the main python directory to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from src.simulation import Simulation
from src.vector import Vector3f

def test_fixed_scenario():
    """Test the fixed scenario with sustainable economy."""
    print("=== Testing Fixed TestCity Scenario ===")
    
    # Create simulation
    simulation = Simulation(12, 12)
    
    # Parse the FIXED TestCity.txt file
    simfile = "demo/data/Simulations/TestCityFixed.txt"
    print(f"\n1. Parsing fixed simulation file: {simfile}")
    if not simulation.parse(simfile):
        print(f"FAILED to parse {simfile}")
        return False
    
    # Create a test city
    print(f"\n2. Creating test city...")
    paris = simulation.add_city("Paris", Vector3f(400.0, 200.0, 0.0))
    
    # Get types
    grass_type = simulation.get_map_type("Grass")
    water_type = simulation.get_map_type("Water")
    road_type = simulation.get_path_type("Road")
    dirt_type = simulation.get_way_type("Dirt")
    home_type = simulation.get_unit_type("Home")
    work_type = simulation.get_unit_type("Work")
    
    # Add maps
    paris_grass = paris.add_map(grass_type)
    paris_water = paris.add_map(water_type)
    
    # Add a simple straight path
    road = paris.add_path(road_type)
    n1 = road.add_node(Vector3f(100.0, 100.0, 0.0))  # Home end
    n2 = road.add_node(Vector3f(200.0, 100.0, 0.0))  # Work end
    w1 = road.add_way(dirt_type, n1, n2)
    
    # Add one Home and one Work unit
    home_unit = paris.add_unit_on_way(home_type, road, w1, 0.1)  # Near start
    work_unit = paris.add_unit_on_way(work_type, road, w1, 0.9)  # Near end
    
    print(f"✓ Created city with {len(paris.units())} units")
    
    # Check the rules in the fixed version
    print(f"\n3. Examining fixed rules:")
    print(f"   Home unit rules: {len(home_type.rules)}")
    for i, rule in enumerate(home_type.rules):
        print(f"     - Rule {i}: '{rule.type()}' rate={rule.rate()}")
    
    print(f"   Work unit rules: {len(work_type.rules)}")
    for i, rule in enumerate(work_type.rules):
        print(f"     - Rule {i}: '{rule.type()}' rate={rule.rate()}")
    
    # Initialize water in the map (for the SendPeopleToHome condition)
    print(f"\n4. Initializing water resources...")
    for u in range(paris_water.grid_size_u()):
        for v in range(paris_water.grid_size_v()):
            paris_water.add_resource(u, v, 80)  # Set water > 70
    print(f"✓ Set water levels to 80 (above the required 70)")
    
    # Track state over many ticks to see if it's sustainable
    print(f"\n5. Simulating over 300 ticks to test sustainability...")
    
    for tick in range(300):
        # Record state before update
        home_people = sum(res.get_amount() for res in home_unit.resources().container() if res.type() == "People")
        work_people = sum(res.get_amount() for res in work_unit.resources().container() if res.type() == "People")
        num_agents = len(paris.agents())
        
        # Run one simulation step
        simulation.update(0.016)  # ~60 FPS delta time
        
        # Record state after update
        new_home_people = sum(res.get_amount() for res in home_unit.resources().container() if res.type() == "People")
        new_work_people = sum(res.get_amount() for res in work_unit.resources().container() if res.type() == "People")
        new_num_agents = len(paris.agents())
        
        # Report changes and periodic status
        if (home_people != new_home_people or 
            work_people != new_work_people or 
            num_agents != new_num_agents or 
            tick % 50 == 0):  # Report every 50 ticks
            
            sim_tick = simulation.get_total_ticks()
            print(f"Tick {sim_tick:3d}: Home People: {new_home_people}, Work People: {new_work_people}, Agents: {new_num_agents}")
            
            if num_agents != new_num_agents:
                if new_num_agents > num_agents:
                    print(f"    → Agent SPAWNED")
                else:
                    print(f"    → Agent ARRIVED at destination")
            
            if home_people != new_home_people:
                if new_home_people < home_people:
                    print(f"    → Home lost People ({home_people} -> {new_home_people})")
                else:
                    print(f"    → Home gained People ({home_people} -> {new_home_people})")
            
            if work_people != new_work_people:
                if new_work_people < work_people:
                    print(f"    → Work lost People ({work_people} -> {new_work_people})")
                else:
                    print(f"    → Work gained People ({work_people} -> {new_work_people})")
    
    # Final summary
    final_home = sum(res.get_amount() for res in home_unit.resources().container() if res.type() == "People")
    final_work = sum(res.get_amount() for res in work_unit.resources().container() if res.type() == "People")
    final_agents = len(paris.agents())
    
    print(f"\n6. Final State Summary:")
    print(f"   - Home People: {final_home}")
    print(f"   - Work People: {final_work}")
    print(f"   - Active Agents: {final_agents}")
    print(f"   - Total People in system: {final_home + final_work + final_agents}")
    
    if final_home + final_work + final_agents > 0:
        print("✓ SUCCESS: Economy is sustainable - People are still in the system!")
    else:
        print("✗ FAILURE: Economy collapsed - all People depleted!")

if __name__ == "__main__":
    test_fixed_scenario()
