"""
Demo application for OpenGlassBox simulation engine using Pygame.

This module implements a visualization for the simulation engine, allowing
users to observe and interact with simulated cities, paths, units, and agents.
Based on the C++ demo implementation.
"""

import os
import sys
import time
import pygame
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field

import sys
import os

# Import from the src package - path should already be set up by main.py
from src.simulation import Simulation
from src.city import City
from src.map import Map
from src.path import Path, Node, Way
from src.unit import Unit
from src.agent import Agent
from src.script_parser import Script
from src.vector import Vector3f

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

# City listener to track entity changes - defined at module level
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

class GlassBoxDemo:
    """
    Main demo application for visualizing OpenGlassBox simulations.

    This class handles rendering and user interaction for the simulation.
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
        self.paused = False  # Start unpaused so simulation runs immediately

        # Simulation components
        self.simulation = Simulation(12, 12)  # Match C++ demo: 12x12 grid
        self.script_parser = Script()
        self.city_names = []
        self.selected_city_index = 0

        # Camera/view settings
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.zoom = 2.0  # Smaller zoom to see both cities

        # Debug flags
        self.show_debug = False
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

    def setup_listeners(self):
        """Set up event listeners for simulation components."""

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

    def draw_ui(self, surface: pygame.Surface):
        """
        Draw UI elements like buttons, sliders, and debug info.

        Args:
            surface: The surface to draw on
        """
        # Draw framerate and simulation stats
        fps = int(self.clock.get_fps())
        text = self.font.render(f"FPS: {fps}", True, WHITE)
        surface.blit(text, (self.width - 100, 10))

        # Draw simulation status
        status = "PAUSED" if self.paused else "RUNNING"
        fps = int(self.clock.get_fps())
        text = self.font.render(f"Status: {status} FPS: {fps}", True, WHITE)
        surface.blit(text, (self.width - 200, 10))

        # Draw debug panel if enabled
        if self.show_debug:
            # Background panel
            panel_rect = pygame.Rect(10, self.height - 120, 200, 110)
            pygame.draw.rect(surface, (0, 0, 0, 180), panel_rect)
            pygame.draw.rect(surface, WHITE, panel_rect, 1)

            # Debug options
            y_offset = self.height - 110
            for i, (option, enabled) in enumerate([
                ("Show Maps", self.show_maps),
                ("Show Paths", self.show_paths),
                ("Show Units", self.show_units),
                ("Show Agents", self.show_agents)
            ]):
                color = GREEN if enabled else RED
                text = self.font.render(f"{option}: {'ON' if enabled else 'OFF'}", True, color)
                surface.blit(text, (20, y_offset + i * 20))

            # Camera info
            text = self.font.render(f"Camera: ({self.camera_offset_x}, {self.camera_offset_y}) Zoom: {self.zoom:.1f}", True, WHITE)
            surface.blit(text, (20, y_offset + 80))

    def handle_events(self):
        """Handle pygame events like keyboard and mouse input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_d:
                    self.show_debug = not self.show_debug
                elif event.key == pygame.K_m:
                    self.show_maps = not self.show_maps
                elif event.key == pygame.K_l:
                    self.show_paths = not self.show_paths
                elif event.key == pygame.K_u:
                    self.show_units = not self.show_units
                elif event.key == pygame.K_a:
                    self.show_agents = not self.show_agents
                elif event.key == pygame.K_r:
                    # Reset view
                    self.camera_offset_x = 0
                    self.camera_offset_y = 0
                    self.zoom = 2.0

            elif event.type == pygame.MOUSEBUTTONDOWN:
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
                if self.dragging:
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
            self.simulation.update(dt)

    def render(self):
        """Render the current simulation state."""
        # Clear screen with dark blue background like C++ demo
        self.screen.fill((50, 50, 100))

        # If paused, show instructions like C++ demo
        if self.paused:
            # Draw instructions
            big_font = pygame.font.SysFont("Arial", 24)
            text1 = big_font.render("- PRESS P TO PLAY!", True, WHITE)
            text2 = big_font.render("- PRESS D TO SHOW DEBUG DURING THE PLAY!", True, WHITE)

            # Center the text
            self.screen.blit(text1, (50, 150))
            self.screen.blit(text2, (50, 200))
        else:
            # Draw grid for reference
            grid_size = 50
            for x in range(0, self.width, grid_size):
                pygame.draw.line(self.screen, (70, 70, 120), (x, 0), (x, self.height), 1)
            for y in range(0, self.height, grid_size):
                pygame.draw.line(self.screen, (70, 70, 120), (0, y), (self.width, y), 1)

            # Draw all cities
            for city_name, city in self.simulation.cities().items():
                self.draw_city(city, self.screen)

        # Draw UI on top
        self.draw_ui(self.screen)

        # Flip display
        pygame.display.flip()

    def init_demo_cities(self):
        """Initialize demo cities directly (like C++ demo) without script parsing."""
        print("Creating demo cities directly...")

        # Import types we need
        from src.map import MapType
        from src.path import PathType, WayType
        from src.unit import UnitType
        from src.agent import AgentType
        from src.resources import Resources

        # Create basic types (matching C++ demo)
        grass_type = MapType("Grass", 0x00FF00, 100)
        water_type = MapType("Water", 0x0000FF, 100)
        road_type = PathType("Road", 0x888888)
        dirt_type = WayType("Dirt", 0x8B4513)
        home_type = UnitType("Home", color=0xFF0000, radius=1, targets=["People", "Worker"])
        work_type = UnitType("Work", color=0x0000FF, radius=1, targets=["People", "Worker"])

        # Create agent types for testing
        people_agent_type = AgentType("People", 50.0, 1.0, 0xFFFF00)  # Yellow people
        worker_agent_type = AgentType("Worker", 30.0, 1.0, 0x00FFFF)  # Cyan workers

        # Create Paris city (matches C++ demo exactly)
        print("Creating Paris...")
        paris = self.simulation.add_city("Paris", Vector3f(400.0, 200.0, 0.0))

        # Add maps to Paris
        print("Adding maps to Paris...")
        paris_grass = paris.add_map(grass_type)
        paris_water = paris.add_map(water_type)

        # Add some resources to maps
        for u in range(0, 12, 2):
            for v in range(0, 12, 2):
                paris_grass.set_resource(u, v, 8)

        for u in range(1, 12, 3):
            for v in range(1, 12, 3):
                paris_water.set_resource(u, v, 50)

        # Add road and nodes to Paris
        print("Adding paths to Paris...")
        road = paris.add_path(road_type)
        n1 = road.add_node(Vector3f(60.0, 60.0, 0.0) + paris.position())
        n2 = road.add_node(Vector3f(300.0, 300.0, 0.0) + paris.position())
        n3 = road.add_node(Vector3f(60.0, 300.0, 0.0) + paris.position())

        # Add ways between nodes
        w1 = road.add_way(dirt_type, n1, n2)
        w2 = road.add_way(dirt_type, n2, n3)
        w3 = road.add_way(dirt_type, n3, n1)

        # Add units to Paris
        print("Adding units to Paris...")
        u1 = paris.add_unit_on_way(home_type, road, w1, 0.66)
        u2 = paris.add_unit_on_way(home_type, road, w1, 0.5)
        u3 = paris.add_unit_on_way(work_type, road, w2, 0.5)
        u4 = paris.add_unit_on_way(work_type, road, w3, 0.5)

        # Add some test agents to see animation
        print("Adding test agents to Paris...")
        test_resources = Resources()
        test_resources.add_resource("food", 5)

        test_agent = paris.add_agent(people_agent_type, u1, test_resources, "Work")
        test_agent2 = paris.add_agent(worker_agent_type, u3, test_resources, "Home")

        # Create Versailles city (matches C++ demo exactly)
        print("Creating Versailles...")
        versailles = self.simulation.add_city("Versailles", Vector3f(0.0, 30.0, 0.0))

        # Add maps to Versailles
        print("Adding maps to Versailles...")
        vers_grass = versailles.add_map(grass_type)
        vers_water = versailles.add_map(water_type)

        # Add some resources to maps
        for u in range(0, 12, 3):
            for v in range(0, 12, 3):
                vers_grass.set_resource(u, v, 6)

        for u in range(2, 12, 4):
            for v in range(2, 12, 4):
                vers_water.set_resource(u, v, 40)

        # Add road and nodes to Versailles
        print("Adding paths to Versailles...")
        road2 = versailles.add_path(road_type)
        n4 = road2.add_node(Vector3f(40.0, 20.0, 0.0) + versailles.position())
        n5 = road2.add_node(Vector3f(300.0, 300.0, 0.0) + versailles.position())

        # Add ways
        w4 = road2.add_way(dirt_type, n4, n5)
        w5 = road2.add_way(dirt_type, n5, n1)  # Connect to Paris

        # Add units to Versailles
        print("Adding units to Versailles...")
        u5 = versailles.add_unit_on_way(home_type, road, w5, 0.1)
        u6 = versailles.add_unit_on_way(work_type, road2, w4, 0.9)

        print("Demo cities initialized successfully!")
        return True

    def run(self):
        """Run the main demo loop."""
        # Initialize the demo cities directly
        self.init_demo_cities()

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
    """Main entry point for the demo application."""
    # Initialize demo
    demo = GlassBoxDemo(1024, 768, "OpenGlassBox Simulation")

    # Run the demo
    demo.run()

if __name__ == "__main__":
    main()
