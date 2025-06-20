import serial
import serial.tools.list_ports
import pygame
import time
import csv
import heapq
import numpy as np
from typing import List, Tuple, Optional, Dict

class Node:
    """
    Node class for A* pathfinding algorithm.
    Represents a position in the grid with cost information.
    """
    def __init__(self, position: Tuple[int, int], g_cost: float = 0, h_cost: float = 0, parent=None):
        self.position = position  # Grid coordinates (row, col)
        self.g_cost = g_cost      # Cost from start to this node
        self.h_cost = h_cost      # Heuristic cost from this node to goal
        self.f_cost = g_cost + h_cost  # Total cost (g + h)
        self.parent = parent      # Parent node for path reconstruction
    
    def __lt__(self, other):
        # Comparison method for priority queue ordering
        return self.f_cost < other.f_cost

class CarController:
    """
    Main controller class that handles both manual joystick control and autonomous navigation.
    Integrates A* pathfinding with serial communication to the car.
    """
    def __init__(self, grid_file: str = None):
        # Serial communication setup
        self.serial_conn = None
        self.joystick = None
        
        # Grid and pathfinding properties
        self.grid = None          # 2D grid representing the environment
        self.rows = 0             # Number of rows in grid
        self.cols = 0             # Number of columns in grid
        self.wall_proximity_weights = {}  # Cost weights based on wall proximity
        
        # Autonomous navigation state
        self.current_path = []        # Current calculated path
        self.current_directions = []  # List of movement directions
        self.path_index = 0           # Current step in the path
        self.autonomous_mode = False  # Whether autonomous mode is active
        self.current_position = (0, 0)  # Current car position
        self.target_position = (0, 0)   # Target destination
        
        # Load grid file if provided
        if grid_file:
            self.load_grid(grid_file)
    
    def load_grid(self, filename: str) -> List[List[int]]:
        """
        Load grid map from CSV file.
        0 = free space, 1 = obstacle/wall
        """
        grid = []
        with open(filename, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                grid.append([int(cell) for cell in row])
        
        self.grid = grid
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.wall_proximity_weights = self._calculate_wall_proximity_weights()
        return grid
    
    def _calculate_wall_proximity_weights(self) -> Dict[Tuple[int, int], float]:
        """
        Calculate movement costs based on proximity to walls.
        Higher costs for positions close to walls to encourage safer paths.
        """
        weights = {}
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == 0:  # Only for free spaces
                    min_distance = self._min_distance_to_wall((row, col))
                    if min_distance <= 2:
                        # Higher cost for positions near walls
                        weight = 3.0 - min_distance * 0.5
                        weights[(row, col)] = weight
                    else:
                        weights[(row, col)] = 1.0  # Normal cost
        return weights
    
    def _min_distance_to_wall(self, position: Tuple[int, int]) -> int:
        """
        Calculate minimum distance from a position to the nearest wall.
        Used for determining movement costs.
        """
        row, col = position
        min_dist = float('inf')
        
        # Check 5x5 area around the position
        for r in range(max(0, row-2), min(self.rows, row+3)):
            for c in range(max(0, col-2), min(self.cols, col+3)):
                if self.grid[r][c] == 1:  # Wall found
                    distance = max(abs(r - row), abs(c - col))
                    min_dist = min(min_dist, distance)
        
        return min_dist if min_dist != float('inf') else 3
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Manhattan distance heuristic for A* algorithm.
        Estimates cost from pos1 to pos2.
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions (up, down, left, right).
        Only returns positions that are within grid bounds and not blocked.
        """
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
        
        for dr, dc in directions:
            new_row, new_col = position[0] + dr, position[1] + dc
            
            # Check if position is valid and free
            if (0 <= new_row < self.rows and 
                0 <= new_col < self.cols and 
                self.grid[new_row][new_col] == 0):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def astar_pathfind(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        A* pathfinding algorithm implementation.
        Finds optimal path from start to end position.
        Returns list of coordinates representing the path, or None if no path exists.
        """
        # Validate start and end positions
        if self.grid[start[0]][start[1]] == 1 or self.grid[end[0]][end[1]] == 1:
            print("Error: Start or end position is blocked!")
            return None
        
        open_list = []        # Priority queue for nodes to explore
        closed_set = set()    # Set of already explored positions
        
        # Initialize start node
        start_node = Node(start, 0, self.heuristic(start, end))
        heapq.heappush(open_list, start_node)
        
        came_from = {}        # Track path reconstruction
        g_score = {start: 0}  # Cost from start to each position
        
        while open_list:
            current_node = heapq.heappop(open_list)
            current_pos = current_node.position
            
            # Goal reached
            if current_pos == end:
                # Reconstruct path
                path = []
                while current_pos in came_from:
                    path.append(current_pos)
                    current_pos = came_from[current_pos]
                path.append(start)
                return path[::-1]  # Reverse to get start to end order
            
            closed_set.add(current_pos)
            
            # Explore neighbors
            for neighbor in self.get_neighbors(current_pos):
                if neighbor in closed_set:
                    continue
                
                # Calculate movement cost including wall proximity penalty
                move_cost = self.wall_proximity_weights.get(neighbor, 1.0)
                tentative_g = g_score[current_pos] + move_cost
                
                # Update if this path is better
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current_pos
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, end)
                    
                    neighbor_node = Node(neighbor, tentative_g, self.heuristic(neighbor, end))
                    heapq.heappush(open_list, neighbor_node)
        
        return None  # No path found
    
    def get_directions(self, path: List[Tuple[int, int]]) -> List[str]:
        """
        Convert path coordinates to movement directions.
        Returns list of "UP", "DOWN", "LEFT", "RIGHT" commands.
        """
        if len(path) < 2:
            return []
        
        directions = []
        direction_map = {
            (-1, 0): "UP",      # Moving up in grid
            (1, 0): "DOWN",     # Moving down in grid
            (0, -1): "LEFT",    # Moving left in grid
            (0, 1): "RIGHT"     # Moving right in grid
        }
        
        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]
            
            # Calculate direction vector
            dr = next_pos[0] - current[0]
            dc = next_pos[1] - current[1]
            
            direction = direction_map.get((dr, dc), "UNKNOWN")
            directions.append(direction)
        
        return directions
    
    def list_serial_ports(self):
        """List all available serial ports for car connection."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def connect_serial(self):
        """
        Connect to car via serial communication.
        Prefers /dev/ttyUSB0, falls back to first available port.
        """
        available_ports = self.list_serial_ports()
        port = '/dev/ttyUSB0' if '/dev/ttyUSB0' in available_ports else (available_ports[0] if available_ports else None)
        if not port:
            raise Exception("No serial ports found.")
        self.serial_conn = serial.Serial(port, baudrate=115200, timeout=1)
        return self.serial_conn

    def init_joystick(self):
        """
        Initialize pygame joystick for manual control.
        Connects to the first available controller.
        """
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            raise Exception("No controller found.")
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        return self.joystick

    def get_axes(self):
        """Get current joystick axis values."""
        pygame.event.pump()
        return [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())]

    def generate_mctl_command(self, x: int, y: int, rx: int, rt: float) -> str:
        """
        Generate movement control command from joystick inputs.
        Converts joystick values to car movement commands.
        
        Args:
            x: Left stick horizontal (-100 to 100)
            y: Left stick vertical (-100 to 100)
            rx: Right stick horizontal (-100 to 100)
            rt: Right trigger (0 to 1)
        """
        MIN = 50   # Minimum speed
        MAX = 100  # Maximum speed
        val = MAX if rt > 0.5 else MIN  # Use max speed if trigger pressed

        # Deadzone - no movement if inputs are too small
        if abs(x) < 20 and abs(y) < 20 and abs(rx) < 20:
            return "mctl 0 0"

        # Rotation only (right stick)
        if abs(rx) > 20 and abs(x) < 20 and abs(y) < 20:
            if rx > 20:
                return f"mctl {val} 0"    # Rotate right
            elif rx < -20:
                return f"mctl 0 {val}"    # Rotate left

        # Forward/backward movement (left stick vertical)
        if y < -20:
            return f"mctl {val} {val}"    # Forward
        elif y > 20:
            return f"mctl {-val} {-val}"  # Backward

        return "mctl 0 0"  # Default - stop

    def send_command(self, command: str):
        """
        Send command to car via serial connection.
        Prints the command for debugging.
        """
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(f"{command}\n".encode())
            print(f"Sent: {command}")

    def execute_direction(self, direction: str):
        """
        Execute a single movement direction command.
        Sends command, waits, then stops the car.
        """
        command_map = {
            "UP": "mctl 70 70",      # Forward
            "DOWN": "mctl -70 -70",  # Backward
            "LEFT": "mctl 0 70",     # Turn left
            "RIGHT": "mctl 70 0"     # Turn right
        }
        
        command = command_map.get(direction, "mctl 0 0")
        self.send_command(command)
        time.sleep(0.5)  # Wait for movement to complete
        self.send_command("mctl 0 0")  # Stop

    def set_autonomous_path(self, start: Tuple[int, int], end: Tuple[int, int]):
        """
        Set up autonomous navigation path.
        Calculates path using A* and prepares for execution.
        """
        if not self.grid:
            print("No grid loaded! Please load a grid file first.")
            return False
        
        path = self.astar_pathfind(start, end)
        if path is None:
            print("No path found!")
            return False
        
        self.current_path = path
        self.current_directions = self.get_directions(path)
        self.path_index = 0
        self.current_position = start
        self.target_position = end
        self.autonomous_mode = True
        
        print(f"Autonomous path set: {len(path)} steps")
        print(f"Directions: {self.current_directions}")
        return True

    def autonomous_step(self):
        """
        Execute one step of autonomous navigation.
        Returns True if step executed, False if path complete.
        """
        if not self.autonomous_mode or self.path_index >= len(self.current_directions):
            self.autonomous_mode = False
            return False
        
        direction = self.current_directions[self.path_index]
        print(f"Executing: {direction} (Step {self.path_index + 1}/{len(self.current_directions)})")
        
        self.execute_direction(direction)
        self.path_index += 1
        
        if self.path_index >= len(self.current_directions):
            print("Autonomous navigation completed!")
            self.autonomous_mode = False
        
        return True

    def run_manual_control(self):
        """
        Run manual joystick control mode.
        Continuous loop for joystick input processing.
        """
        print("Manual control mode - Use joystick to control the car")
        print("Press 'q' to quit, 'a' to toggle autonomous mode")
        
        try:
            while True:
                # Get joystick inputs
                axes = self.get_axes()
                if len(axes) >= 4:
                    x, y, rx, rt = [int(axis * 100) for axis in axes[:4]]
                    command = self.generate_mctl_command(x, y, rx, rt)
                    self.send_command(command)
                
                # Handle keyboard events
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            return
                        elif event.key == pygame.K_a and self.grid:
                            self.toggle_autonomous_mode()
                
                time.sleep(0.1)  # Control loop frequency
                
        except KeyboardInterrupt:
            print("\nManual control stopped")

    def toggle_autonomous_mode(self):
        """
        Toggle between manual and autonomous control modes.
        Prompts for start/end positions when activating autonomous mode.
        """
        if not self.grid:
            print("No grid loaded for autonomous mode!")
            return
        
        if not self.autonomous_mode:
            # Get start and end positions from user
            start_input = input("Enter start position (row,col): ").strip()
            end_input = input("Enter end position (row,col): ").strip()
            
            try:
                start = tuple(map(int, start_input.split(',')))
                end = tuple(map(int, end_input.split(',')))
                
                if self.set_autonomous_path(start, end):
                    print("Autonomous mode activated!")
                else:
                    print("Failed to set autonomous path!")
            except ValueError:
                print("Invalid input format! Use: row,col")
        else:
            self.autonomous_mode = False
            print("Autonomous mode deactivated")

    def run_hybrid_control(self):
        """
        Run hybrid control mode combining manual and autonomous control.
        Seamlessly switches between modes based on user input.
        """
        print("Hybrid control mode - Manual joystick + Autonomous navigation")
        print("Controls: Joystick for manual, 'a' for autonomous, 'q' to quit")
        
        try:
            while True:
                if self.autonomous_mode:
                    # Execute autonomous navigation step
                    if not self.autonomous_step():
                        time.sleep(0.1)
                else:
                    # Manual joystick control
                    axes = self.get_axes()
                    if len(axes) >= 4:
                        x, y, rx, rt = [int(axis * 100) for axis in axes[:4]]
                        command = self.generate_mctl_command(x, y, rx, rt)
                        self.send_command(command)
                
                # Handle keyboard events
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            return
                        elif event.key == pygame.K_a and self.grid:
                            self.toggle_autonomous_mode()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nHybrid control stopped")

    def run_autonomous_test(self, start: Tuple[int, int], end: Tuple[int, int], 
                           move_speed: int = 70, move_duration: float = 0.5, 
                           turn_speed: int = 70, turn_duration: float = 0.3,
                           step_delay: float = 0.2):
        """
        Run autonomous navigation test with fixed parameters.
        
        Args:
            start: Starting position (row, col)
            end: Target position (row, col)
            move_speed: Speed for forward/backward movement (0-100)
            move_duration: Duration for each movement step (seconds)
            turn_speed: Speed for turning movements (0-100)
            turn_duration: Duration for each turn step (seconds)
            step_delay: Delay between steps (seconds)
        """
        print(f"=== Autonomous Test Mode ===")
        print(f"Start: {start}, End: {end}")
        print(f"Move Speed: {move_speed}, Move Duration: {move_duration}s")
        print(f"Turn Speed: {turn_speed}, Turn Duration: {turn_duration}s")
        print(f"Step Delay: {step_delay}s")
        
        if not self.grid:
            print("Error: No grid loaded!")
            return False
        
        # Calculate path
        path = self.astar_pathfind(start, end)
        if path is None:
            print("No path found!")
            return False
        
        directions = self.get_directions(path)
        print(f"Path found with {len(directions)} steps: {directions}")
        
        # Execute path step by step
        print("\nStarting autonomous navigation...")
        for i, direction in enumerate(directions):
            print(f"Step {i+1}/{len(directions)}: {direction}")
            
            # Execute movement with custom parameters
            self.execute_test_direction(direction, move_speed, move_duration, 
                                      turn_speed, turn_duration)
            
            # Wait between steps
            if i < len(directions) - 1:  # Don't wait after last step
                time.sleep(step_delay)
        
        print("Autonomous test completed!")
        return True

    def execute_test_direction(self, direction: str, move_speed: int, move_duration: float,
                              turn_speed: int, turn_duration: float):
        """
        Execute a movement direction with configurable parameters for testing.
        
        Args:
            direction: Movement direction ("UP", "DOWN", "LEFT", "RIGHT")
            move_speed: Speed for forward/backward movement
            move_duration: Duration for movement
            turn_speed: Speed for turning
            turn_duration: Duration for turning
        """
        if direction in ["UP", "DOWN"]:
            # Forward/backward movement
            if direction == "UP":
                command = f"mctl {move_speed} {move_speed}"
            else:  # DOWN
                command = f"mctl -{move_speed} -{move_speed}"
            
            self.send_command(command)
            time.sleep(move_duration)
            self.send_command("mctl 0 0")
            
        elif direction in ["LEFT", "RIGHT"]:
            # Turning movement
            if direction == "LEFT":
                command = f"mctl 0 {turn_speed}"
            else:  # RIGHT
                command = f"mctl {turn_speed} 0"
            
            self.send_command(command)
            time.sleep(turn_duration)
            self.send_command("mctl 0 0")
        
        else:
            print(f"Unknown direction: {direction}")
            self.send_command("mctl 0 0")

def run_fixed_scenario():
    """
    Run a fixed test scenario with predefined parameters.
    All connections are automatic, just runs the test.
    """
    # Fixed test parameters - modify these for your experiments
    GRID_FILE = "floor2.csv"
    START_POS = (12, 17)
    END_POS = (18, 17)
    
    # Movement parameters for testing/configuration
    MOVE_SPEED = 70        # Speed for forward/backward (0-100)
    MOVE_DURATION = 0.5    # How long to move forward/backward (seconds)
    TURN_SPEED = 70        # Speed for turning (0-100)
    TURN_DURATION = 0.3    # How long to turn (seconds)
    STEP_DELAY = 0.2       # Delay between movement steps (seconds)
    
    controller = CarController()
    
    try:
        print("=== Fixed Scenario Test ===")
        print("Setting up connections...")
        
        # Load grid
        controller.load_grid(GRID_FILE)
        print(f"Grid loaded from {GRID_FILE}")
        
        # Connect to car
        controller.connect_serial()
        print("Serial connection established")
        
        # Run autonomous test
        success = controller.run_autonomous_test(
            start=START_POS,
            end=END_POS,
            move_speed=MOVE_SPEED,
            move_duration=MOVE_DURATION,
            turn_speed=TURN_SPEED,
            turn_duration=TURN_DURATION,
            step_delay=STEP_DELAY
        )
        
        if success:
            print("Test scenario completed successfully!")
        else:
            print("Test scenario failed!")
            
    except Exception as e:
        print(f"Error in test scenario: {e}")
    finally:
        if controller.serial_conn:
            controller.serial_conn.close()
            print("Serial connection closed")

def main():
    """
    Main function - entry point for the car controller application.
    Provides menu for selecting control mode and initializes the system.
    """
    controller = CarController()
    
    try:
        print("=== Auto Car Controller ===")
        print("1. Manual control only")
        print("2. Hybrid control (manual + autonomous)")
        print("3. Load grid and start hybrid control")
        print("4. Run fixed test scenario")
        
        choice = input("Select mode (1-4): ").strip()
        
        if choice == "4":
            # Run fixed scenario without further input
            run_fixed_scenario()
            return
        
        # Initialize hardware connections for other modes
        controller.connect_serial()
        controller.init_joystick()
        
        # Run selected mode
        if choice == "1":
            controller.run_manual_control()
        elif choice == "2":
            controller.run_hybrid_control()
        elif choice == "3":
            grid_file = input("Enter grid file path (e.g., floor2.csv): ").strip()
            controller.load_grid(grid_file)
            controller.run_hybrid_control()
        else:
            print("Invalid choice!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up serial connection
        if controller.serial_conn:
            controller.serial_conn.close()

if __name__ == "__main__":
    main()
