import math
import json
import os

# --- 1. Constants ---
METERS_PER_PIXEL = 67/857   # ≈ 0.0781797
      # CHANGED: from SCALE_RATIO=2.46 to real calibration (20px = 1m)
Human_avg_Speed = .5486         # same
MAX_SPEED = 1.2           # same

node_coordinates = {}
connections = {}

def load_map_data(json_file_path=None):
    global node_coordinates
    global connections
    if json_file_path is None:
        here = os.path.dirname(__file__)
        candidates = [
            os.path.join(here, "college_map_data.json"),
            os.path.join(here, "..", "college_map_data.json")
        ]
        for p in candidates:
            if os.path.exists(p):
                json_file_path = p
                break
    if not json_file_path or not os.path.exists(json_file_path):
        print("Error: Map data file 'college_map_data.json' not found near the script or parent directory.")
        return False
    with open(json_file_path, "r", encoding="utf-8") as f:
        map_data = json.load(f)
    for node_name, data in map_data.items():
        node_coordinates[node_name] = (data["x"], data["y"])
        neighbors = data.get("neighbors", [])
        if neighbors and isinstance(neighbors[0], dict):
            connections[node_name] = [n["name"] for n in neighbors]
        else:
            connections[node_name] = neighbors
    return True

load_map_data()

# --- 4. Helper Functions ---

def calc_dist(n1, n2):
    if n1 not in node_coordinates or n2 not in node_coordinates:
        return float('inf')
    x1, y1 = node_coordinates[n1]
    x2, y2 = node_coordinates[n2]
    dx = x2 - x1                       # CHANGED: added dx for correct Euclidean distance
    dy = y2 - y1                       # CHANGED: added dy for correct Euclidean distance
    return math.sqrt(dx*dx + dy*dy)    # CHANGED: was (dx*2 + dy*2). Now dx^2 + dy^2

def pixels_to_m(dist_pixels):
    return dist_pixels * METERS_PER_PIXEL   # CHANGED: new conversion pixels -> meters

def calculate_time_cost(node_a, node_b):
    dist_pixels = calc_dist(node_a, node_b)
    real_dist_m = pixels_to_m(dist_pixels)  # CHANGED: was dist_pixels * SCALE_RATIO
    return real_dist_m / Human_avg_Speed 

def calculate_heuristic(node, goal):
    dist_pixels = calc_dist(node, goal)
    real_dist_m = pixels_to_m(dist_pixels)  # CHANGED: was dist_pixels * SCALE_RATIO
    return real_dist_m / MAX_SPEED

# --- 5. A* Algorithm (Cumulative Time + Distance) ---

def a_star(start, goal):
    if start not in node_coordinates or goal not in node_coordinates:
        print("Error: Invalid start or goal node names.")
        return None, 0, 0

    # Structure: (node, path, g_time_seconds, g_distance_meters)
    open_list = [(start, [start], 0, 0)]
    closed = []

    while open_list:
        min_f = float('inf')
        best_index = 0

        # Select best node based on f = g_time + h_time
        for i in range(len(open_list)):
            node, path, g_time, g_dist = open_list[i]
            h = calculate_heuristic(node, goal)
            f = g_time + h
            if f < min_f:
                min_f = f
                best_index = i

        current_node, path, g_time, g_dist = open_list.pop(best_index)
        closed.append(current_node)

        if current_node == goal:
            return path, g_time, g_dist

        if current_node in connections:
            for neighbor in connections[current_node]:
                if neighbor not in closed and neighbor not in path:
                    step_pixels = calc_dist(current_node, neighbor)
                    step_meters = pixels_to_m(step_pixels)   # CHANGED: use pixel->meter conversion
                    step_time = step_meters / Human_avg_Speed

                    new_g_time = g_time + step_time
                    new_g_dist = g_dist + step_meters        # CHANGED: distance now meters (correct)

                    new_path = path + [neighbor]

                    in_open = False
                    for j, (o_node, o_path, o_time, o_dist) in enumerate(open_list):
                        if o_node == neighbor:
                            in_open = True
                            if new_g_time < o_time:
                                open_list[j] = (neighbor, new_path, new_g_time, new_g_dist)
                            break

                    if not in_open:
                        open_list.append((neighbor, new_path, new_g_time, new_g_dist))

    return None, float('inf'), float('inf')


# --- 6. Execution Block ---
if __name__ == "__main__":
    start_node = 'Point 8'
    goal_node = 'Point 21'

    path, total_time, total_distance = a_star(start_node, goal_node)

    if path:
        print("\n✅ Path Found!")
        print(" -> ".join(path))
        print("-" * 30)
        print(f"⏱  Total Time:     {total_time:.2f} seconds")
        print(f"📏 Total Distance: {total_distance:.2f} m")  # CHANGED: label was cm but value is meters
        print("-" * 30)
    else:
        print("\n❌ Could not find a path.")
