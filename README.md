# Autonomous Car Pathfinding System

This system implements A* pathfinding algorithm for autonomous car navigation using a grid-based map from `floor2.csv`.

## Features

- **Grid Visualization**: Visual representation of the map with obstacles and free spaces
- **A* Pathfinding**: Efficient shortest path finding algorithm with wall proximity weighting
- **Wall Avoidance**: Increased cost for cells near walls (within 2 cells) to keep car safer
- **Waypoint Navigation**: Support for intermediate waypoints with color-coded path segments
- **Interactive Input**: User-friendly input system for start, end, and waypoint positions
- **Direction Output**: Step-by-step directions (UP, DOWN, LEFT, RIGHT)
- **Path Visualization**: Visual display of paths with different colors for each segment

## Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Grid Format

The `floor2.csv` file should contain:
- `1` = Obstacle/Wall (car cannot pass)
- `0` = Free space (car can move)

## Usage

### Interactive Mode

Run the main script for interactive navigation:

```bash
python pathfinding_car.py
```

This will:
1. Display the grid map
2. Ask for start position (row, col)
3. Ask for end position (row, col)
4. Ask for optional waypoints (can add multiple)
5. Find the shortest path using A* with wall avoidance
6. Display step-by-step directions for each segment
7. Show the path on the grid with color-coded segments

### Demo Mode

Run the demo script to see all features:

```bash
python demo_enhanced_pathfinding.py
```

This demonstrates:
- Wall proximity weighting effects
- Waypoint pathfinding with color visualization
- Comparison between weighted and unweighted paths

### Programmatic Usage

#### Basic Pathfinding with Wall Avoidance

```python
from pathfinding_car import CarPathfinder

# Initialize pathfinder (automatically calculates wall proximity weights)
pathfinder = CarPathfinder('floor2.csv')

# Define start and end positions
start = (10, 20)  # (row, col)
end = (80, 120)

# Find path with wall avoidance
path = pathfinder.astar_pathfind(start, end)

if path:
    # Get directions
    directions = pathfinder.get_directions(path)
    print("Directions:", directions)
    
    # Visualize
    pathfinder.visualize_grid(path, start, end)
```

#### Waypoint Navigation

```python
from pathfinding_car import CarPathfinder

pathfinder = CarPathfinder('floor2.csv')

start = (10, 20)
waypoints = [(30, 40), (50, 60)]  # Intermediate points
end = (80, 120)

# Find path through waypoints
path, segments, colors = pathfinder.pathfind_with_waypoints(start, waypoints, end)

if path:
    print("Complete path found!")
    print(f"Segments: {list(segments.keys())}")
    print(f"Colors: {colors}")
    
    # Visualize with color-coded segments
    pathfinder.visualize_grid(path, start, end, waypoints, segments, colors)
```

## Input Format

When prompted, enter coordinates as: `row,col`

Example:
- Start position: `10,20`
- End position: `80,120`
- Waypoint 1: `30,40`
- Waypoint 2: `50,60`

**Note**: Coordinates are 0-indexed, with (0,0) at the top-left corner.

For waypoints, press Enter without input to finish adding waypoints.

## Output

The system provides:

1. **Segment breakdown** (with waypoints):
   ```
   Segment 1: Start -> Waypoint 1 (red)
     Length: 25 steps
     Directions: ['RIGHT', 'DOWN', 'RIGHT', ...]
   
   Segment 2: Waypoint 1 -> End (blue)
     Length: 42 steps
     Directions: ['UP', 'RIGHT', 'DOWN', ...]
   ```

2. **Complete step-by-step directions**:
   ```
   Step 1: RIGHT
   Step 2: DOWN
   Step 3: RIGHT
   ...
   ```

3. **Path coordinates**:
   ```
   Step 0: (10, 20)
   Step 1: (10, 21)
   Step 2: (11, 21)
   ...
   ```

4. **Visual map** showing:
   - White: Free space
   - Black: Obstacles
   - Green: Start position
   - Purple: Waypoints
   - Different colors: Path segments
   - Red: End position

5. **Path segment colors list** displaying which color represents each segment

## Algorithm Details

- **A* Algorithm**: Uses Manhattan distance as heuristic
- **Wall Proximity Weighting**: Cells within 2 cells of walls have increased cost (3.0 to 2.0)
- **Movement**: 4-directional (up, down, left, right)
- **Pathfinding**: Finds safest path balancing distance and wall avoidance
- **Waypoint Support**: Connects multiple points with optimal segments
- **Efficiency**: Optimized with priority queue (heapq)

## Error Handling

The system handles:
- Invalid coordinates (out of bounds)
- Blocked start/end positions
- Unreachable destinations
- File not found errors

## For Autonomous Car Integration

The direction output can be directly used for car control:

```python
direction_to_action = {
    "UP": move_forward,
    "DOWN": move_backward, 
    "LEFT": turn_left,
    "RIGHT": turn_right
}

for direction in directions:
    direction_to_action[direction]()
``` 