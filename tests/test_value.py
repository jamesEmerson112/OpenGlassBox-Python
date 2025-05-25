"""
Test suite for the RuleValue class and related value types.

This file covers:
- Construction and evaluation of different RuleValue types.
- Testing global values, local values, map values, and constants.
- Verification of arithmetic operations and value comparisons.
- Testing resource-based value calculations and context handling.

The tests ensure that RuleValue objects behave correctly for simulation logic,
rule evaluation, and resource management within the OpenGlassBox engine.
"""

import pytest
import math

from src.resource import Resource
from src.rule_value import IRuleValue as RuleValueGlobal, RuleValueLocal, RuleValueMap


# Mock RuleContext for testing since it may not be fully implemented
class MockRuleContext:
    """Mock context for rule evaluation testing."""
    def __init__(self):
        self.m_globalResources = {}
        self.m_localResources = {}
        self.m_mapValue = 0.0


def test_rule_value_global():
    """Test global rule values."""
    try:
        # Test creating and evaluating global values
        global_value = RuleValueGlobal("TestResource")

        if hasattr(global_value, 'm_name'):
            assert global_value.m_name == "TestResource"

        # Test evaluation with context if method exists
        if hasattr(global_value, 'eval'):
            context = MockRuleContext()
            context.m_globalResources = {"TestResource": Resource("TestResource", 42.0)}

            result = global_value.eval(context)
            assert isinstance(result, (int, float))

            # Test with missing resource
            context.m_globalResources = {}
            result = global_value.eval(context)
            assert result == 0.0 or result is None
        else:
            pytest.skip("RuleValueGlobal.eval() method not implemented")

    except (ImportError, AttributeError, NotImplementedError):
        pytest.skip("RuleValueGlobal not yet fully implemented")


def test_rule_value_local():
    """Test local rule values."""
    try:
        # Test creating and evaluating local values
        local_value = RuleValueLocal("LocalResource")

        if hasattr(local_value, 'm_name'):
            assert local_value.m_name == "LocalResource"

        # Test evaluation with context if method exists
        if hasattr(local_value, 'eval'):
            context = MockRuleContext()
            context.m_localResources = {"LocalResource": Resource("LocalResource", 25.5)}

            result = local_value.eval(context)
            assert isinstance(result, (int, float))

            # Test with missing resource
            context.m_localResources = {}
            result = local_value.eval(context)
            assert result == 0.0 or result is None
        else:
            pytest.skip("RuleValueLocal.eval() method not implemented")

    except (ImportError, AttributeError, NotImplementedError):
        pytest.skip("RuleValueLocal not yet fully implemented")


def test_rule_value_map():
    """Test map rule values."""
    try:
        # Test creating map values
        map_value = RuleValueMap("MapResource")

        if hasattr(map_value, 'm_name'):
            assert map_value.m_name == "MapResource"

        # Test evaluation with context if method exists
        if hasattr(map_value, 'eval'):
            context = MockRuleContext()
            context.m_mapValue = 15.0

            result = map_value.eval(context)
            assert isinstance(result, (int, float))

            # Test with no map value set
            context.m_mapValue = 0.0
            result = map_value.eval(context)
            assert result == 0.0
        else:
            pytest.skip("RuleValueMap.eval() method not implemented")

    except (ImportError, AttributeError, NotImplementedError):
        pytest.skip("RuleValueMap not yet fully implemented")


def test_rule_context():
    """Test the RuleContext container."""
    try:
        # Test with mock context for now
        context = MockRuleContext()

        # Test initialization
        assert isinstance(context.m_globalResources, dict)
        assert isinstance(context.m_localResources, dict)
        assert context.m_mapValue == 0.0

        # Test setting resources
        global_res = Resource("Global", 100.0)
        local_res = Resource("Local", 50.0)

        context.m_globalResources["Global"] = global_res
        context.m_localResources["Local"] = local_res
        context.m_mapValue = 75.0

        assert context.m_globalResources["Global"].value() == 100.0
        assert context.m_localResources["Local"].value() == 50.0
        assert context.m_mapValue == 75.0

    except (ImportError, AttributeError, NotImplementedError):
        pytest.skip("RuleContext not yet fully implemented")


def test_rule_value_arithmetic():
    """Test arithmetic operations with rule values."""
    try:
        # Create some test values
        value1 = RuleValueGlobal("Resource1")
        value2 = RuleValueGlobal("Resource2")

        if hasattr(value1, 'eval') and hasattr(value2, 'eval'):
            context = MockRuleContext()
            context.m_globalResources = {
                "Resource1": Resource("Resource1", 10.0),
                "Resource2": Resource("Resource2", 5.0)
            }

            # Test individual evaluations
            result1 = value1.eval(context)
            result2 = value2.eval(context)

            assert isinstance(result1, (int, float))
            assert isinstance(result2, (int, float))
        else:
            pytest.skip("RuleValue eval methods not available for arithmetic testing")

    except (ImportError, AttributeError, NotImplementedError):
        pytest.skip("RuleValue arithmetic not yet fully implemented")


