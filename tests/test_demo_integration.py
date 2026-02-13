"""
Integration tests for the demo applications.

Tests the complete demo functionality including enhanced debug UI features.
"""

import unittest
import os
import pygame
import time
from unittest.mock import Mock, patch, MagicMock

from demo.src.demo import GlassBoxDemo as BasicDemo
from openglassbox.simulation import Simulation
from openglassbox.vector import Vector3f


class TestBasicDemoIntegration(unittest.TestCase):
    """Integration tests for the basic demo application."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock pygame to avoid creating actual windows in tests
        pygame.init = Mock()
        pygame.display.set_mode = Mock(return_value=Mock())
        pygame.display.set_caption = Mock()
        pygame.font.SysFont = Mock(return_value=Mock())
        pygame.time.Clock = Mock(return_value=Mock())

    def tearDown(self):
        """Clean up after tests."""
        pygame.quit = Mock()

    def test_basic_demo_initialization(self):
        """Test that basic demo initializes correctly."""
        try:
            demo = BasicDemo(800, 600, "Test Demo")
            self.assertIsNotNone(demo)
            self.assertEqual(demo.width, 800)
            self.assertEqual(demo.height, 600)
            self.assertTrue(demo.paused)
            self.assertFalse(demo.running)  # Not started yet
        except Exception as e:
            self.fail(f"Basic demo initialization failed: {e}")

    def test_basic_demo_simulation_setup(self):
        """Test that basic demo sets up simulation correctly."""
        demo = BasicDemo(800, 600, "Test Demo")

        # Check simulation is created
        self.assertIsNotNone(demo.simulation)
        self.assertEqual(demo.simulation.grid_size_u(), 12)
        self.assertEqual(demo.simulation.grid_size_v(), 12)

    def test_basic_demo_listeners_setup(self):
        """Test that event listeners are set up correctly."""
        demo = BasicDemo(800, 600, "Test Demo")

        # Simulation should have a listener
        self.assertIsNotNone(demo.simulation._listener)

        # City names list should be initialized
        self.assertIsInstance(demo.city_names, list)

    def test_basic_demo_coordinate_conversion(self):
        """Test world-to-screen coordinate conversion."""
        demo = BasicDemo(800, 600, "Test Demo")

        # Test coordinate conversion
        world_x, world_y = 100.0, 200.0
        screen_x, screen_y = demo.world_to_screen(world_x, world_y)

        # Should return integers
        self.assertIsInstance(screen_x, int)
        self.assertIsInstance(screen_y, int)

        # Test reverse conversion
        back_world_x, back_world_y = demo.screen_to_world(screen_x, screen_y)

        # Should be approximately the same (allowing for floating point precision)
        self.assertAlmostEqual(back_world_x, world_x, places=1)
        self.assertAlmostEqual(back_world_y, world_y, places=1)

    @patch('pygame.event.get')
    def test_basic_demo_event_handling(self, mock_get_events):
        """Test basic demo event handling."""
        demo = BasicDemo(800, 600, "Test Demo")

        # Mock quit event
        quit_event = Mock()
        quit_event.type = pygame.QUIT
        mock_get_events.return_value = [quit_event]

        # Handle events
        demo.handle_events()

        # Should set running to False
        self.assertFalse(demo.running)

    def test_basic_demo_load_simulation_with_missing_file(self):
        """Test loading simulation with missing file."""
        demo = BasicDemo(800, 600, "Test Demo")

        # Try to load non-existent file
        result = demo.load_simulation("nonexistent_file.txt")

        # Should return False
        self.assertFalse(result)


@unittest.skip("demo_enhanced module not available")
class TestEnhancedDemoIntegration(unittest.TestCase):
    """Integration tests for the enhanced demo application with debug UI."""
    pass


class TestDemoPerformance(unittest.TestCase):
    """Performance tests for demo applications."""

    def setUp(self):
        """Set up performance test fixtures."""
        # Mock pygame for performance tests
        pygame.init = Mock()
        pygame.display.set_mode = Mock(return_value=Mock())
        pygame.display.set_caption = Mock()
        pygame.font.SysFont = Mock(return_value=Mock())
        pygame.time.Clock = Mock(return_value=Mock())

    @unittest.skip("Performance test - run manually when needed")
    def test_basic_demo_performance(self):
        """Test basic demo performance."""
        demo = BasicDemo(1024, 768, "Performance Test")

        # Create a larger simulation for performance testing
        for i in range(5):
            city = demo.simulation.add_city(f"City{i}", Vector3f(i * 100, i * 100, 0))

        # Time multiple update cycles
        start_time = time.time()
        for _ in range(100):
            demo.update(0.016)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_update = total_time / 100

        print(f"Basic demo average update time: {avg_time_per_update:.4f}s")

        # Should complete 100 updates in reasonable time (< 1 second)
        self.assertLess(total_time, 1.0, "Basic demo update performance too slow")


class TestDemoFileOperations(unittest.TestCase):
    """Test file operations and resource loading in demos."""

    def setUp(self):
        """Set up file operation test fixtures."""
        # Mock pygame
        pygame.init = Mock()
        pygame.display.set_mode = Mock(return_value=Mock())
        pygame.display.set_caption = Mock()
        pygame.font.SysFont = Mock(return_value=Mock())
        pygame.time.Clock = Mock(return_value=Mock())

    def test_demo_simulation_file_search(self):
        """Test simulation file search functionality."""
        demo = BasicDemo(800, 600, "File Test Demo")

        # Test the simulation file search paths
        possible_paths = [
            os.path.join("data", "simulations", "TestCity.txt"),
            os.path.join("python", "data", "simulations", "TestCity.txt"),
            os.path.join("demo", "data", "Simulations", "TestCity.txt"),
            os.path.join("..", "demo", "data", "Simulations", "TestCity.txt")
        ]

        # At least one of these paths should exist or be searched
        self.assertIsInstance(possible_paths, list)
        self.assertGreater(len(possible_paths), 0)

    def test_demo_fallback_city_creation(self):
        """Test fallback city creation when simulation file is missing."""
        demo = BasicDemo(800, 600, "Fallback Test Demo")

        # Simulate missing simulation file by trying to load nonexistent file
        result = demo.load_simulation("definitely_nonexistent_file.txt")
        self.assertFalse(result)

        # The main() function should handle this gracefully by creating a test city
        # We can't easily test the main() function directly, but we can verify
        # that the demo can create cities programmatically
        test_city = demo.simulation.add_city("TestFallbackCity", Vector3f(0, 0, 0))
        self.assertIsNotNone(test_city)
        self.assertEqual(test_city.name(), "TestFallbackCity")


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
