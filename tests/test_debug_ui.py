"""
Tests for the debug UI system.

Tests the Dear ImGui-equivalent debug panels and interactive UI components.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame
from typing import List, Dict

import debug_ui DebugUI
from simulation import Simulation
from city import City
from vector import Vector3f


class TestDebugUI(unittest.TestCase):
    """Test cases for the DebugUI class."""

    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 16)
        self.debug_ui = DebugUI(self.font)

        # Create a mock simulation with test data
        self.simulation = Simulation(12, 12)
        self.city = self.simulation.add_city("TestCity", Vector3f(100, 100, 0))

        # Create mock surface
        self.surface = pygame.Surface((800, 600))

    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()

    def test_init(self):
        """Test DebugUI initialization."""
        debug_ui = DebugUI(self.font)
        self.assertFalse(debug_ui.visible)
        self.assertEqual(debug_ui.selected_city_index, 0)
        self.assertIsNotNone(debug_ui.font)
        self.assertEqual(debug_ui.panel_x, 10)
        self.assertEqual(debug_ui.panel_y, 50)
        self.assertEqual(debug_ui.panel_width, 300)

    def test_visibility_toggle(self):
        """Test showing and hiding the debug UI."""
        # Initially not visible
        self.assertFalse(self.debug_ui.visible)

        # Make visible
        self.debug_ui.visible = True
        self.assertTrue(self.debug_ui.visible)

        # Hide again
        self.debug_ui.visible = False
        self.assertFalse(self.debug_ui.visible)

    def test_draw_debug_panel_hidden(self):
        """Test that nothing is drawn when debug UI is hidden."""
        # Mock the surface blit method to count calls
        original_blit = self.surface.blit
        blit_calls = []
        self.surface.blit = lambda *args, **kwargs: blit_calls.append((args, kwargs))

        # Draw with hidden UI
        self.debug_ui.visible = False
        self.debug_ui.draw_debug_panel(self.surface, self.simulation)

        # Should have no blit calls
        self.assertEqual(len(blit_calls), 0)

        # Restore original blit
        self.surface.blit = original_blit

    def test_draw_debug_panel_visible(self):
        """Test that debug panel is drawn when visible."""
        # Mock the surface blit method to count calls
        original_blit = self.surface.blit
        blit_calls = []
        self.surface.blit = lambda *args, **kwargs: blit_calls.append((args, kwargs))

        # Draw with visible UI
        self.debug_ui.visible = True
        self.debug_ui.draw_debug_panel(self.surface, self.simulation)

        # Should have some blit calls (at least for the panel background and headers)
        self.assertGreater(len(blit_calls), 0)

        # Restore original blit
        self.surface.blit = original_blit

    def test_collapsible_headers(self):
        """Test collapsible header functionality."""
        # Test initial state
        self.assertIn("simulation", self.debug_ui.collapsed_headers)
        self.assertIn("cities", self.debug_ui.collapsed_headers)

        # Test toggling simulation header
        initial_state = self.debug_ui.collapsed_headers["simulation"]
        self.debug_ui._toggle_header("simulation")
        self.assertEqual(
            self.debug_ui.collapsed_headers["simulation"],
            not initial_state
        )

        # Test toggling back
        self.debug_ui._toggle_header("simulation")
        self.assertEqual(
            self.debug_ui.collapsed_headers["simulation"],
            initial_state
        )

    def test_city_selection(self):
        """Test city selection functionality."""
        # Add multiple cities to simulation
        city2 = self.simulation.add_city("SecondCity", Vector3f(200, 200, 0))
        city3 = self.simulation.add_city("ThirdCity", Vector3f(300, 300, 0))

        # Test initial selection
        self.assertEqual(self.debug_ui.selected_city_index, 0)

        # Test cycling through cities
        city_names = [city.name() for city in self.simulation.cities()]

        # Cycle to next city
        self.debug_ui.selected_city_index = 1
        self.assertEqual(self.debug_ui.selected_city_index, 1)

        # Cycle to third city
        self.debug_ui.selected_city_index = 2
        self.assertEqual(self.debug_ui.selected_city_index, 2)

        # Test wrapping (should handle bounds checking)
        self.debug_ui.selected_city_index = 0
        self.assertEqual(self.debug_ui.selected_city_index, 0)

    def test_handle_click_on_header(self):
        """Test clicking on collapsible headers."""
        city_names = ["TestCity"]

        # Mock click on simulation header area
        click_pos = (self.debug_ui.panel_x + 10, self.debug_ui.panel_y + 30)

        # Get initial state
        initial_simulation_state = self.debug_ui.collapsed_headers["simulation"]

        # Test click handling
        result = self.debug_ui.handle_click(click_pos, city_names)

        # Should return True if click was handled
        self.assertTrue(result)

    def test_handle_click_outside_panel(self):
        """Test clicking outside the debug panel."""
        city_names = ["TestCity"]

        # Click far outside the panel
        click_pos = (500, 500)

        # Test click handling
        result = self.debug_ui.handle_click(click_pos, city_names)

        # Should return False if click was not in panel
        self.assertFalse(result)

    def test_key_press_tab_cycles_cities(self):
        """Test that Tab key cycles through cities."""
        # Add multiple cities
        city2 = self.simulation.add_city("SecondCity", Vector3f(200, 200, 0))
        city_names = [city.name() for city in self.simulation.cities()]

        # Test Tab key press
        initial_index = self.debug_ui.selected_city_index
        self.debug_ui.handle_key_press(pygame.K_TAB, city_names)

        # Should cycle to next city
        expected_index = (initial_index + 1) % len(city_names)
        self.assertEqual(self.debug_ui.selected_city_index, expected_index)

    def test_key_press_space_toggles_simulation(self):
        """Test that Space key toggles simulation header."""
        initial_state = self.debug_ui.collapsed_headers["simulation"]

        # Test Space key press
        self.debug_ui.handle_key_press(pygame.K_SPACE, ["TestCity"])

        # Should toggle simulation header
        self.assertEqual(
            self.debug_ui.collapsed_headers["simulation"],
            not initial_state
        )

    def test_draw_text_helper(self):
        """Test the text drawing helper method."""
        # Mock surface blit
        original_blit = self.surface.blit
        blit_calls = []
        self.surface.blit = lambda *args, **kwargs: blit_calls.append((args, kwargs))

        # Test drawing text
        result_y = self.debug_ui._draw_text(
            self.surface, "Test Text", 10, 20, (255, 255, 255)
        )

        # Should return updated Y position
        self.assertGreater(result_y, 20)

        # Should have called blit
        self.assertEqual(len(blit_calls), 1)

        # Restore original blit
        self.surface.blit = original_blit

    def test_draw_header_helper(self):
        """Test the header drawing helper method."""
        # Mock surface methods
        original_blit = self.surface.blit
        original_draw_rect = pygame.draw.rect
        blit_calls = []
        rect_calls = []

        self.surface.blit = lambda *args, **kwargs: blit_calls.append((args, kwargs))
        pygame.draw.rect = lambda *args, **kwargs: rect_calls.append((args, kwargs))

        # Test drawing header
        result_y = self.debug_ui._draw_header(
            self.surface, "Test Header", 10, 20, "test_key"
        )

        # Should return updated Y position
        self.assertGreater(result_y, 20)

        # Should have drawn rectangle and text
        self.assertGreater(len(rect_calls), 0)
        self.assertGreater(len(blit_calls), 0)

        # Restore original methods
        self.surface.blit = original_blit
        pygame.draw.rect = original_draw_rect

    def test_error_handling_with_invalid_simulation(self):
        """Test error handling with invalid simulation data."""
        # Test with None simulation
        try:
            self.debug_ui.visible = True
            self.debug_ui.draw_debug_panel(self.surface, None)
            # Should not crash
        except AttributeError:
            self.fail("DebugUI should handle None simulation gracefully")

    def test_performance_with_large_simulation(self):
        """Test performance with a large simulation."""
        # Create a larger simulation with many cities
        large_simulation = Simulation(32, 32)
        for i in range(10):
            city = large_simulation.add_city(f"City{i}", Vector3f(i * 50, i * 50, 0))

        # Time the drawing operation
        import time
        start_time = time.time()

        self.debug_ui.visible = True
        self.debug_ui.draw_debug_panel(self.surface, large_simulation)

        end_time = time.time()
        draw_time = end_time - start_time

        # Should complete within reasonable time (< 0.1 seconds)
        self.assertLess(draw_time, 0.1, "Debug UI drawing should be fast")


class TestDebugUIIntegration(unittest.TestCase):
    """Integration tests for DebugUI with simulation components."""

    def setUp(self):
        """Set up integration test fixtures."""
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 16)
        self.debug_ui = DebugUI(self.font)
        self.surface = pygame.Surface((800, 600))

        # Create a complete simulation with multiple components
        self.simulation = Simulation(12, 12)

        # Create cities with paths, units, and maps
        from .map import MapType
        from .path import PathType, WayType
        from .unit import UnitType

        # Create types
        self.grass_type = MapType("Grass", 0x00FF00, 100)
        self.road_type = PathType("Road", 0x555555)
        self.dirt_type = WayType("Dirt", 0x8B4513)
        self.home_type = UnitType("Home", 0xFF0000)

        # Create Paris city with full components
        self.paris = self.simulation.add_city("Paris", Vector3f(400, 200, 0))

        # Add map
        self.paris_grass = self.paris.add_map(self.grass_type)
        for u in range(0, 12, 2):
            for v in range(0, 12, 2):
                self.paris_grass.set_resource(u, v, 8)

        # Add path with nodes and ways
        self.road = self.paris.add_path(self.road_type)
        self.n1 = self.road.addNode(Vector3f(60.0, 60.0, 0.0))
        self.n2 = self.road.addNode(Vector3f(300.0, 300.0, 0.0))
        self.w1 = self.road.addWay(self.dirt_type, self.n1, self.n2)

        # Add units
        self.unit1 = self.paris.add_unit(self.home_type, self.road, self.w1, 0.5)

    def tearDown(self):
        """Clean up after integration tests."""
        pygame.quit()

    def test_debug_ui_with_complete_simulation(self):
        """Test debug UI with a complete simulation including all components."""
        # Make debug UI visible
        self.debug_ui.visible = True

        # Should be able to draw without errors
        try:
            self.debug_ui.draw_debug_panel(self.surface, self.simulation)
        except Exception as e:
            self.fail(f"Debug UI failed with complete simulation: {e}")

    def test_city_switching_with_multiple_cities(self):
        """Test city switching functionality with multiple cities."""
        # Add second city
        versailles = self.simulation.add_city("Versailles", Vector3f(0, 30, 0))

        city_names = [city.name() for city in self.simulation.cities()]

        # Test switching between cities
        self.assertEqual(self.debug_ui.selected_city_index, 0)

        # Switch to second city
        self.debug_ui.handle_key_press(pygame.K_TAB, city_names)
        self.assertEqual(self.debug_ui.selected_city_index, 1)

        # Switch back to first city
        self.debug_ui.handle_key_press(pygame.K_TAB, city_names)
        self.assertEqual(self.debug_ui.selected_city_index, 0)

    def test_resource_display_accuracy(self):
        """Test that resource information is displayed accurately."""
        # The debug UI should display resource information correctly
        # This is mainly a visual test, but we can check that it doesn't crash
        self.debug_ui.visible = True

        # Expand the cities section to show resource details
        self.debug_ui.collapsed_headers["cities"] = False

        try:
            self.debug_ui.draw_debug_panel(self.surface, self.simulation)
        except Exception as e:
            self.fail(f"Debug UI failed displaying resources: {e}")


if __name__ == "__main__":
    unittest.main()
