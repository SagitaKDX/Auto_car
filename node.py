from typing import Tuple, Optional

class Node:
    """
    Node class for A* pathfinding algorithm.
    Represents a position in the grid with cost information for pathfinding.
    """
    
    def __init__(self, position: Tuple[int, int], g_cost: float = 0, h_cost: float = 0, parent: Optional['Node'] = None):
        """
        Initialize a node for pathfinding.
        
        Args:
            position: Grid coordinates (row, col)
            g_cost: Cost from start to this node
            h_cost: Heuristic cost from this node to goal
            parent: Parent node for path reconstruction
        """
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = parent
    
    def __lt__(self, other: 'Node') -> bool:
        """
        Comparison method for priority queue ordering.
        Nodes with lower f_cost have higher priority.
        """
        return self.f_cost < other.f_cost
    
    def __eq__(self, other: 'Node') -> bool:
        """Check if two nodes are at the same position."""
        return self.position == other.position
    
    def __hash__(self) -> int:
        """Hash method for using nodes in sets and dictionaries."""
        return hash(self.position)
    
    def __repr__(self) -> str:
        """String representation of the node."""
        return f"Node(pos={self.position}, f={self.f_cost:.1f}, g={self.g_cost:.1f}, h={self.h_cost:.1f})"
    
    def update_costs(self, g_cost: float, h_cost: float, parent: Optional['Node'] = None):
        """
        Update node costs and parent.
        
        Args:
            g_cost: New cost from start
            h_cost: New heuristic cost
            parent: New parent node
        """
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        if parent:
            self.parent = parent
    
    def get_path(self) -> list:
        """
        Reconstruct path from this node back to start.
        Returns list of positions from start to this node.
        """
        path = []
        current = self
        while current:
            path.append(current.position)
            current = current.parent
        return path[::-1] 