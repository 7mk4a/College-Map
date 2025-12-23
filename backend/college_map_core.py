import math
import json
import os
from datetime import datetime


# --- 0. Current Time Info ---
def time ():
    now = datetime.now()
    return {
        "now": now,
        "hour": now.hour,        # 0–23
        "minute": now.minute,
        "weekday": now.weekday()  # 0=Mon, 6=Sun
    }

# --- 1. Constants ---
METERS_PER_PIXEL = 67/857   # ≈ 0.0781797
Human_avg_Speed = .5486  #m/s
MAX_SPEED = 1.2  #m/s
BREAK_START = 13  # 1 PM
BREAK_END = 14    # 2 PM
ELEVATOR_DELAY_DURING_BREAK = 60  # seconds
Ground_First_Floor_ElevTime = 18  # seconds
Ground_Second_Floor_ElevTime = 25  # seconds
First_Second_Floor_ElevTime = 15  # seconds
Ground_First_Floor_StairsTime = 30  # seconds
Ground_Second_Floor_StairsTime = 55  # seconds
First_Second_Floor_StairsTime = 25  # seconds
Ground_First_floorDistance = 6.2  # meters
Ground_Second_floorDistance = 11.2  # meters
First_Second_floorDistance = 5.0  # meters


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
    is_elevator = (node_types.get(node_a) == 'elevator' and node_types.get(node_b) == 'elevator')
    node_a_floor = node_floors.get(node_a, 0)
    node_b_floor = node_floors.get(node_b, 0)
    current = time()
    current_hour = current["hour"]
    is_break = BREAK_START <= current_hour < BREAK_END
    
    if is_stairs:
        if mode == "wheelchair":
            return float ('inf')
        
        # In 'stairs' mode, we use standard stairs time without any penalty
        if (node_a_floor == 2 and node_b_floor==1) or (node_a_floor == 1 and node_b_floor==2):
            return First_Second_Floor_StairsTime
        if (node_a_floor == 1 and node_b_floor==0) or (node_a_floor == 0 and node_b_floor==1):
            return Ground_First_Floor_StairsTime
        if (node_a_floor == 2 and node_b_floor==0) or (node_a_floor == 0 and node_b_floor==2):
            return Ground_Second_Floor_StairsTime 
    
    if is_elevator:
        Elev_time = 0
        if is_break:
            Elev_time = ELEVATOR_DELAY_DURING_BREAK
        
        # In 'stairs' mode, we penalize the elevator to favor stairs
        if mode == "stairs":
            Elev_time += 120 # Added 2 min penalty to elevator in stairs mode

        if (node_a_floor == 0 and node_b_floor==1) or (node_a_floor == 1 and node_b_floor==0):
            return Ground_First_Floor_ElevTime + Elev_time
        if (node_a_floor == 1 and node_b_floor==2) or (node_a_floor == 2 and node_b_floor==1):
            return First_Second_Floor_ElevTime + Elev_time
        if (node_a_floor == 0 and node_b_floor==2) or (node_a_floor == 2 and node_b_floor==0):
            return Ground_Second_Floor_ElevTime + Elev_time
        
    return real_dist_m / Human_avg_Speed 

def calculate_heuristic(node, goal):
    dist_pixels = calc_dist(node, goal)
    real_dist_m = pixels_to_m(dist_pixels)  
    return real_dist_m / MAX_SPEED

def calculate_different_floors_heuristic(node, goal):
    dist_pixels = calc_dist(node, goal)
    real_dist_m = pixels_to_m(dist_pixels) 
    node_floor = node_floors.get(node, 0)
    goal_floor = node_floors.get(goal, 0)
  
    if (node_floor == 0 and goal_floor == 1) or (node_floor == 1 and goal_floor == 0): 
        return calc_hypotenuse(real_dist_m, Ground_First_floorDistance)/ MAX_SPEED
    elif node_floor ==0 and goal_floor==2 or node_floor ==2 and goal_floor==0 :
        return calc_hypotenuse(real_dist_m, Ground_Second_floorDistance)/ MAX_SPEED
    elif node_floor ==1 and goal_floor==2 or node_floor ==2 and goal_floor==1 :
        return calc_hypotenuse(real_dist_m, First_Second_floorDistance)/ MAX_SPEED

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


