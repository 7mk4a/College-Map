import math
import json
import os

# --- 1. Constants ---
METERS_PER_PIXEL = 67/857   # ≈ 0.0781797
Human_avg_Speed = .5486   
MAX_SPEED = 1.2           

# --- 2. Data Structures ---
node_coordinates = {}
connections = {}
node_types = {}
node_floors = {}

def load_map_data(json_file_path=None):
    global node_coordinates, connections, node_types, node_floors

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
        print("Error: Map data file 'college_map_data.json' not found.")
        return False

    with open(json_file_path, "r", encoding="utf-8") as f:
        map_data = json.load(f)

    for node_name, data in map_data.items():
        # Coordinates
        node_coordinates[node_name] = (data["x"], data["y"])

        # Neighbors
        neighbors = data.get("neighbors", [])
        if neighbors and isinstance(neighbors[0], dict):
            connections[node_name] = [n["name"] for n in neighbors]
        else:
            connections[node_name] = neighbors

        # Type & Floor (NEW)
        node_types[node_name] = data.get("type", "corridor")
        node_floors[node_name] = data.get("floor", 0)

    return True


load_map_data()


# --- 4. Helper Functions ---
def calc_hypotenuse(D1, D2):
    return math.sqrt(D1*D1 + D2*D2)

def calc_dist(n1, n2):
    if n1 not in node_coordinates or n2 not in node_coordinates:
        return float('inf')
    x1, y1 = node_coordinates[n1]
    x2, y2 = node_coordinates[n2]
    dx = x2 - x1                       
    dy = y2 - y1                       
    return math.sqrt(dx*dx + dy*dy)    

def pixels_to_m(dist_pixels):
    return dist_pixels * METERS_PER_PIXEL   

def calculate_time_cost(node_a, node_b, mode="normal"):
    dist_pixels = calc_dist(node_a, node_b)
    real_dist_m = pixels_to_m(dist_pixels)
    is_stairs = (node_types.get(node_a) == 'stairs' and node_types.get(node_b) == 'stairs')

    if is_stairs:
        if mode == "wheelchair":
            return float ('inf')
        if mode == "energy_saver":
            return 60 + (real_dist_m / Human_avg_Speed)
    
    if (node_types.get(node_a) == 'stairs' and node_types.get(node_b) == 'stairs') and (node_floors.get(node_a, 0) == 2 and node_floors.get(node_b, 0)==1) or (node_floors.get(node_a, 0) == 1 and node_floors.get(node_b, 0)==2):
        return 23
    if (node_types.get(node_a) == 'stairs' and node_types.get(node_b) == 'stairs') and (node_floors.get(node_a, 0) == 1 and node_floors.get(node_b, 0)==0) or (node_floors.get(node_a, 0) == 0 and node_floors.get(node_b, 0)==1):
        return 28 #asssumtion
    if (node_types.get(node_a) == 'stairs' and node_types.get(node_b) == 'stairs') and (node_floors.get(node_a, 0) == 2 and node_floors.get(node_b, 0)==0) or (node_floors.get(node_a, 0) == 0 and node_floors.get(node_b, 0)==2):
        return 51 #assumtion 
    
    if (node_types.get(node_a) == 'elevator' and node_types.get(node_b) == 'elevator') and (node_floors.get(node_a, 0) == 2 and node_floors.get(node_b, 0)==1) or (node_floors.get(node_a, 0) == 1 and node_floors.get(node_b, 0)==2):
        return 14 #assumption for elevator time between floors 
    if (node_types.get(node_a) == 'elevator' and node_types.get(node_b) == 'elevator') and (node_floors.get(node_a, 0) == 1 and node_floors.get(node_b, 0)==0) or (node_floors.get(node_a, 0) == 0 and node_floors.get(node_b, 0)==1):
        return 18 ################################################
    if (node_types.get(node_a) == 'elevator' and node_types.get(node_b) == 'elevator') and (node_floors.get(node_a, 0) == 2 and node_floors.get(node_b, 0)==0) or (node_floors.get(node_a, 0) == 0 and node_floors.get(node_b, 0)==2):
        return 32 ################################################
    return real_dist_m / Human_avg_Speed 

def calculate_heuristic(node, goal):
    dist_pixels = calc_dist(node, goal)
    real_dist_m = pixels_to_m(dist_pixels)  
    return real_dist_m / MAX_SPEED

def calculate_different_floors_heuristic(node, goal):
    dist_pixels = calc_dist(node, goal)
    real_dist_m = pixels_to_m(dist_pixels)  
    if (node_floors.get(node, 0) == 0 and node_floors.get(goal, 0)==1) or node_floors.get(node, 0) == 1 and node_floors.get(goal, 0)==0 :
        floor_diffrence_distance = 6.2 #meters
        return calc_hypotenuse(real_dist_m, floor_diffrence_distance)/ MAX_SPEED
    elif node_floors.get(node, 0) ==0 and node_floors.get(goal, 0)==2 or node_floors.get(node, 0) ==2 and node_floors.get(goal, 0)==0 :
        floor_diffrence_distance = 11.2 
        return calc_hypotenuse(real_dist_m, floor_diffrence_distance)/ MAX_SPEED
    elif node_floors.get(node, 0) ==1 and node_floors.get(goal, 0)==2 or node_floors.get(node, 0) ==2 and node_floors.get(goal, 0)==1 :
        floor_diffrence_distance = 5.0 
        return calc_hypotenuse(real_dist_m, floor_diffrence_distance)/ MAX_SPEED

# A* Algorithm (Cumulative Time + Distance)

def a_star(start, goal, mode ="normal"):
    if start not in node_coordinates or goal not in node_coordinates:
        print("Error: Invalid start or goal node names.")
        return None, 0, 0

    #            (node, path, g_time_seconds, g_distance_meters)
    open_list = [(start, [start], 0, 0)]
    closed = []

    while open_list:
        min_f = float('inf')
        best_index = 0

        # Select best node based on f = g_time + h_time
        for i in range(len(open_list)):
            node, path, g_time, g_dist = open_list[i]
            if node_floors.get(node, 0) != node_floors.get(goal, 0):
                h = calculate_different_floors_heuristic(node, goal)
            else:
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
                    step_meters = pixels_to_m(step_pixels)  
                    step_time = calculate_time_cost(current_node, neighbor, mode)

                    new_g_time = g_time + step_time
                    new_g_dist = g_dist + step_meters 

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


# Execution Block
if __name__ == "__main__":
    print("\n--- Select Navigation Mode ---")
    print("1. Energy Saver (Avoid Stairs)")
    print("2. Normal (Fastest Route)")
    print("3. Wheelchair (No Stairs)")
    
    choice = input("Enter choice (1, 2, or 3): ")
    mode = "normal" 
    if choice == "1":
        mode = "energy_saver"
    elif choice == "3":
        mode = "wheelchair"
    else :
        mode = "normal"
        
    print(f"\n🔹 Mode Active: {mode}")
    start_node = 'Auditorium-door1'
    goal_node = 'English-Dept'

    path, total_time, total_distance = a_star(start_node, goal_node, mode) 

    if path:
        print("\n✅ Path Found!")
        print(" -> ".join(path))
        print("-" * 30)
        print(f"⏱  Total Time:     {total_time:.2f} seconds")
        print(f"📏 Total Distance: {total_distance:.2f} m")  
        print("-" * 30)
    else:
        print("\n❌ Could not find a path.")
