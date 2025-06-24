import csv
from typing import List, Tuple, Dict

class GridMap:
    """
    Grid map class for loading and managing the navigation environment.
    Handles CSV file loading and grid-related operations.
    """
    
    def __init__(self, grid_file: str = None):
        """
        Initialize grid map.
        
        Args:
            grid_file: Path to CSV grid file (optional)
        """
        self.grid = None
        self.rows = 0
        self.cols = 0
        self.wall_proximity_weights = {}
        
        if grid_file:
            self.load_grid(grid_file)
    
    def load_grid(self, filename: str) -> List[List[int]]:
        """
        Load grid map from CSV file.
        Grid format: 0 = free space, 1 = obstacle/wall
        
        Args:
            filename: Path to CSV file
            
        Returns:
            2D list representing the grid
        """
        grid = []
        try:
            with open(filename, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    grid.append([int(cell) for cell in row])
            
            self.grid = grid
            self.rows = len(self.grid)
            self.cols = len(self.grid[0]) if self.grid else 0
            self.wall_proximity_weights = self._calculate_wall_proximity_weights()
            
            print(f"Grid loaded successfully: {self.rows}x{self.cols}")
            return grid
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Grid file '{filename}' not found")
        except Exception as e:
            raise Exception(f"Error loading grid: {e}")
    
    def _calculate_wall_proximity_weights(self) -> Dict[Tuple[int, int], float]:
        """
        Calculate movement costs based on proximity to walls.
        Higher costs for positions close to walls encourage safer paths.
        
        Returns:
            Dictionary mapping positions to movement weights
        """
        weights = {}
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 0:
                    min_distance = self._min_distance_to_wall((row, col))
                    if min_distance <= 2:
                        weight = 3.0 - min_distance * 0.5
                        weights[(row, col)] = weight
                    else:
                        weights[(row, col)] = 1.0
        return weights
    
    def _min_distance_to_wall(self, position: Tuple[int, int]) -> int:
        """
        Calculate minimum distance from a position to the nearest wall.
        
        Args:
            position: Grid coordinates (row, col)
            
        Returns:
            Minimum distance to nearest wall
        """
        row, col = position
        min_dist = float('inf')
        
        for r in range(max(0, row-2), min(self.rows, row+3)):
            for c in range(max(0, col-2), min(self.cols, col+3)):
                if self.grid[r][c] == 1:
                    distance = max(abs(r - row), abs(c - col))
                    min_dist = min(min_dist, distance)
        
        return min_dist if min_dist != float('inf') else 3
    
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """
        Check if a position is valid and free.
        
        Args:
            position: Grid coordinates (row, col)
            
        Returns:
            True if position is valid and free, False otherwise
        """
        row, col = position
        return (0 <= row < self.rows and 
                0 <= col < self.cols and 
                self.grid[row][col] == 0)
    
    def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions (up, down, left, right).
        
        Args:
            position: Current grid coordinates (row, col)
            
        Returns:
            List of valid neighboring positions
        """
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dr, dc in directions:
            new_row, new_col = position[0] + dr, position[1] + dc
            
            if self.is_valid_position((new_row, new_col)):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def get_movement_cost(self, position: Tuple[int, int]) -> float:
        """
        Get movement cost for a position based on wall proximity.
        
        Args:
            position: Grid coordinates (row, col)
            
        Returns:
            Movement cost (higher near walls)
        """
        return self.wall_proximity_weights.get(position, 1.0)
    
    def print_grid_info(self):
        """Print information about the loaded grid."""
        if not self.grid:
            print("No grid loaded")
            return
        
        free_spaces = sum(row.count(0) for row in self.grid)
        obstacles = sum(row.count(1) for row in self.grid)
        total = self.rows * self.cols
        
        print(f"Grid Information:")
        print(f"  Dimensions: {self.rows} x {self.cols}")
        print(f"  Total cells: {total}")
        print(f"  Free spaces: {free_spaces} ({free_spaces/total*100:.1f}%)")
        print(f"  Obstacles: {obstacles} ({obstacles/total*100:.1f}%)")
    
    def get_grid_bounds(self) -> Tuple[int, int]:
        """
        Get grid dimensions.
        
        Returns:
            Tuple of (rows, cols)
        """
        return self.rows, self.cols 