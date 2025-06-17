from pathfinding_car import CarPathfinder
import matplotlib.pyplot as plt

def demo_wall_proximity_weights():
    print("=== DEMO: Wall Proximity Weighting ===")
    pathfinder = CarPathfinder('floor2.csv')
    
    print(f"Grid size: {pathfinder.rows} x {pathfinder.cols}")
    print("Wall proximity weights calculated - cells near walls have higher costs")
    
    start = (5, 5)
    end = (90, 140)
    
    print(f"\nFinding path from {start} to {end} with wall avoidance...")
    path = pathfinder.astar_pathfind(start, end)
    
    if path:
        print(f"Path found! Length: {len(path)} steps")
        print("The path will prefer routes away from walls when possible")
        
        directions = pathfinder.get_directions(path)
        print(f"\nFirst 10 directions: {directions[:10]}")
        
        pathfinder.visualize_grid(path, start, end)
        
        weighted_costs = []
        for pos in path:
            weight = pathfinder.wall_proximity_weights.get(pos, 1.0)
            weighted_costs.append(weight)
        
        print(f"\nPath cost analysis:")
        print(f"Average weight along path: {sum(weighted_costs)/len(weighted_costs):.2f}")
        print(f"Max weight: {max(weighted_costs):.2f}, Min weight: {min(weighted_costs):.2f}")
    else:
        print("No path found!")

def demo_waypoint_pathfinding():
    print("\n=== DEMO: Waypoint Pathfinding with Color Visualization ===")
    pathfinder = CarPathfinder('floor2.csv')
    
    start = (5, 5)
    waypoints = [(30, 40), (60, 80), (50, 120)]
    end = (90, 140)
    
    print(f"Finding path from {start} through waypoints {waypoints} to {end}")
    
    path, path_segments, segment_colors = pathfinder.pathfind_with_waypoints(start, waypoints, end)
    
    if path:
        print(f"\nComplete path found! Total length: {len(path)} steps")
        print(f"Number of segments: {len(path_segments)}")
        
        print("\n=== SEGMENT BREAKDOWN ===")
        for segment_name, segment_path in path_segments.items():
            segment_directions = pathfinder.get_directions(segment_path)
            color = segment_colors[segment_name]
            print(f"\n{segment_name} (Color: {color}):")
            print(f"  Length: {len(segment_path)} steps")
            print(f"  Start: {segment_path[0]}, End: {segment_path[-1]}")
            print(f"  First 5 directions: {segment_directions[:5]}")
        
        pathfinder.visualize_grid(path, start, end, waypoints, path_segments, segment_colors)
        
        print(f"\nTotal navigation cost:")
        total_cost = 0
        for pos in path:
            cost = pathfinder.wall_proximity_weights.get(pos, 1.0)
            total_cost += cost
        print(f"Total weighted cost: {total_cost:.2f}")
        print(f"Average cost per step: {total_cost/len(path):.2f}")
    else:
        print("No complete path found!")

def demo_comparison():
    print("\n=== DEMO: Comparison with/without Wall Avoidance ===")
    pathfinder = CarPathfinder('floor2.csv')
    
    start = (10, 20)
    end = (80, 120)
    
    print("Finding path with wall avoidance weighting...")
    path_weighted = pathfinder.astar_pathfind(start, end)
    
    original_weights = pathfinder.wall_proximity_weights.copy()
    pathfinder.wall_proximity_weights = {pos: 1.0 for pos in pathfinder.wall_proximity_weights}
    
    print("Finding path without wall avoidance weighting...")
    path_unweighted = pathfinder.astar_pathfind(start, end)
    
    pathfinder.wall_proximity_weights = original_weights
    
    if path_weighted and path_unweighted:
        print(f"\nPath with wall avoidance: {len(path_weighted)} steps")
        print(f"Path without wall avoidance: {len(path_unweighted)} steps")
        
        weighted_cost = sum(pathfinder.wall_proximity_weights.get(pos, 1.0) for pos in path_weighted)
        unweighted_cost = sum(pathfinder.wall_proximity_weights.get(pos, 1.0) for pos in path_unweighted)
        
        print(f"\nSafety comparison (lower = safer from walls):")
        print(f"Wall-avoiding path safety cost: {weighted_cost:.2f}")
        print(f"Regular path safety cost: {unweighted_cost:.2f}")
        print(f"Safety improvement: {((unweighted_cost - weighted_cost) / unweighted_cost * 100):.1f}%")

def main():
    try:
        demo_wall_proximity_weights()
        demo_waypoint_pathfinding()
        demo_comparison()
        
        print("\n=== INTERACTIVE MODE ===")
        print("Run python pathfinding_car.py for interactive mode with all features!")
        
    except FileNotFoundError:
        print("Error: floor2.csv file not found!")
        print("Make sure the grid file is in the current directory.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 