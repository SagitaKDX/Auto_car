import heapq
import json
from typing import List, Tuple, Optional, Dict
from node import Node
from map import GridMap

class PathfindingAlgorithm:
    """
    A* pathfinding algorithm implementation.
    Finds optimal paths and returns results in JSON format.
    """
    
    def __init__(self, grid_map: GridMap):
        """
        Initialize pathfinding algorithm with a grid map.
        
        Args:
            grid_map: GridMap instance containing the environment
        """
        self.grid_map = grid_map
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Manhattan distance heuristic for A* algorithm.
        
        Args:
            pos1: First position (row, col)
            pos2: Second position (row, col)
            
        Returns:
            Heuristic distance between positions
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def astar_pathfind(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        A* pathfinding algorithm implementation.
        
        Args:
            start: Starting position (row, col)
            end: Target position (row, col)
            
        Returns:
            List of coordinates representing the path, or None if no path exists
        """
        if not self.grid_map.is_valid_position(start) or not self.grid_map.is_valid_position(end):
            print("Error: Start or end position is blocked or invalid!")
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
            
            for neighbor in self.grid_map.get_neighbors(current_pos):
                if neighbor in closed_set:
                    continue
                
                move_cost = self.grid_map.get_movement_cost(neighbor)
                tentative_g = g_score[current_pos] + move_cost
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current_pos
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, end)
                    
                    neighbor_node = Node(neighbor, tentative_g, self.heuristic(neighbor, end))
                    heapq.heappush(open_list, neighbor_node)
        
        return None
    
    def get_directions(self, path: List[Tuple[int, int]]) -> List[str]:
        """
        Convert path coordinates to movement directions.
        
        Args:
            path: List of coordinates representing the path
            
        Returns:
            List of direction commands ("UP", "DOWN", "LEFT", "RIGHT")
        """
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
    
    def find_path_with_json_output(self, start: Tuple[int, int], end: Tuple[int, int], 
                                  output_file: str = None) -> Dict:
        """
        Find path and return/save results in JSON format.
        
        Args:
            start: Starting position (row, col)
            end: Target position (row, col)
            output_file: Optional file path to save JSON output
            
        Returns:
            Dictionary containing path information in JSON format
        """
        print(f"Finding path from {start} to {end}...")
        
        path = self.astar_pathfind(start, end)
        
        if path is None:
            result = {
                "success": False,
                "message": "No path found",
                "start": start,
                "end": end,
                "path": [],
                "commands": [],
                "path_length": 0
            }
        else:
            directions = self.get_directions(path)
            
            result = {
                "success": True,
                "message": "Path found successfully",
                "start": start,
                "end": end,
                "path": path,
                "commands": directions,
                "path_length": len(path),
                "steps": len(directions),
                "detailed_steps": []
            }
            
            for i, (position, command) in enumerate(zip(path[:-1], directions)):
                step_info = {
                    "step": i + 1,
                    "from_position": position,
                    "to_position": path[i + 1],
                    "command": command
                }
                result["detailed_steps"].append(step_info)
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Results saved to {output_file}")
            except Exception as e:
                print(f"Error saving to file: {e}")
        
        return result
    
    def pathfind_with_waypoints(self, start: Tuple[int, int], waypoints: List[Tuple[int, int]], 
                               end: Tuple[int, int], output_file: str = None) -> Dict:
        """
        Find path through multiple waypoints and return JSON results.
        
        Args:
            start: Starting position
            waypoints: List of waypoint positions to visit in order
            end: Final destination
            output_file: Optional file path to save JSON output
            
        Returns:
            Dictionary containing complete path information
        """
        print(f"Finding path from {start} through waypoints {waypoints} to {end}...")
        
        complete_path = []
        complete_commands = []
        segments = []
        
        current_start = start
        points = waypoints + [end]
        
        for i, target in enumerate(points):
            segment_path = self.astar_pathfind(current_start, target)
            
            if segment_path is None:
                result = {
                    "success": False,
                    "message": f"No path found from {current_start} to {target}",
                    "start": start,
                    "waypoints": waypoints,
                    "end": end,
                    "failed_segment": i + 1,
                    "complete_path": [],
                    "complete_commands": [],
                    "segments": []
                }
                
                if output_file:
                    with open(output_file, 'w') as f:
                        json.dump(result, f, indent=2)
                
                return result
            
            segment_commands = self.get_directions(segment_path)
            
            segment_info = {
                "segment": i + 1,
                "from": current_start,
                "to": target,
                "path": segment_path,
                "commands": segment_commands,
                "length": len(segment_path),
                "steps": len(segment_commands)
            }
            segments.append(segment_info)
            
            if complete_path:
                complete_path.extend(segment_path[1:])
                complete_commands.extend(segment_commands)
            else:
                complete_path.extend(segment_path)
                complete_commands.extend(segment_commands)
            
            current_start = target
        
        result = {
            "success": True,
            "message": "Multi-waypoint path found successfully",
            "start": start,
            "waypoints": waypoints,
            "end": end,
            "complete_path": complete_path,
            "complete_commands": complete_commands,
            "total_length": len(complete_path),
            "total_steps": len(complete_commands),
            "segments": segments,
            "segment_count": len(segments)
        }
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Multi-waypoint results saved to {output_file}")
            except Exception as e:
                print(f"Error saving to file: {e}")
        
        return result
    
    def print_path_summary(self, result: Dict):
        """
        Print a summary of pathfinding results.
        
        Args:
            result: Dictionary containing pathfinding results
        """
        if not result["success"]:
            print(f"❌ {result['message']}")
            return
        
        print(f"✅ {result['message']}")
        print(f"📍 Start: {result['start']}")
        print(f"🎯 End: {result['end']}")
        
        if "waypoints" in result and result["waypoints"]:
            print(f"🗺️  Waypoints: {result['waypoints']}")
        
        if "total_length" in result:
            print(f"📏 Total path length: {result['total_length']} positions")
            print(f"🎮 Total commands: {result['total_steps']}")
            print(f"🔗 Segments: {result['segment_count']}")
        else:
            print(f"📏 Path length: {result['path_length']} positions")
            print(f"🎮 Commands: {result['steps']}")
        
        print(f"🎮 Command sequence: {result.get('complete_commands', result.get('commands', []))}")

def main():
    """
    Example usage of the pathfinding algorithm.
    """
    try:
        grid_map = GridMap("floor2.csv")
        pathfinder = PathfindingAlgorithm(grid_map)
        
        grid_map.print_grid_info()
        
        start = (12, 17)
        end = (18, 17)
        
        result = pathfinder.find_path_with_json_output(start, end, "path_result.json")
        pathfinder.print_path_summary(result)
        
        waypoints = [(15, 20), (15, 10)]
        waypoint_result = pathfinder.pathfind_with_waypoints(start, waypoints, end, "waypoint_result.json")
        pathfinder.print_path_summary(waypoint_result)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 