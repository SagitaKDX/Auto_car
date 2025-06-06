# Autonomous Car Pathfinding System

This system implements A* pathfinding algorithm for autonomous car navigation using a grid-based map from `floor2.csv`.

## Features

- **Grid Visualization**: Visual representation of the map with obstacles and free spaces
- **A* Pathfinding**: Efficient shortest path finding algorithm
- **Interactive Input**: User-friendly input system for start and end positions
- **Direction Output**: Step-by-step directions (UP, DOWN, LEFT, RIGHT)
- **Path Visualization**: Visual display of the found path on the grid

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
4. Find the shortest path using A*
5. Display step-by-step directions
6. Show the path on the grid

### Programmatic Usage

```python
from pathfinding_car import CarPathfinder

# Initialize pathfinder
pathfinder = CarPathfinder('floor2.csv')

# Define start and end positions
start = (10, 20)  # (row, col)
end = (80, 120)

# Find path
path = pathfinder.astar_pathfind(start, end)

if path:
    # Get directions
    directions = pathfinder.get_directions(path)
    print("Directions:", directions)
    
    # Visualize
    pathfinder.visualize_grid(path, start, end)
```

## Input Format

When prompted, enter coordinates as: `row,col`

Example:
- Start position: `10,20`
- End position: `80,120`

**Note**: Coordinates are 0-indexed, with (0,0) at the top-left corner.

## Output

The system provides:

1. **Step-by-step directions**:
   ```
   Step 1: RIGHT
   Step 2: DOWN
   Step 3: RIGHT
   ...
   ```

2. **Path coordinates**:
   ```
   Step 0: (10, 20)
   Step 1: (10, 21)
   Step 2: (11, 21)
   ...
   ```

3. **Visual map** showing:
   - White: Free space
   - Black: Obstacles
   - Green: Start position
   - Blue: Path
   - Red: End position

## Algorithm Details

- **A* Algorithm**: Uses Manhattan distance as heuristic
- **Movement**: 4-directional (up, down, left, right)
- **Pathfinding**: Guarantees shortest path if one exists
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