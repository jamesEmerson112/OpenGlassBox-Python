"""
Enhanced demo application for OpenGlassBox simulation engine using Pygame.

This module implements a visualization for the simulation engine with advanced
debug UI capabilities, allowing users to observe and interact with simulated
cities, paths, units, and agents. Based on the C++ demo implementation with
Dear ImGui-style debug panels.
"""

import os
import sys
import time
import pygame
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field

from simulation import Simulation
from city import City
from map import Map
from path import Path, Node, Way
from unit import Unit
from agent import Agent
from script_parser import Script
from vector import Vector3f
from debug_ui import DebugUI

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

# Convert hex color to RGB tuple
def hex_to_rgb(hex_color: int) -> Tuple[int, int, int]:
    """Convert a hex color (0xRRGGBB) to an RGB tuple."""
    r = (hex_color >> 16) & 0xFF
    g = (hex_color >> 8) & 0xFF
    b = hex_color & 0xFF
    return (r, g, b)

class GlassBoxDemo:
    """
    Enhanced demo application for visualizing OpenGlassBox simulations.

    This class handles rendering and user interaction for the simulation,
    with advanced debug UI capabilities matching the C++ Dear ImGui interface.
    """

    def __init__(self, width: int = 800, height: int = 600, title: str = "OpenGlassBox Demo"):
        """
        Initialize the demo application.

        Args:
            width: Window width in pixels
            height: Window height in pixels
            title: Window title
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)
        self.running = True
        self.paused = True

        # Simulation components
        self.simulation = Simulation(12, 12)  # Match C++ demo: 12x12 grid
        self.script_parser = Script()
        self.city_names = []
        self.selected_city_index = 0

        # Camera/view settings
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.zoom = 2.0  # Smaller zoom to see both cities

        # Debug system - matches C++ Dear ImGui functionality
        self.debug_ui = DebugUI(self.font)
        self.show_debug = False  # Start with debug hidden, press 'D' to show
        self.show_maps = True
        self.show_paths = True
        self.show_units = True
        self.show_agents = True

        # Input state
        self.mouse_x = 0
        self.mouse_y = 0
        self.dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        # Set up simulation listeners
        self.setup_listeners()

        print("Controls:")
        print("- Press SPACE to pause/unpause simulation")
        print("- Press D to show/hide debug panel (matches C++ 'D' key)")
        print("- Press M/P/U/A to toggle Maps/Paths/Units/Agents")
        print("- Press R to reset camera view")
        print("- Mouse wheel to zoom, drag to pan")
        print("- ESC to exit")

    def setup_listeners(self):
        """Set up event listeners for simulation components."""

        # City listener to track entity changes
        class CityListener(City.Listener):
            def __init__(self, demo):
                super().__init__()
                self.demo = demo

            def on_map_added(self, map_obj):
                print(f"Map added: {map_obj.type()}")

            def on_map_removed(self, map_obj):
                print(f"Map removed: {map_obj.type()}")

            def on_path_added(self, path):
                print(f"Path added: {path.type()}")

            def on_path_removed(self, path):
                print(f"Path removed: {path.type()}")

            def on_unit_added(self, unit):
                print(f"Unit added: {unit.type()}")

            def on_unit_removed(self, unit):
                print(f"Unit removed: {unit.type()}")

            def on_agent_added(self, agent):
                print(f"Agent added: {agent.type()}")

            def on_agent_removed(self, agent):
                print(f"Agent removed: {agent.type()}")

        # Simulation listener to track city changes
        class SimulationListener(Simulation.Listener):
            def __init__(self, demo):
                super().__init__()
                self.demo = demo

            def on_city_added(self, city):
                print(f"City added: {city.name()}")
                self.demo.city_names.append(city.name())
                # Set city listener
                city.set_listener(CityListener(self.demo))

            def on_city_removed(self, city):
                print(f"City removed: {city.name()}")
                if city.name() in self.demo.city_names:
                    self.demo.city_names.remove(city.name())

        # Set simulation listener
        self.simulation.set_listener(SimulationListener(self))

    def load_simulation(self, filename: str) -> bool:
        """
        Load a simulation from a script file and create cities like C++ demo.

        Args:
            filename: Path to the simulation script file

        Returns:
            True if loading succeeded, False otherwise
        """
        print(f"Loading simulation from {filename}...")
        if not self.script_parser.parse(filename):
            print(f"Failed to parse script {filename}")
            return False

        # Reset simulation
        self.simulation = Simulation(12, 12)  # Match C++ demo
        self.setup_listeners()

        # Parse script types to get the definitions
        from map import MapType
        from path import PathType, WayType
        from unit import UnitType

        # Get types from script
        road_type = None
        dirt_type = None
        home_type = None
        work_type = None
        grass_type = None
        water_type = None

        for name, path_type in self.script_parser.m_pathTypes.items():
            if name == "Road":
                road_type = PathType(path_type.name, path_type.color)

        for name, segment_type in self.script_parser.m_segmentTypes.items():
            if name == "Dirt":
                dirt_type = WayType(segment_type.name, segment_type.color)

        for name, unit_type in self.script_parser.m_unitTypes.items():
            if name == "Home":
                home_type = UnitType(unit_type.name, unit_type.color)
            elif name == "Work":
                work_type = UnitType(unit_type.name, unit_type.color)

        for name, map_type in self.script_parser.m_mapTypes.items():
            if name == "Grass":
                grass_type = MapType(map_type.name, map_type.color, map_type.capacity)
            elif name == "Water":
                water_type = MapType(map_type.name, map_type.color, map_type.capacity)

        # Create Paris city (matches C++ demo exactly)
        paris = self.simulation.add_city("Paris", Vector3f(400.0, 200.0, 0.0))
        paris.set_listener(CityListener(self))

        # Add maps to Paris
        if grass_type:
            paris_grass = paris.add_map(grass_type)
            # Add some grass resources
            for u in range(0, 12, 2):
                for v in range(0, 12, 2):
                    paris_grass.set_resource(u, v, 8)

        if water_type:
            paris_water = paris.add_map(water_type)
            # Add some water resources
            for u in range(1, 12, 3):
                for v in range(1, 12, 3):
                    paris_water.set_resource(u, v, 50)

        # Add road and nodes to Paris
        if road_type:
            road = paris.add_path(road_type)
            n1 = road.add_node(Vector3f(60.0, 60.0, 0.0) + paris.position())
            n2 = road.add_node(Vector3f(300.0, 300.0, 0.0) + paris.position())
            n3 = road.add_node(Vector3f(60.0, 300.0, 0.0) + paris.position())

            if dirt_type:
                w1 = road.add_way(dirt_type, n1, n2)
                w2 = road.add_way(dirt_type, n2, n3)
                w3 = road.add_way(dirt_type, n3, n1)

                # Add units to Paris
                if home_type:
                    u1 = paris.add_unit(home_type, road, w1, 0.66)
                    u2 = paris.add_unit(home_type, road, w1, 0.5)
                if work_type:
                    u3 = paris.add_unit(work_type, road, w2, 0.5)
                    u4 = paris.add_unit(work_type, road, w3, 0.5)

        # Create Versailles city (matches C++ demo exactly)
        versailles = self.simulation.add_city("Versailles", Vector3f(0.0, 30.0, 0.0))
        versailles.set_listener(CityListener(self))

        # Add maps to Versailles
        if grass_type:
            vers_grass = versailles.add_map(grass_type)
            # Add some grass resources
            for u in range(0, 12, 3):
                for v in range(0, 12, 3):
                    vers_grass.set_resource(u, v, 6)

        if water_type:
            vers_water = versailles.add_map(water_type)
            # Add some water resources
            for u in range(2, 12, 4):
                for v in range(2, 12, 4):
                    vers_water.set_resource(u, v, 40)

        # Add road and nodes to Versailles
        if road_type:
            road2 = versailles.add_path(road_type)
            n4 = road2.add_node(Vector3f(40.0, 20.0, 0.0) + versailles.position())
            n5 = road2.add_node(Vector3f(300.0, 300.0, 0.0) + versailles.position())

            if dirt_type:
                w4 = road2.add_way(dirt_type, n4, n5)
                # Connect to Paris (n1 from Paris)
                if road_type and dirt_type:
                    w5 = road2.add_way(dirt_type, n5, n1)  # Connect to Paris

                # Add units to Versailles
                if home_type and work_type:
                    u5 = versailles.add_unit(home_type, road, w5, 0.1)
                    u6 = versailles.add_unit(work_type, road2, w4, 0.9)

        print("Simulation loaded successfully")
        return True

    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """
        Convert world coordinates to screen coordinates.

        Args:
            world_x: X coordinate in world space
            world_y: Y coordinate in world space

        Returns:
            Tuple of (screen_x, screen_y) coordinates
        """
        screen_x = int((world_x * self.zoom) + self.width / 2 + self.camera_offset_x)
        screen_y = int((world_y * self.zoom) + self.height / 2 + self.camera_offset_y)
        return (screen_x, screen_y)

    def screen_to_world(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """
        Convert screen coordinates to world coordinates.

        Args:
            screen_x: X coordinate on screen
            screen_y: Y coordinate on screen

        Returns:
            Tuple of (world_x, world_y) coordinates
        """
        world_x = (screen_x - self.width / 2 - self.camera_offset_x) / self.zoom
        world_y = (screen_y - self.height / 2 - self.camera_offset_y) / self.zoom
        return (world_x, world_y)

    def draw_maps(self, city: City, surface: pygame.Surface):
        """
        Draw all maps in the city.

        Args:
            city: The city containing maps to draw
            surface: The surface to draw on
        """
        if not self.show_maps:
            return

        for map_name, map_obj in city.maps().items():
            pos = map_obj.position()
            grid_size_u = map_obj.grid_size_u()
            grid_size_v = map_obj.grid_size_v()
            cell_size = max(1, int(self.zoom * 5))  # Make cells visible

            # Draw cells with resources
            for u in range(grid_size_u):
                for v in range(grid_size_v):
                    # Get resource at cell
                    resource_amount = map_obj.get_resource(u, v)
                    if resource_amount > 0:
                        # Calculate world position for this cell
                        cell_world_x = pos.x + u * 10  # Scale up cell size
                        cell_world_y = pos.y + v * 10

                        # Convert to screen coordinates
                        screen_x, screen_y = self.world_to_screen(cell_world_x, cell_world_y)

                        # Scale color intensity based on resource amount
                        color = hex_to_rgb(map_obj.color())
                        intensity = min(255, int(resource_amount / map_obj.get_capacity() * 255))
                        cell_color = (
                            min(255, color[0] + intensity // 3),
                            min(255, color[1] + intensity // 3),
                            min(255, color[2] + intensity // 3)
                        )

                        # Draw filled rectangle for cell
                        pygame.draw.rect(surface, cell_color,
                                       (screen_x, screen_y, cell_size, cell_size))

    def draw_paths(self, city: City, surface: pygame.Surface):
        """
        Draw all paths, nodes, and ways in the city.

        Args:
            city: The city containing paths to draw
            surface: The surface to draw on
        """
        if not self.show_paths:
            return

        for path_name, path in city.paths().items():
            # Draw ways first (connections between nodes)
            for way in path.ways():
                from_pos = way.position1()
                to_pos = way.position2()
                from_x, from_y = self.world_to_screen(from_pos.x, from_pos.y)
                to_x, to_y = self.world_to_screen(to_pos.x, to_pos.y)

                # Get way color and draw line
                color = hex_to_rgb(way.color())
                pygame.draw.line(surface, color, (from_x, from_y), (to_x, to_y), 2)

            # Then draw nodes on top
            for i, node in enumerate(path.nodes()):
                pos = node.position()
                x, y = self.world_to_screen(pos.x, pos.y)

                # Draw node circle
                pygame.draw.circle(surface, WHITE, (x, y), 6)
                pygame.draw.circle(surface, BLACK, (x, y), 4)

                # Draw node ID
                text = self.font.render(str(i), True, WHITE)
                surface.blit(text, (x + 8, y - 8))

    def draw_units(self, city: City, surface: pygame.Surface):
        """
        Draw all units in the city.

        Args:
            city: The city containing units to draw
            surface: The surface to draw on
        """
        if not self.show_units:
            return

        for unit in city.units():
            # Get unit position
            pos = unit.position()
            x, y = self.world_to_screen(pos.x, pos.y)

            # Draw unit box
            color = hex_to_rgb(unit.color())
            size = max(8, int(self.zoom * 3))
            pygame.draw.rect(surface, color, (x - size//2, y - size//2, size, size))

    def draw_agents(self, city: City, surface: pygame.Surface):
        """
        Draw all agents in the city.

        Args:
            city: The city containing agents to draw
            surface: The surface to draw on
        """
        if not self.show_agents:
            return

        for agent in city.agents():
            pos = agent.position()
            x, y = self.world_to_screen(pos.x, pos.y)

            # Draw agent triangle
            color = hex_to_rgb(agent.m_type.color)
            size = 6
            points = [
                (x, y - size),
                (x - size, y + size),
                (x + size, y + size)
            ]
            pygame.draw.polygon(surface, color, points)

    def draw_city(self, city: City, surface: pygame.Surface):
        """
        Draw a city and all its components.

        Args:
            city: The city to draw
            surface: The surface to draw on
        """
        # Draw city components in order: maps, paths, units, agents
        self.draw_maps(city, surface)
        self.draw_paths(city, surface)
        self.draw_units(city, surface)
        self.draw_agents(city, surface)

        # Draw city name
        pos = city.position()
        x, y = self.world_to_screen(pos.x, pos.y)
        text = self.font.render(city.name().upper(), True, WHITE)
        surface.blit(text, (x - 50, y - 50))

    def draw_status_ui(self, surface: pygame.Surface):
        """
        Draw status UI elements (framerate, simulation status).

        Args:
            surface: The surface to draw on
        """
        # Draw framerate and simulation stats
        fps = int(self.clock.get_fps())
        text = self.font.render(f"FPS: {fps}", True, WHITE)
        surface.blit(text, (self.width - 100, 10))

        # Draw simulation status
        status = "PAUSED" if self.paused else "RUNNING"
        text = self.font.render(f"Status: {status}", True, WHITE)
        surface.blit(text, (self.width - 200, 10))

        # Show debug mode status
        if self.show_debug:
            text = self.font.render("DEBUG MODE - Press D to hide", True, GREEN)
            surface.blit(text, (self.width - 250, 30))

    def handle_events(self):
        """Handle pygame events like keyboard and mouse input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Handle keyboard input
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    print(f"Simulation {'PAUSED' if self.paused else 'RUNNING'}")
                elif event.key == pygame.K_d:
                    self.show_debug = not self.show_debug
                    self.debug_ui.visible = self.show_debug
                    print(f"Debug panel {'SHOWN' if self.show_debug else 'HIDDEN'}")
                elif event.key == pygame.K_m:
                    self.show_maps = not self.show_maps
                    print(f"Maps {'SHOWN' if self.show_maps else 'HIDDEN'}")
                elif event.key == pygame.K_p:
                    self.show_paths = not self.show_paths
                    print(f"Paths {'SHOWN' if self.show_paths else 'HIDDEN'}")
                elif event.key == pygame.K_u:
                    self.show_units = not self.show_units
                    print(f"Units {'SHOWN' if self.show_units else 'HIDDEN'}")
                elif event.key == pygame.K_a:
                    self.show_agents = not self.show_agents
                    print(f"Agents {'SHOWN' if self.show_agents else 'HIDDEN'}")
                elif event.key == pygame.K_r:
                    # Reset view
                    self.camera_offset_x = 0
                    self.camera_offset_y = 0
                    self.zoom = 2.0
                    print("Camera view reset")

                # Pass key events to debug UI
                if self.show_debug:
                    self.debug_ui.handle_key_press(event.key, self.city_names)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check if debug UI handles the click first
                if self.show_debug and self.debug_ui.handle_click(event.pos, self.city_names):
                    continue  # UI handled the click

                # Handle camera controls
                if event.button == 1:  # Left mouse button
                    self.dragging = True
                    self.last_mouse_x, self.last_mouse_y = event.pos
                elif event.button == 4:  # Mouse wheel up
                    self.zoom *= 1.1
                elif event.button == 5:  # Mouse wheel down
                    self.zoom /= 1.1

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_x, self.mouse_y = event.pos
                if self.dragging and not self.show_debug:  # Don't pan while debug UI is active
                    dx = event.pos[0] - self.last_mouse_x
                    dy = event.pos[1] - self.last_mouse_y
                    self.camera_offset_x += dx
                    self.camera_offset_y += dy
                    self.last_mouse_x, self.last_mouse_y = event.pos

    def update(self, dt: float):
        """
        Update simulation state.

        Args:
            dt: Time delta in seconds
        """
        if not self.paused:
            self.simulation.update()

    def render(self):
        """Render the current simulation state."""
        # Clear screen with dark blue background like C++ demo
        self.screen.fill((50, 50, 100))

        # Draw grid for reference
        grid_size = 50
        for x in range(0, self.width, grid_size):
            pygame.draw.line(self.screen, (70, 70, 120), (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_size):
            pygame.draw.line(self.screen, (70, 70, 120), (0, y), (self.width, y), 1)

        # Draw all cities
        for city in self.simulation.cities():
            self.draw_city(city, self.screen)

        # Draw status UI
        self.draw_status_ui(self.screen)

        # Draw debug UI (if enabled) - this matches C++ Dear ImGui functionality
        if self.show_debug:
            self.debug_ui.draw_debug_panel(self.screen, self.simulation)

        # Flip display
        pygame.display.flip()

    def run(self):
        """Run the main demo loop."""
        last_time = time.time()

        while self.running:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Handle input
            self.handle_events()

            # Update simulation
            self.update(dt)

            # Render
            self.render()

            # Cap frame rate
            self.clock.tick(60)

        pygame.quit()

def main():
    """Main entry point for the enhanced demo application."""
    # Initialize demo with enhanced features
    demo = GlassBoxDemo(1024, 768, "OpenGlassBox Simulation - Enhanced Debug UI")

    # Load test simulation if available
    # Try different possible locations for the simulation file
    possible_paths = [
        os.path.join("data", "simulations", "TestCity.txt"),  # Python-specific path when running from python/ directory
        os.path.join("python", "data", "simulations", "TestCity.txt"),  # Python-specific path when running from project root
        os.path.join("demo", "data", "Simulations", "TestCity.txt"),  # C++ path when running from project root
        os.path.join("..", "demo", "data", "Simulations", "TestCity.txt")  # C++ path when running from python/ directory
    ]

    sim_path = None
    for path in possible_paths:
        if os.path.exists(path):
            sim_path = path
            break

    if sim_path:
        demo.load_simulation(sim_path)
    else:
        print(f"Warning: Could not find simulation file")

        # Create a simple test city if no simulation file
        from city import City
        from map import MapType
        from path import PathType, WayType
        from unit import UnitType
        from vector import Vector3f

        city = City("TestCity")
        demo.simulation.add_city(city, Vector3f(0, 0, 0))

        # Add a map
        water_map = city.add_map(MapType("Water", 0x0000FF, 100))

        # Add a path with nodes and ways
        road = city.add_path(PathType("Road", 0x555555))
        node1 = road.add_node(Vector3f(-50.0, -50.0, 0.0))
        node2 = road.add_node(Vector3f(50.0, -50.0, 0.0))
        node3 = road.add_node(Vector3f(50.0, 50.0, 0.0))
        node4 = road.add_node(Vector3f(-50.0, 50.0, 0.0))

        road.add_way(WayType("Dirt", 0x8B4513), node1, node2)
        road.add_way(WayType("Dirt", 0x8B4513), node2, node3)
        road.add_way(WayType("Dirt", 0x8B4513), node3, node4)
        road.add_way(WayType("Dirt", 0x8B4513), node4, node1)

        # Add a unit
        city.add_unit(UnitType("House", 0xFF0000), node1)

    # Run the demo
    demo.run()

if __name__ == "__main__":
    main()
