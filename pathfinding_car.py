import csv
import heapq
import matplotlib.pyplot as plt
import numpy as np
import random
from typing import List, Tuple, Optional, Dict

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
        self.wall_proximity_weights = self._calculate_wall_proximity_weights()
        
    def load_grid(self, filename: str) -> List[List[int]]:
        grid = []
        with open(filename, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                grid.append([int(cell) for cell in row])
        return grid
    
    def _calculate_wall_proximity_weights(self) -> Dict[Tuple[int, int], float]:
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
        row, col = position
        min_dist = float('inf')
        
        for r in range(max(0, row-2), min(self.rows, row+3)):
            for c in range(max(0, col-2), min(self.cols, col+3)):
                if self.grid[r][c] == 1:
                    distance = max(abs(r - row), abs(c - col))
                    min_dist = min(min_dist, distance)
        
        return min_dist if min_dist != float('inf') else 3
    
    def visualize_grid(self, path: Optional[List[Tuple[int, int]]] = None, start: Optional[Tuple[int, int]] = None, end: Optional[Tuple[int, int]] = None, waypoints: Optional[List[Tuple[int, int]]] = None, path_segments: Optional[Dict[str, List[Tuple[int, int]]]] = None, segment_colors: Optional[Dict[str, str]] = None):
        fig, ax = plt.subplots(figsize=(15, 10))
        
        grid_array = np.array(self.grid)
        display_grid = grid_array.copy().astype(float)
        
        if path_segments and segment_colors:
            color_map = plt.cm.get_cmap('tab10')
            for i, (segment_name, segment_path) in enumerate(path_segments.items()):
                for pos in segment_path:
                    if pos != start and pos != end and (not waypoints or pos not in waypoints):
                        display_grid[pos[0], pos[1]] = 0.3 + (i * 0.1) % 0.4
        elif path:
            for pos in path:
                if pos != start and pos != end and (not waypoints or pos not in waypoints):
                    display_grid[pos[0], pos[1]] = 0.5
        
        if waypoints:
            for waypoint in waypoints:
                display_grid[waypoint[0], waypoint[1]] = 0.9
        
        if start:
            display_grid[start[0], start[1]] = 0.3
        if end:
            display_grid[end[0], end[1]] = 0.7
        
        im = ax.imshow(display_grid, cmap='RdYlGn_r', vmin=0, vmax=1)
        
        title = 'Car Navigation Grid\nWhite=Free, Black=Obstacle, Green=Start, Red=End'
        if waypoints:
            title += ', Purple=Waypoints'
        if path_segments and segment_colors:
            title += '\nPath Segments: '
            for segment_name, color in segment_colors.items():
                title += f'{segment_name}({color}) '
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        
        if path_segments and segment_colors:
            print("\n=== PATH SEGMENT COLORS ===")
            for segment_name, color in segment_colors.items():
                print(f"{segment_name}: {color}")
        
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
                
                move_cost = self.wall_proximity_weights.get(neighbor, 1.0)
                tentative_g = g_score[current_pos] + move_cost
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current_pos
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, end)
                    
                    neighbor_node = Node(neighbor, tentative_g, self.heuristic(neighbor, end))
                    heapq.heappush(open_list, neighbor_node)
        
        return None
    
    def pathfind_with_waypoints(self, start: Tuple[int, int], waypoints: List[Tuple[int, int]], end: Tuple[int, int]) -> Tuple[Optional[List[Tuple[int, int]]], Dict[str, List[Tuple[int, int]]], Dict[str, str]]:
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        complete_path = []
        path_segments = {}
        segment_colors = {}
        
        current_start = start
        points = waypoints + [end]
        
        for i, target in enumerate(points):
            if any(self.grid[pos[0]][pos[1]] == 1 for pos in [current_start, target]):
                print(f"Error: Position {current_start} or {target} is blocked!")
                return None, {}, {}
            
            segment_path = self.astar_pathfind(current_start, target)
            if segment_path is None:
                print(f"No path found from {current_start} to {target}")
                return None, {}, {}
            
            if i == len(points) - 1:
                segment_name = f"Segment {i+1}: Waypoint {i} -> End"
            else:
                segment_name = f"Segment {i+1}: {'Start' if i == 0 else f'Waypoint {i}'} -> Waypoint {i+1}"
            
            color = random.choice(colors)
            colors.remove(color) if color in colors else None
            
            path_segments[segment_name] = segment_path
            segment_colors[segment_name] = color
            
            if complete_path:
                complete_path.extend(segment_path[1:])
            else:
                complete_path.extend(segment_path)
            
            current_start = target
        
        return complete_path, path_segments, segment_colors
    
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
    
    def get_waypoints_input(self) -> List[Tuple[int, int]]:
        waypoints = []
        print("\nEnter waypoints (optional). Press Enter without input to finish.")
        
        while True:
            try:
                waypoint_input = input(f"Enter waypoint {len(waypoints)+1} (row,col) or press Enter to finish: ").strip()
                if not waypoint_input:
                    break
                
                waypoint_row, waypoint_col = map(int, waypoint_input.split(','))
                waypoint = (waypoint_row, waypoint_col)
                
                if not (0 <= waypoint_row < self.rows and 0 <= waypoint_col < self.cols):
                    print("Waypoint position out of bounds!")
                    continue
                if self.grid[waypoint_row][waypoint_col] == 1:
                    print("Waypoint position is blocked!")
                    continue
                
                waypoints.append(waypoint)
                print(f"Waypoint {len(waypoints)} added: {waypoint}")
                
            except ValueError:
                print("Invalid input! Please enter as: row,col (e.g., 30,40)")
        
        return waypoints
    
    def navigate_car(self):
        print("=== Autonomous Car Navigation System ===")
        print("Loading grid map...")
        
        self.visualize_grid()
        
        start, end = self.get_user_input()
        waypoints = self.get_waypoints_input()
        
        if waypoints:
            print(f"\nFinding path from {start} through waypoints {waypoints} to {end}...")
            path, path_segments, segment_colors = self.pathfind_with_waypoints(start, waypoints, end)
            
            if path is None:
                print("No path found! One or more segments are unreachable.")
                return
            
            directions = self.get_directions(path)
            
            print(f"\nPath found! Total length: {len(path)} steps")
            print(f"Number of segments: {len(path_segments)}")
            
            print("\n=== SEGMENT BREAKDOWN ===")
            for segment_name, segment_path in path_segments.items():
                segment_directions = self.get_directions(segment_path)
                print(f"\n{segment_name} ({segment_colors[segment_name]}):")
                print(f"  Length: {len(segment_path)} steps")
                print(f"  Directions: {segment_directions}")
            
            print(f"\n=== COMPLETE NAVIGATION INSTRUCTIONS ===")
            for i, direction in enumerate(directions, 1):
                print(f"Step {i}: {direction}")
            
            print(f"\n=== PATH COORDINATES ===")
            for i, pos in enumerate(path):
                print(f"Step {i}: {pos}")
            
            print("\n=== VISUALIZATION ===")
            self.visualize_grid(path, start, end, waypoints, path_segments, segment_colors)
            
        else:
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