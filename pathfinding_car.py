import csv
import heapq
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Optional

class Node:
    def __init__(self, position: Tuple[int, int], g_cost: float = 0, h_cost: float = 0, parent=None):
        self.position = position
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost
        self.parent = parent
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost

class CarPathfinder:
    def __init__(self, grid_file: str):
        self.grid = self.load_grid(grid_file)
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        
    def load_grid(self, filename: str) -> List[List[int]]:
        grid = []
        with open(filename, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                grid.append([int(cell) for cell in row])
        return grid
    
    def visualize_grid(self, path: Optional[List[Tuple[int, int]]] = None, start: Optional[Tuple[int, int]] = None, end: Optional[Tuple[int, int]] = None):
        fig, ax = plt.subplots(figsize=(15, 10))
        
        grid_array = np.array(self.grid)
        display_grid = grid_array.copy().astype(float)
        
        if path:
            for pos in path:
                if pos != start and pos != end:
                    display_grid[pos[0], pos[1]] = 0.5
        
        if start:
            display_grid[start[0], start[1]] = 0.3
        if end:
            display_grid[end[0], end[1]] = 0.7
        
        colors = ['white', 'black', 'green', 'blue', 'red']
        bounds = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        
        im = ax.imshow(display_grid, cmap='RdYlGn_r', vmin=0, vmax=1)
        
        ax.set_title('Car Navigation Grid\nWhite=Free, Black=Obstacle, Green=Start, Blue=Path, Red=End')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        
        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        plt.show()
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dr, dc in directions:
            new_row, new_col = position[0] + dr, position[1] + dc
            
            if (0 <= new_row < self.rows and 
                0 <= new_col < self.cols and 
                self.grid[new_row][new_col] == 0):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def astar_pathfind(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        if self.grid[start[0]][start[1]] == 1 or self.grid[end[0]][end[1]] == 1:
            print("Error: Start or end position is blocked!")
            return None
        
        open_list = []
        closed_set = set()
        
        start_node = Node(start, 0, self.heuristic(start, end))
        heapq.heappush(open_list, start_node)
        
        came_from = {}
        g_score = {start: 0}
        
        while open_list:
            current_node = heapq.heappop(open_list)
            current_pos = current_node.position
            
            if current_pos == end:
                path = []
                while current_pos in came_from:
                    path.append(current_pos)
                    current_pos = came_from[current_pos]
                path.append(start)
                return path[::-1]
            
            closed_set.add(current_pos)
            
            for neighbor in self.get_neighbors(current_pos):
                if neighbor in closed_set:
                    continue
                
                tentative_g = g_score[current_pos] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current_pos
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, end)
                    
                    neighbor_node = Node(neighbor, tentative_g, self.heuristic(neighbor, end))
                    heapq.heappush(open_list, neighbor_node)
        
        return None
    
    def get_directions(self, path: List[Tuple[int, int]]) -> List[str]:
        if len(path) < 2:
            return []
        
        directions = []
        direction_map = {
            (-1, 0): "UP",
            (1, 0): "DOWN", 
            (0, -1): "LEFT",
            (0, 1): "RIGHT"
        }
        
        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]
            
            dr = next_pos[0] - current[0]
            dc = next_pos[1] - current[1]
            
            direction = direction_map.get((dr, dc), "UNKNOWN")
            directions.append(direction)
        
        return directions
    
    def get_user_input(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        print(f"Grid dimensions: {self.rows} rows x {self.cols} columns")
        print("Enter coordinates as (row, column) where (0,0) is top-left")
        
        while True:
            try:
                start_input = input("Enter start position (row,col): ").strip()
                start_row, start_col = map(int, start_input.split(','))
                start = (start_row, start_col)
                
                if not (0 <= start_row < self.rows and 0 <= start_col < self.cols):
                    print("Start position out of bounds!")
                    continue
                if self.grid[start_row][start_col] == 1:
                    print("Start position is blocked!")
                    continue
                break
            except ValueError:
                print("Invalid input! Please enter as: row,col (e.g., 10,20)")
        
        while True:
            try:
                end_input = input("Enter end position (row,col): ").strip()
                end_row, end_col = map(int, end_input.split(','))
                end = (end_row, end_col)
                
                if not (0 <= end_row < self.rows and 0 <= end_col < self.cols):
                    print("End position out of bounds!")
                    continue
                if self.grid[end_row][end_col] == 1:
                    print("End position is blocked!")
                    continue
                break
            except ValueError:
                print("Invalid input! Please enter as: row,col (e.g., 50,80)")
        
        return start, end
    
    def navigate_car(self):
        print("=== Autonomous Car Navigation System ===")
        print("Loading grid map...")
        
        self.visualize_grid()
        
        start, end = self.get_user_input()
        
        print(f"\nFinding path from {start} to {end}...")
        path = self.astar_pathfind(start, end)
        
        if path is None:
            print("No path found! The destination is unreachable.")
            return
        
        directions = self.get_directions(path)
        
        print(f"\nPath found! Length: {len(path)} steps")
        print("\n=== NAVIGATION INSTRUCTIONS ===")
        for i, direction in enumerate(directions, 1):
            print(f"Step {i}: {direction}")
        
        print(f"\n=== PATH COORDINATES ===")
        for i, pos in enumerate(path):
            print(f"Step {i}: {pos}")
        
        print("\n=== VISUALIZATION ===")
        self.visualize_grid(path, start, end)
        
        return path, directions

def main():
    try:
        pathfinder = CarPathfinder('floor2.csv')
        path, directions = pathfinder.navigate_car()
    except FileNotFoundError:
        print("Error: floor2.csv file not found!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 