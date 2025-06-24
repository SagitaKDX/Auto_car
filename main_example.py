#!/usr/bin/env python3
"""
Example usage of the divided pathfinding system.
Demonstrates how to use the 4 separate modules together.
"""

from map import GridMap
from algorithm import PathfindingAlgorithm
from carcontroller import CarController
from node import Node

def simple_pathfinding_example():
    """
    Simple example showing pathfinding without car control.
    """
    print("=== Simple Pathfinding Example ===")
    
    try:
        grid_map = GridMap("floor2.csv")
        pathfinder = PathfindingAlgorithm(grid_map)
        
        grid_map.print_grid_info()
        
        start = (12, 17)
        end = (18, 17)
        
        result = pathfinder.find_path_with_json_output(start, end, "simple_path.json")
        pathfinder.print_path_summary(result)
        
        return result
        
    except Exception as e:
        print(f"Error in simple example: {e}")
        return None

def waypoint_pathfinding_example():
    """
    Example with waypoints.
    """
    print("\n=== Waypoint Pathfinding Example ===")
    
    try:
        grid_map = GridMap("floor2.csv")
        pathfinder = PathfindingAlgorithm(grid_map)
        
        start = (10, 15)
        waypoints = [(15, 20), (20, 15), (15, 10)]
        end = (10, 15)
        
        result = pathfinder.pathfind_with_waypoints(start, waypoints, end, "waypoint_path.json")
        pathfinder.print_path_summary(result)
        
        return result
        
    except Exception as e:
        print(f"Error in waypoint example: {e}")
        return None

def car_integration_example():
    """
    Example showing integration with car controller.
    Note: Car movement functions are blank as requested.
    """
    print("\n=== Car Integration Example ===")
    
    try:
        grid_map = GridMap("floor2.csv")
        pathfinder = PathfindingAlgorithm(grid_map)
        car_controller = CarController()
        
        start = (12, 17)
        end = (18, 17)
        
        result = pathfinder.find_path_with_json_output(start, end)
        
        if result["success"]:
            print(f"Path found! Executing {len(result['commands'])} commands...")
            
            for i, command in enumerate(result["commands"]):
                print(f"Step {i+1}: {command}")
                
                if command == "UP":
                    car_controller.move_up()
                elif command == "DOWN":
                    car_controller.move_down()
                elif command == "LEFT":
                    car_controller.move_left()
                elif command == "RIGHT":
                    car_controller.move_right()
                
                print(f"  Executed: {command} (function is blank)")
            
            car_controller.stop()
            print("Navigation complete!")
        else:
            print("No path found for car navigation")
        
        return result
        
    except Exception as e:
        print(f"Error in car integration: {e}")
        return None

def interactive_pathfinding():
    """
    Interactive example where user can input start and end positions.
    """
    print("\n=== Interactive Pathfinding ===")
    
    try:
        grid_map = GridMap("floor2.csv")
        pathfinder = PathfindingAlgorithm(grid_map)
        
        print(f"Grid dimensions: {grid_map.rows} x {grid_map.cols}")
        print("Enter coordinates as row,col (e.g., 12,17)")
        
        start_input = input("Enter start position: ").strip()
        end_input = input("Enter end position: ").strip()
        
        start = tuple(map(int, start_input.split(',')))
        end = tuple(map(int, end_input.split(',')))
        
        output_file = input("Enter output filename (or press Enter for no file): ").strip()
        output_file = output_file if output_file else None
        
        result = pathfinder.find_path_with_json_output(start, end, output_file)
        pathfinder.print_path_summary(result)
        
        return result
        
    except ValueError:
        print("Invalid input format! Use: row,col")
        return None
    except Exception as e:
        print(f"Error in interactive example: {e}")
        return None

def main():
    """
    Main function demonstrating all examples.
    """
    print("Auto Car Pathfinding System - Modular Examples")
    print("=" * 50)
    
    while True:
        print("\nSelect an example:")
        print("1. Simple pathfinding (JSON output)")
        print("2. Waypoint pathfinding")
        print("3. Car integration example")
        print("4. Interactive pathfinding")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            simple_pathfinding_example()
        elif choice == "2":
            waypoint_pathfinding_example()
        elif choice == "3":
            car_integration_example()
        elif choice == "4":
            interactive_pathfinding()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please select 1-5.")

if __name__ == "__main__":
    main() 