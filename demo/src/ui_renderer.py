"""
UI Renderer module for OpenGlassBox demo.

This module handles all drawing and rendering functionality.
"""

import pygame
from typing import Dict, List, Optional, Tuple, Any, Set

from src.city import City
from src.map import Map
from src.path import Path, Node, Way
from src.unit import Unit
from src.agent import Agent
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
YELLOW = (255, 255, 0)

def hex_to_rgb(hex_color: int) -> Tuple[int, int, int]:
    """Convert a hex color (0xRRGGBB) to an RGB tuple."""
    r = (hex_color >> 16) & 0xFF
    g = (hex_color >> 8) & 0xFF
    b = hex_color & 0xFF
    return (r, g, b)

class UIRenderer:
    """Handles all UI rendering for the demo."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Arial", 16)
        self.big_font = pygame.font.SysFont("Arial", 20, bold=True)
    
    def world_to_screen(self, world_x: float, world_y: float, zoom: float, 
                       camera_offset_x: float, camera_offset_y: float) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        screen_x = int((world_x * zoom) + self.width / 2 + camera_offset_x)
        screen_y = int((world_y * zoom) + self.height / 2 + camera_offset_y)
        return (screen_x, screen_y)

    def draw_maps(self, city: City, surface: pygame.Surface, zoom: float, 
                  camera_offset_x: float, camera_offset_y: float, show_maps: bool):
        """Draw all maps in the city."""
        if not show_maps:
            return

        for map_name, map_obj in city.maps().items():
            pos = map_obj.position()
            grid_size_u = map_obj.grid_size_u()
            grid_size_v = map_obj.grid_size_v()
            cell_size = max(1, int(zoom * 5))

            for u in range(grid_size_u):
                for v in range(grid_size_v):
                    resource_amount = map_obj.get_resource(u, v)
                    if resource_amount > 0:
                        cell_world_x = pos.x + u * 10
                        cell_world_y = pos.y + v * 10
                        screen_x, screen_y = self.world_to_screen(
                            cell_world_x, cell_world_y, zoom, camera_offset_x, camera_offset_y)

                        color = hex_to_rgb(map_obj.color())
                        intensity = min(255, int(resource_amount / map_obj.get_capacity() * 255))
                        cell_color = (
                            min(255, color[0] + intensity // 3),
                            min(255, color[1] + intensity // 3),
                            min(255, color[2] + intensity // 3)
                        )

                        pygame.draw.rect(surface, cell_color,
                                       (screen_x, screen_y, cell_size, cell_size))

    def draw_paths(self, city: City, surface: pygame.Surface, zoom: float,
                   camera_offset_x: float, camera_offset_y: float, show_paths: bool):
        """Draw all paths, nodes, and ways in the city."""
        if not show_paths:
            return

        for path_name, path in city.paths().items():
            # Draw ways first
            for way in path.ways():
                from_pos = way.position1()
                to_pos = way.position2()
                from_x, from_y = self.world_to_screen(
                    from_pos.x, from_pos.y, zoom, camera_offset_x, camera_offset_y)
                to_x, to_y = self.world_to_screen(
                    to_pos.x, to_pos.y, zoom, camera_offset_x, camera_offset_y)

                color = hex_to_rgb(way.color())
                pygame.draw.line(surface, color, (from_x, from_y), (to_x, to_y), 2)

            # Draw nodes on top
            for i, node in enumerate(path.nodes()):
                pos = node.position()
                x, y = self.world_to_screen(
                    pos.x, pos.y, zoom, camera_offset_x, camera_offset_y)

                pygame.draw.circle(surface, WHITE, (x, y), 3)
                pygame.draw.circle(surface, BLACK, (x, y), 2)

                text = self.font.render(str(i), True, WHITE)
                surface.blit(text, (x + 8, y - 8))

    def draw_units(self, city: City, surface: pygame.Surface, zoom: float,
                   camera_offset_x: float, camera_offset_y: float, show_units: bool):
        """Draw all units in the city."""
        if not show_units:
            return

        for unit in city.units():
            pos = unit.position()
            x, y = self.world_to_screen(
                pos.x, pos.y, zoom, camera_offset_x, camera_offset_y)

            unit_type_name = unit.type() if callable(unit.type) else getattr(unit, "type", "Unknown")
            color = hex_to_rgb(unit.color())
            base_size = max(8, int(zoom * 3))

            if unit_type_name == "Home":
                # Draw triangle for houses
                triangle_size = base_size
                points = [
                    (x, y - triangle_size // 2),
                    (x - triangle_size // 2, y + triangle_size // 2),
                    (x + triangle_size // 2, y + triangle_size // 2)
                ]
                pygame.draw.polygon(surface, color, points)
            elif unit_type_name == "Work":
                # Draw large rectangle for factories
                size = base_size * 4
                pygame.draw.rect(surface, color, (x - size//2, y - size//2, size, size))
            else:
                # Default rectangle
                size = base_size
                pygame.draw.rect(surface, color, (x - size//2, y - size//2, size, size))

    def draw_agents(self, city: City, surface: pygame.Surface, zoom: float,
                    camera_offset_x: float, camera_offset_y: float, show_agents: bool):
        """Draw all agents in the city."""
        if not show_agents:
            return

        for agent in city.agents():
            pos = agent.position()
            x, y = self.world_to_screen(
                pos.x, pos.y, zoom, camera_offset_x, camera_offset_y)

            # Determine color based on agent type
            if hasattr(agent, "type") and agent.type() == "People":
                if hasattr(agent, "goal") and agent.goal == "Work":
                    color = (255, 255, 0)  # Yellow
                elif hasattr(agent, "goal") and agent.goal == "Home":
                    color = (255, 255, 255)  # White
                else:
                    color = (255, 255, 0)  # Default yellow
            else:
                color = hex_to_rgb(agent.m_type.color)

            size = 6
            points = [
                (x, y - size),
                (x - size, y + size),
                (x + size, y + size)
            ]
            pygame.draw.polygon(surface, color, points)

    def draw_city(self, city: City, surface: pygame.Surface, zoom: float,
                  camera_offset_x: float, camera_offset_y: float, 
                  show_maps: bool, show_paths: bool, show_units: bool, show_agents: bool):
        """Draw a city and all its components."""
        self.draw_maps(city, surface, zoom, camera_offset_x, camera_offset_y, show_maps)
        self.draw_paths(city, surface, zoom, camera_offset_x, camera_offset_y, show_paths)
        self.draw_units(city, surface, zoom, camera_offset_x, camera_offset_y, show_units)
        self.draw_agents(city, surface, zoom, camera_offset_x, camera_offset_y, show_agents)

        # Draw city name
        pos = city.position()
        x, y = self.world_to_screen(
            pos.x, pos.y, zoom, camera_offset_x, camera_offset_y)
        text = self.font.render(city.name().upper(), True, WHITE)
        surface.blit(text, (x - 50, y - 50))

    def draw_tick_counter(self, surface: pygame.Surface, tick_count: int, show_tick_counter: bool):
        """Draw the tick counter in the top left."""
        if not show_tick_counter:
            return
            
        tick_text = self.big_font.render(f"Ticks: {tick_count}", True, YELLOW)
        text_rect = tick_text.get_rect()
        bg_rect = text_rect.copy()
        bg_rect.x = 10
        bg_rect.y = 10
        bg_rect.width += 10
        bg_rect.height += 6
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(surface, YELLOW, bg_rect, 1)
        surface.blit(tick_text, (15, 13))

    def draw_debug_panel(self, surface: pygame.Surface, debug_options: Dict[str, bool], 
                        camera_offset_x: float, camera_offset_y: float, zoom: float):
        """Draw the debug panel."""
        panel_rect = pygame.Rect(10, self.height - 140, 200, 130)
        pygame.draw.rect(surface, (0, 0, 0, 180), panel_rect)
        pygame.draw.rect(surface, WHITE, panel_rect, 1)

        y_offset = self.height - 130
        for i, (option, enabled) in enumerate(debug_options.items()):
            color = GREEN if enabled else RED
            text = self.font.render(f"{option}: {'ON' if enabled else 'OFF'}", True, color)
            surface.blit(text, (20, y_offset + i * 20))

        # Camera info
        text = self.font.render(f"Camera: ({camera_offset_x}, {camera_offset_y}) Zoom: {zoom:.1f}", True, WHITE)
        surface.blit(text, (20, y_offset + 100))

    def draw_status(self, surface: pygame.Surface, paused: bool, fps: int):
        """Draw status information."""
        status = "PAUSED" if paused else "RUNNING"
        status_text = self.font.render(f"Status: {status} | FPS: {fps}", True, WHITE)
        surface.blit(status_text, (self.width - 200, 10))

    def draw_grid(self, surface: pygame.Surface):
        """Draw reference grid."""
        grid_size = 50
        for x in range(0, self.width, grid_size):
            pygame.draw.line(surface, (70, 70, 120), (x, 0), (x, self.height), 1)
        for y in range(0, self.height, grid_size):
            pygame.draw.line(surface, (70, 70, 120), (0, y), (self.width, y), 1)

    def draw_instructions(self, surface: pygame.Surface):
        """Draw pause screen instructions."""
        big_font = pygame.font.SysFont("Arial", 24)
        text1 = big_font.render("- PRESS P TO PLAY!", True, WHITE)
        text2 = big_font.render("- PRESS D TO SHOW DEBUG DURING THE PLAY!", True, WHITE)
        text3 = big_font.render("- PRESS T TO TOGGLE TICK COUNTER!", True, WHITE)

        surface.blit(text1, (50, 150))
        surface.blit(text2, (50, 200))
        surface.blit(text3, (50, 250))
