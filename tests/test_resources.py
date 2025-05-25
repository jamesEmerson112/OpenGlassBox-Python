"""
Test suite for the Resources container class.

This file covers:
- Construction and initialization of Resources containers.
- Adding, retrieving, and manipulating Resource objects within containers.
- Testing resource queries, searches, and collection operations.
- Verification of resource transfer and transformation methods.

The tests ensure that Resources containers behave correctly for resource management,
providing efficient storage and manipulation of Resource collections.
"""

import pytest

from src.resource import Resource
from src.resources import Resources

def test_constructor():
    """Test Resources container construction and basic operations."""
    resources = Resources()

    # Test initial state
    assert len(resources) == 0
    assert resources.empty()

    # Test adding resources
    water = Resource("Water", 100.0)
    food = Resource("Food", 50.0)

    resources.add(water)
    resources.add(food)

    assert len(resources) == 2
    assert not resources.empty()


def test_resource_access():
    """Test resource access and retrieval methods."""
    resources = Resources()

    # Add some test resources
    water = Resource("Water", 75.0)
    gold = Resource("Gold", 25.0)

    resources.add(water)
    resources.add(gold)

    # Test get method
    retrieved_water = resources.get("Water")
    assert retrieved_water is not None
    assert retrieved_water.name() == "Water"
    assert retrieved_water.value() == 75.0

    # Test get with non-existent resource
    missing = resources.get("NonExistent")
    assert missing is None

    # Test contains method
    assert resources.contains("Water")
    assert resources.contains("Gold")
    assert not resources.contains("Silver")


def test_resource_modification():
    """Test resource modification and manipulation."""
    resources = Resources()

    # Add initial resource
    energy = Resource("Energy", 100.0)
    resources.add(energy)

    # Test modification
    resources.set("Energy", 150.0)
    modified = resources.get("Energy")
    assert modified.value() == 150.0

    # Test addition to existing resource
    resources.add_value("Energy", 50.0)
    updated = resources.get("Energy")
    assert updated.value() == 200.0

    # Test subtraction
    resources.subtract_value("Energy", 25.0)
    decreased = resources.get("Energy")
    assert decreased.value() == 175.0


def test_resource_removal():
    """Test resource removal operations."""
    resources = Resources()

    # Add test resources
    resources.add(Resource("Iron", 100.0))
    resources.add(Resource("Coal", 200.0))
    resources.add(Resource("Stone", 300.0))

    assert len(resources) == 3

    # Test remove method
    removed = resources.remove("Coal")
    assert removed is not None
    assert removed.name() == "Coal"
    assert removed.value() == 200.0
    assert len(resources) == 2
    assert not resources.contains("Coal")

    # Test remove non-existent
    missing = resources.remove("NonExistent")
    assert missing is None
    assert len(resources) == 2


def test_resource_iteration():
    """Test iteration over resources."""
    resources = Resources()

    # Add test data
    test_data = [
        ("Wood", 50.0),
        ("Stone", 75.0),
        ("Metal", 100.0)
    ]

    for name, value in test_data:
        resources.add(Resource(name, value))

    # Test iteration
    found_resources = []
    for resource in resources:
        found_resources.append((resource.name(), resource.value()))

    # Sort both lists for comparison
    found_resources.sort(key=lambda x: x[0])
    test_data.sort(key=lambda x: x[0])

    assert found_resources == test_data


def test_resource_transfer():
    """Test resource transfer between containers."""
    source = Resources()
    destination = Resources()

    # Set up source resources
    source.add(Resource("Wheat", 100.0))
    source.add(Resource("Corn", 50.0))

    # Set up destination with some existing resources
    destination.add(Resource("Wheat", 25.0))
    destination.add(Resource("Rice", 75.0))

    # Transfer wheat from source to destination
    transferred = source.transfer_to(destination, "Wheat", 40.0)
    assert transferred == 40.0

    # Check source reduction
    source_wheat = source.get("Wheat")
    assert source_wheat.value() == 60.0

    # Check destination increase
    dest_wheat = destination.get("Wheat")
    assert dest_wheat.value() == 65.0

    # Test transfer more than available
    transferred = source.transfer_to(destination, "Wheat", 100.0)
    assert transferred == 60.0  # Only what was available

    # Source should be empty of wheat now
    assert not source.contains("Wheat")


def test_resource_copying():
    """Test resource container copying and cloning."""
    original = Resources()
    original.add(Resource("Lumber", 200.0))
    original.add(Resource("Nails", 500.0))

    # Test copy constructor
    copy = Resources(original)
    assert len(copy) == len(original)
    assert copy.get("Lumber").value() == 200.0
    assert copy.get("Nails").value() == 500.0

    # Test that it's a deep copy
    copy.set("Lumber", 300.0)
    assert original.get("Lumber").value() == 200.0  # Original unchanged
    assert copy.get("Lumber").value() == 300.0


def test_resource_clear():
    """Test clearing all resources."""
    resources = Resources()

    # Add some resources
    resources.add(Resource("Oil", 100.0))
    resources.add(Resource("Gas", 200.0))
    resources.add(Resource("Coal", 300.0))

    assert len(resources) == 3
    assert not resources.empty()

    # Clear all resources
    resources.clear()

    assert len(resources) == 0
    assert resources.empty()
    assert not resources.contains("Oil")
    assert not resources.contains("Gas")
    assert not resources.contains("Coal")


def test_resource_bulk_operations():
    """Test bulk operations on resources."""
    resources = Resources()

    # Add multiple resources at once
    bulk_data = {
        "Copper": 150.0,
        "Tin": 75.0,
        "Bronze": 25.0
    }

    resources.add_bulk(bulk_data)

    assert len(resources) == 3
    for name, value in bulk_data.items():
        resource = resources.get(name)
        assert resource is not None
        assert resource.value() == value


def test_resource_capacity_limits():
    """Test resource capacity and overflow handling."""
    resources = Resources()

    # Test with capacity limits
    resources.set_capacity("Water", 100.0)

    # Add within capacity
    resources.add(Resource("Water", 50.0))
    assert resources.get("Water").value() == 50.0

    # Try to add beyond capacity
    overflow = resources.add_with_capacity("Water", 75.0)
    assert resources.get("Water").value() == 100.0  # Capped at capacity
    assert overflow == 25.0  # Amount that couldn't be added
