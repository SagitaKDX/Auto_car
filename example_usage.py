from pathfinding_car import CarPathfinder

def example_usage():
    pathfinder = CarPathfinder('floor2.csv')
    
    start = (12, 17)
    end = (18, 17)
    
    print(f"Finding path from {start} to {end}")
    
    path = pathfinder.astar_pathfind(start, end)
    
    if path:
        directions = pathfinder.get_directions(path)
        
        print(f"Path found! Length: {len(path)} steps")
        print("Directions:", directions)
        
        pathfinder.visualize_grid(path, start, end)
    else:
        print("No path found!")

if __name__ == "__main__":
    example_usage() 