def show_Current_Time():

    Hours = {
        0: "12 AM", 1: "1 AM", 2: "2 AM", 3: "3 AM", 4: "4 AM", 5: "5 AM",
        6: "6 AM", 7: "7 AM", 8: "8 AM", 9: "9 AM", 10: "10 AM", 11: "11 AM",
        12: "12 PM", 13: "1 PM", 14: "2 PM", 15: "3 PM", 16: "4 PM", 17: "5 PM",
        18: "6 PM", 19: "7 PM", 20: "8 PM", 21: "9 PM", 22: "10 PM", 23: "11 PM"
    }

    Days = {
        0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
        4: "Friday", 5: "Saturday", 6: "Sunday"
    }
    # Fetch fresh values
    current = time()
    current_hour = current["hour"]
    current_weekday = current["weekday"]

    return Days.get(current_weekday, "Unknown"), Hours.get(current_hour, "Unknown"), current["minute"]

def check_room_status(target_room):
    if node_types.get(target_room) == "department" or node_types.get(target_room) == "corridor":
        return
    else:
        
        # Get readable day/hour and numeric time values
        day_name, hour_label = show_Current_Time()
        current = time()
        current_hour = current["hour"]
        current_minute = current["minute"]

        # Try to find schedule.json in here or parent dir
        here = os.path.dirname(__file__)
        file_name = os.path.join(here, "schedule.json")
        if not os.path.exists(file_name):
            file_name = os.path.join(here, "..", "schedule.json")

        if not os.path.exists(file_name):
            print(f"❌ Error: schedule.json file not found.")
            return

        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and "schedule" in data:
            schedule_data = data["schedule"]
        else:
            schedule_data = data

        print(f"\n🔎 Checking schedule for room: {target_room} on {(day_name, hour_label)}...")
        
        found_lecture = False
        
        current_time_minutes = (current_hour * 60) + current_minute

        for course in schedule_data:
            room_in_json = str(course.get("room", "")) 
            day_in_json = course.get("day", "")
            
            
            if target_room in room_in_json and day_in_json == day_name:
                
                start_str = course.get("start", "00:00")
                end_str = course.get("end", "00:00")

                try:
                    start_h, start_m = map(int, start_str.split(":"))
                    end_h, end_m = map(int, end_str.split(":"))
                    
                    lecture_start_minutes = (start_h * 60) + start_m
                    lecture_end_minutes = (end_h * 60) + end_m

                    if lecture_start_minutes <= current_time_minutes <= lecture_end_minutes:
                        print(f"\n Room is BUSY (Occupied)!")
                        print(f"   Course:     {course.get('course', 'Unknown')}")
                        print(f"   Instructor: {course.get('instructor', 'Unknown')}")
                        print(f"   Group:      {course.get('group', 'Unknown')}")
                        print(f"   Time:       {start_str} - {end_str}")
                        found_lecture = True
                        break 
                except ValueError:
                    continue 

        if not found_lecture:
            print(f"\n Room {target_room} is currently EMPTY. You can use it.")

def search_schedule(query):
    # Try to find schedule.json in here or parent dir
    here = os.path.dirname(__file__)
    file_name = os.path.join(here, "schedule.json")
    if not os.path.exists(file_name):
        file_name = os.path.join(here, "..", "schedule.json")

    if not os.path.exists(file_name):
        return []

    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)

    schedule_data = data.get("schedule", []) if isinstance(data, dict) else data
    
    results = []
    query = query.lower()
    for entry in schedule_data:
        course = entry.get("course", "").lower()
        instructor = entry.get("instructor", "")
        instructor_str = instructor.lower() if instructor else ""
        room = entry.get("room", "").lower()
        
        if query in course or query in instructor_str or query in room:
            results.append(entry)
            
    return results

