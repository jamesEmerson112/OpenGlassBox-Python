"""
Test suite for the Resource class.

This file covers:
- Construction and initialization of Resource objects.
- Verification of member variables, type properties, and correct default values.
- Methods for adding, removing, and transferring resource amounts.
- Capacity management and edge cases for resource handling.

The tests ensure that Resource objects behave as expected for all basic operations, matching the logic and constraints of the original C++ simulation engine.
"""

import pytest
from src.resource import Resource

def test_constants():
    assert Resource.MAX_CAPACITY >= 65535

def test_constructor():
    oil = Resource("oil")
    assert oil.m_type == "oil"
    assert oil.m_amount == 0
    assert oil.m_capacity == Resource.MAX_CAPACITY
    assert oil.getAmount() == 0
    assert oil.hasAmount() is False
    assert oil.getCapacity() == Resource.MAX_CAPACITY
    assert oil.type() == "oil"

def test_add_amount():
    oil = Resource("oil")
    assert oil.m_amount == 0
    assert oil.m_capacity == Resource.MAX_CAPACITY

    oil.add(32)
    assert oil.m_amount == 32
    assert oil.getAmount() == 32
    assert oil.hasAmount() is True

    oil.add(32)
    assert oil.m_amount == 64
    assert oil.getAmount() == 64
    assert oil.hasAmount() is True

    oil.setCapacity(32)
    assert oil.m_capacity == 32
    assert oil.getCapacity() == 32
    assert oil.m_amount == 32
    assert oil.getAmount() == 32
    assert oil.hasAmount() is True

    oil.add(32)
    assert oil.m_capacity == 32
    assert oil.getCapacity() == 32
    assert oil.m_amount == 32
    assert oil.getAmount() == 32
    assert oil.hasAmount() is True

    oil.setCapacity(0)
    assert oil.m_capacity == 0
    assert oil.getCapacity() == 0
    assert oil.m_amount == 0
    assert oil.getAmount() == 0
    assert oil.hasAmount() is False

def test_add_amount_pathological_case():
    oil = Resource("oil")
    oil.add(32)
    assert oil.getAmount() == 32
    assert oil.hasAmount() is True

    oil.add(Resource.MAX_CAPACITY)
    assert oil.getAmount() == Resource.MAX_CAPACITY
    assert oil.hasAmount() is True

    oil.m_amount = 32
    oil.setCapacity(32)
    oil.add(Resource.MAX_CAPACITY)
    assert oil.getAmount() == 32
    assert oil.hasAmount() is True

def test_remove_amount():
    oil = Resource("oil")
    oil.add(32)
    assert oil.getAmount() == 32
    assert oil.hasAmount() is True

    oil.remove(16)
    assert oil.getAmount() == 16
    assert oil.hasAmount() is True

    oil.remove(18)
    assert oil.getAmount() == 0
    assert oil.hasAmount() is False

def test_transfert():
    oil = Resource("oil")
    gaz = Resource("gaz")

    assert oil.getAmount() == 0
    assert oil.getCapacity() == Resource.MAX_CAPACITY
    assert gaz.getAmount() == 0
    assert gaz.getCapacity() == Resource.MAX_CAPACITY

    oil.add(32)
    assert oil.getAmount() == 32
    assert oil.getCapacity() == Resource.MAX_CAPACITY

    oil.transferTo(gaz)
    assert oil.getAmount() == 0
    assert oil.getCapacity() == Resource.MAX_CAPACITY
    assert gaz.getAmount() == 32
    assert gaz.getCapacity() == Resource.MAX_CAPACITY

    oil.transferTo(gaz)
    assert oil.getAmount() == 0
    assert oil.getCapacity() == Resource.MAX_CAPACITY
    assert gaz.getAmount() == 32
    assert gaz.getCapacity() == Resource.MAX_CAPACITY

    oil.add(32)
    gaz.setCapacity(16)
    assert oil.getAmount() == 32
    assert oil.getCapacity() == Resource.MAX_CAPACITY
    assert gaz.getAmount() == 16
    assert gaz.getCapacity() == 16

    gaz.remove(1)
    assert gaz.getAmount() == 15
    assert gaz.getCapacity() == 16
    oil.transferTo(gaz)
    assert oil.getAmount() == 31
    assert gaz.getAmount() == 16
    assert gaz.getCapacity() == 16
