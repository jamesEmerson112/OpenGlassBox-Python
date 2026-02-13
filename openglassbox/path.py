"""
Path module implementation for the OpenGlassBox engine.

This module implements the graph structure for simulating transportation networks.
It provides the Node and Way classes for building the graph, and the Path class
as a container for managing the graph structure.
"""

from typing import List, Dict, Optional, Any, Union, TypeVar, Tuple
from dataclasses import dataclass, field
import math

from .vector import Vector3f


@dataclass
class WayType:
    """
    Defines properties of a Way (connection between nodes).
    """
    name: str
    color: int = 0xFFFFFF


@dataclass
class PathType:
    """
    Defines properties of a Path (a collection of nodes and ways).
    """
    name: str
    color: int = 0xFFFFFF


class Node:
    """
    Node class representing vertices in the path graph.

    Nodes define connection points in the transportation network.
    They store their position in the world, track connected Ways,
    and may have Units attached to them.
    """

    def __init__(self, node_id: int, position: Vector3f):
        """
        Initialize a node with ID and position.

        Args:
            node_id: Unique identifier for this node
            position: The node's position in world space
        """
        self.m_id = node_id
        self.m_position = position
        self.m_ways: List['Way'] = []
        self.m_units: List[Any] = []  # Will be populated with references to Unit instances

    def add_unit(self, unit: Any) -> None:
        """
        Attach a Unit to this node.

        Args:
            unit: The Unit to attach to this node
        """
        self.m_units.append(unit)

    def translate(self, direction: Vector3f) -> None:
        """
        Move the node by the specified direction vector.

        Args:
            direction: Vector representing the direction and magnitude of movement
        """
        self.m_position += direction
        # Update magnitude of all connected ways
        for way in self.m_ways:
            way.update_magnitude()

    def get_way_to_node(self, other_node: 'Node') -> Optional['Way']:
        """
        Find a way connecting this node to another specified node.

        Args:
            other_node: The node to find a connection to

        Returns:
            The Way object connecting the nodes, or None if no connection exists
        """
        for way in self.m_ways:
            if (way.m_from is other_node and way.m_to is self) or \
               (way.m_to is other_node and way.m_from is self):
                return way
        return None

    def has_ways(self) -> bool:
        """
        Check if this node has any ways connected to it.

        Returns:
            True if the node has at least one connected Way, False otherwise
        """
        return len(self.m_ways) > 0

    def get_map_position(self, grid_size_u: int, grid_size_v: int, u: int, v: int) -> Tuple[int, int]:
        """
        Convert world position to map coordinates.

        Args:
            grid_size_u: The grid size in the U direction
            grid_size_v: The grid size in the V direction
            u: Output parameter for U coordinate
            v: Output parameter for V coordinate

        Returns:
            Tuple of (u, v) map coordinates
        """
        # This version returns calculated values directly rather than using output parameters
        # In real implementation, this would map from world to grid coordinates
        return u, v

    def id(self) -> int:
        """
        Get the node's unique identifier.

        Returns:
            The node's ID
        """
        return self.m_id

    def position(self) -> Vector3f:
        """
        Get the node's position in world space.

        Returns:
            The node's position as a Vector3f
        """
        return self.m_position

    def ways(self) -> List['Way']:
        """
        Get the list of ways connected to this node.

        Returns:
            List of connected Way objects
        """
        return self.m_ways

    def units(self) -> List[Any]:
        """
        Get the list of units attached to this node.

        Returns:
            List of attached Unit objects
        """
        return self.m_units

    def unit(self, index: int) -> Any:
        """
        Get a specific unit by index.

        Args:
            index: The index of the unit to retrieve

        Returns:
            The Unit at the specified index
        """
        return self.m_units[index]

    @staticmethod
    def color() -> int:
        """
        Get the global color for nodes.

        Returns:
            The color value as an integer
        """
        return 0xAAAAAA