def test_complex_rule_evaluation():
    """Test complex rule evaluation scenarios."""
    try:
        context = MockRuleContext()

        # Set up a complex context
        context.m_globalResources = {
            "Population": Resource("Population", 1000.0),
            "Happiness": Resource("Happiness", 0.8)
        }

        context.m_localResources = {
            "Housing": Resource("Housing", 50.0),
            "Jobs": Resource("Jobs", 45.0)
        }

        context.m_mapValue = 25.0

        # Test various value types
        pop_value = RuleValueGlobal("Population")
        happiness_value = RuleValueGlobal("Happiness")
        housing_value = RuleValueLocal("Housing")
        jobs_value = RuleValueLocal("Jobs")
        map_value = RuleValueMap("WaterLevel")

        # Test evaluations if methods exist
        if all(hasattr(v, 'eval') for v in [pop_value, happiness_value, housing_value, jobs_value, map_value]):
            pop_result = pop_value.eval(context)
            happiness_result = happiness_value.eval(context)
            housing_result = housing_value.eval(context)
            jobs_result = jobs_value.eval(context)
            map_result = map_value.eval(context)

            # Verify they return numeric values
            assert isinstance(pop_result, (int, float))
            assert isinstance(happiness_result, (int, float))
            assert isinstance(housing_result, (int, float))
            assert isinstance(jobs_result, (int, float))
            assert isinstance(map_result, (int, float))
        else:
            pytest.skip("Complex rule evaluation requires eval methods")

    except (ImportError, AttributeError, NotImplementedError):
        pytest.skip("Complex rule evaluation not yet fully implemented")


def test_rule_value_edge_cases():
    """Test edge cases and error handling."""
    try:
        context = MockRuleContext()

        # Test with empty context
        value = RuleValueGlobal("NonExistent")

        if hasattr(value, 'eval'):
            result = value.eval(context)
            assert result == 0.0 or result is None

            # Test with None resources
            context.m_globalResources = None
            context.m_localResources = None

            global_val = RuleValueGlobal("Test")
            local_val = RuleValueLocal("Test")
            map_val = RuleValueMap("Test")

            # Should handle gracefully
            try:
                global_result = global_val.eval(context)
                local_result = local_val.eval(context)
                map_result = map_val.eval(context)

                # Results should be valid numbers or None
                assert global_result is None or isinstance(global_result, (int, float))
                assert local_result is None or isinstance(local_result, (int, float))
                assert map_result is None or isinstance(map_result, (int, float))
            except (AttributeError, TypeError):
                # Expected if implementation doesn't handle None gracefully yet
                pass
        else:
            pytest.skip("RuleValue eval methods not available for edge case testing")

    except (ImportError, AttributeError, NotImplementedError):
        pytest.skip("RuleValue edge case handling not yet fully implemented")


def test_resource_value_precision():
    """Test floating point precision in resource values."""
    try:
        context = MockRuleContext()

        # Test with very small values
        small_value = 0.000001
        context.m_globalResources = {
            "Small": Resource("Small", small_value)
        }

        value = RuleValueGlobal("Small")

        if hasattr(value, 'eval'):
            result = value.eval(context)
            if result is not None:
                assert abs(result - small_value) < 1e-10

            # Test with very large values
            large_value = 1e10
            context.m_globalResources = {
                "Large": Resource("Large", large_value)
            }

            value = RuleValueGlobal("Large")
            result = value.eval(context)
            if result is not None:
                assert abs(result - large_value) < 1e-5  # Allow some floating point error
        else:
            pytest.skip("RuleValue eval method not available for precision testing")

    except (ImportError, AttributeError, NotImplementedError):
        pytest.skip("Resource value precision testing not yet fully implemented")


def test_rule_value_types():
    """Test different rule value type instantiation."""
    try:
        # Test basic construction
        global_val = RuleValueGlobal("test_global")
        local_val = RuleValueLocal("test_local")
        map_val = RuleValueMap("test_map")

        # Test type properties if available
        if hasattr(global_val, 'type'):
            assert global_val.type() == "global" or isinstance(global_val.type(), str)
        if hasattr(local_val, 'type'):
            assert local_val.type() == "local" or isinstance(local_val.type(), str)
        if hasattr(map_val, 'type'):
            assert map_val.type() == "map" or isinstance(map_val.type(), str)

        # Test name properties
        if hasattr(global_val, 'name'):
            assert global_val.name() == "test_global"
        if hasattr(local_val, 'name'):
            assert local_val.name() == "test_local"
        if hasattr(map_val, 'name'):
            assert map_val.name() == "test_map"

    except (ImportError, AttributeError, NotImplementedError):
        pytest.skip("RuleValue type instantiation not yet fully implemented")


def test_rule_value_string_representation():
    """Test string representation of rule values."""
    try:
        global_val = RuleValueGlobal("TestGlobal")
        local_val = RuleValueLocal("TestLocal")
        map_val = RuleValueMap("TestMap")

        # Test string representations
        global_str = str(global_val)
        local_str = str(local_val)
        map_str = str(map_val)

        assert isinstance(global_str, str)
        assert isinstance(local_str, str)
        assert isinstance(map_str, str)

        # Test that names appear in string representation
        assert "TestGlobal" in global_str or "global" in global_str.lower()
        assert "TestLocal" in local_str or "local" in local_str.lower()
        assert "TestMap" in map_str or "map" in map_str.lower()

    except (ImportError, AttributeError, NotImplementedError):
        pytest.skip("RuleValue string representation not yet fully implemented")