def generate_directions(path):
    if not path or len(path) < 2:
        return []


    def describe_node(node):
        node_type = node_types.get(node, "corridor")
        if node_type in ["room", "department"]:
            return node
        return "the corridor"


    def get_nearby_place(node):
        for n in connections.get(node, []):
            if node_types.get(n) in ["room", "department"]:
                return n
        return None

    directions = [f"Start at {describe_node(path[0])}"]
    previous_angle = None

    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i + 1]

        x1, y1 = node_coordinates[current]
        x2, y2 = node_coordinates[next_node]

        floor_current = node_floors.get(current, 0)
        floor_next = node_floors.get(next_node, 0)

        type_current = node_types.get(current, "corridor")
        type_next = node_types.get(next_node, "corridor")

        target = describe_node(next_node)
        place_ahead = get_nearby_place(next_node)


        if floor_current != floor_next:
            if type_current == "stairs" or type_next == "stairs":
                direction = "UP" if floor_next > floor_current else "DOWN"
                directions.append(f"Take the stairs {direction} to floor {floor_next}")
            elif type_current == "elevator" or type_next == "elevator":
                directions.append(f"Take the elevator to floor {floor_next}")


            if type_next not in ["stairs", "elevator"]:
                directions.append(f"Exit and head towards {target}")

            previous_angle = None
            continue


        dx = x2 - x1
        dy = y2 - y1
        current_angle = math.degrees(math.atan2(dy, dx))
        if current_angle < 0:
            current_angle += 360


        if previous_angle is None:
            if place_ahead:
                directions.append(f"Walk forward (you'll pass near {place_ahead})")
            else:
                directions.append("Walk forward along the corridor")

            previous_angle = current_angle
            continue


        turn = current_angle - previous_angle
        while turn > 180:
            turn -= 360
        while turn < -180:
            turn += 360

        if -45 <= turn <= 45:
            move = "Continue straight"
        elif 45 < turn <= 135:
            move = "Turn RIGHT"
        elif -135 <= turn < -45:
            move = "Turn LEFT"
        else:
            move = "Turn AROUND"

        if place_ahead:
            directions.append(f"{move} towards {place_ahead}")
        else:
            directions.append(f"{move} along the corridor")

        previous_angle = current_angle


    final = path[-1]
    final_type = node_types.get(final, "corridor")

    if final_type == "room":
        directions.append(f"🎯 You have arrived at room {final}")
    elif final_type == "department":
        directions.append(f"🎯 You have arrived at {final}")
    else:
        directions.append("🎯 You have arrived at your destination")

    return directions
if __name__ == "__main__":
    print("\n--- Select Navigation Mode ---")
    print("1. Stairs (Favor Stairs)")
    print("2. Normal (Fastest Route)")
    print("3. Wheelchair (Elevator Only)")
    
    choice = input("Enter choice (1, 2, or 3): ")
    mode = "normal" 
    if choice == "1":
        mode = "stairs"
    elif choice == "3":
        mode = "wheelchair"
    else :
        mode = "normal"
        
    print(f"\n🔹 Mode Active: {mode}")
    start_node = 'VIP'
    goal_node = '318A'

    check_room_status(goal_node)

    path, total_time, total_distance = a_star(start_node, goal_node, mode) 
    if path:
        print("\n✅ Path Found!")
        print(" -> ".join(path))
        print("-" * 30)
        print(f"⏱  Total Time:     {total_time:.2f} seconds")
        print(f"📏 Total Distance: {total_distance:.2f} m")  
        print("-" * 30)

        directions = generate_directions(path)
        print("Directions:")
        for i, d in enumerate(directions, 1):
            print(f"{i}. {d}")

    else:
        print("\n❌ Could not find a path.")