class Way:
    """
    Way class representing edges in the path graph.

    Ways connect nodes together, forming the transportation network.
    Ways have a type that defines their properties, and they track
    their length for pathfinding calculations.
    """

    def __init__(self, way_id: int, way_type: WayType, from_node: Node, to_node: Node):
        """
        Initialize a way connecting two nodes.

        Args:
            way_id: Unique identifier for this way
            way_type: The type of the way (defining its properties)
            from_node: The origin node
            to_node: The destination node
        """
        self.m_id = way_id
        self.m_type = way_type
        self.m_from = from_node
        self.m_to = to_node
        self.m_magnitude = 0.0

        # Add this way to both nodes' lists
        self.m_from.m_ways.append(self)
        self.m_to.m_ways.append(self)

        # Calculate initial length
        self.update_magnitude()

    def update_magnitude(self) -> None:
        """
        Update the cached length of the way.
        """
        self.m_magnitude = (self.m_to.position() - self.m_from.position()).magnitude()

    def id(self) -> int:
        """
        Get the way's unique identifier.

        Returns:
            The way's ID
        """
        return self.m_id

    def from_(self) -> Node:
        """
        Get the origin node.

        Returns:
            The origin Node
        """
        return self.m_from

    def to(self) -> Node:
        """
        Get the destination node.

        Returns:
            The destination Node
        """
        return self.m_to

    def position1(self) -> Vector3f:
        """
        Get the position of the origin node.

        Returns:
            The origin node's position
        """
        return self.m_from.position()

    def position2(self) -> Vector3f:
        """
        Get the position of the destination node.

        Returns:
            The destination node's position
        """
        return self.m_to.position()

    def magnitude(self) -> float:
        """
        Get the length of the way.

        Returns:
            The length (magnitude) of the way
        """
        return self.m_magnitude

    def type(self) -> str:
        """
        Get the way's type name.

        Returns:
            The name of the way type
        """
        return self.m_type.name

    def color(self) -> int:
        """
        Get the way's color.

        Returns:
            The color value as an integer
        """
        return self.m_type.color


class Path:
    """
    Path class representing a graph of nodes and ways.

    A Path is a complete transportation network consisting of Nodes (points)
    connected by Ways (segments). This class manages the collection of nodes
    and ways, and provides methods for building and modifying the network.
    """

    def __init__(self, path_type: PathType):
        """
        Initialize an empty path.

        Args:
            path_type: The type of the path
        """
        self.m_type = path_type
        self.m_nodes: List[Node] = []
        self.m_ways: List[Way] = []
        self.m_nextNodeId = 0
        self.m_nextWayId = 0

    def add_node(self, position: Vector3f) -> Node:
        """
        Create and add a new node to the path.

        Args:
            position: The position for the new node

        Returns:
            The newly created Node
        """
        node = Node(self.m_nextNodeId, position)
        self.m_nodes.append(node)
        self.m_nextNodeId += 1
        return node

    def add_way(self, way_type: WayType, node1: Node, node2: Node) -> Way:
        """
        Create and add a new way connecting two nodes.

        Args:
            way_type: The type of way to create
            node1: The origin node
            node2: The destination node

        Returns:
            The newly created Way
        """
        way = Way(self.m_nextWayId, way_type, node1, node2)
        self.m_ways.append(way)
        self.m_nextWayId += 1
        return way

    def split_way(self, way: Way, offset: float) -> Node:
        """
        Split a way into two segments by creating a new node.

        Args:
            way: The way to split
            offset: Normalized position along the way (0.0 to 1.0)

        Returns:
            The newly created Node at the split point
        """
        # If offset is at an endpoint, return the existing node
        if offset <= 0.0:
            return way.from_()
        elif offset >= 1.0:
            return way.to()

        # Calculate position for the new node
        world_position = way.position1() + (way.position2() - way.position1()) * offset

        # Create the new node
        new_node = self.add_node(world_position)

        # Create a new way from the new node to the original destination
        self.add_way(way.m_type, new_node, way.to())

        # Update the original way to end at the new node
        # First remove it from the original destination node
        way.to().m_ways.remove(way)

        # Change the destination
        way.m_to = new_node

        # Add the way to the new node
        new_node.m_ways.append(way)

        # Update the way's length
        way.update_magnitude()

        return new_node

    def translate(self, direction: Vector3f) -> None:
        """
        Translate all nodes in the path.

        Args:
            direction: Vector representing direction and magnitude of movement
        """
        for node in self.m_nodes:
            node.translate(direction)

    def type(self) -> str:
        """
        Get the path type name.

        Returns:
            The name of the path type
        """
        return self.m_type.name

    def color(self) -> int:
        """
        Get the path color.

        Returns:
            The color value from the path type
        """
        return self.m_type.color

    def nodes(self) -> List[Node]:
        """
        Get the list of nodes in the path.

        Returns:
            List of Node objects
        """
        return self.m_nodes

    def ways(self) -> List[Way]:
        """
        Get the list of ways in the path.

        Returns:
            List of Way objects
        """
        return self.m_ways
