import math
import json
import os
from datetime import datetime


# --- 0. Current Time Info ---
now = datetime.now()
current_hour = now.hour        # 0–23
current_minute = now.minute
current_weekday = now.weekday()  # 0=Mon, 6=Sun


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
    is_break = BREAK_START <= current_hour < BREAK_END
    
    if is_stairs:
        if mode == "wheelchair":
            return float ('inf')
        if mode == "energy_saver":
            return 60 + (real_dist_m / Human_avg_Speed)

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
    ## print(f"🕒 Current Time: {Hours.get(current_hour, 'Unknown')} on {Days.get(current_weekday, 'Unknown')}")
    
    return Days.get(current_weekday, "Unknown")


# 🟢 (تعديل) الدالة دي لازم تكون بره show_Current_Time
def check_room_status(target_room):
    # 1. عرض الوقت وتحديد اليوم
    today_name_str = show_Current_Time() 

    # 2. تحميل الملف
    file_name = "schedule.json" # تأكد أن اسم الملف صحيح
    if not os.path.exists(file_name):
        print(f"❌ Error: {file_name} file not found.")
        return

    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ⚠️ (تعديل هام 1) الدخول إلى القائمة داخل المفتاح "schedule"
    # لو الملف مفيهوش مفتاح schedule، نستخدم البيانات زي ما هي
    if isinstance(data, dict) and "schedule" in data:
        schedule_data = data["schedule"]
    else:
        schedule_data = data

    print(f"\n🔎 Checking schedule for room: {target_room} on {today_name_str}...")
    
    found_lecture = False
    
    # حساب الوقت الحالي بالدقائق
    current_time_minutes = (current_hour * 60) + current_minute

    for course in schedule_data:
        # 3. التأكد من البيانات
        room_in_json = str(course.get("room", "")) # تحويل الرقم لنص لتجنب المشاكل
        day_in_json = course.get("day", "")
        
        # المقارنة: هل الغرفة واليوم متطابقين؟
        if target_room in room_in_json and day_in_json == today_name_str:
            
            # ⚠️ (تعديل هام 2) استخدام مفاتيح الجيسون الجديد (start, end)
            start_str = course.get("start", "00:00")
            end_str = course.get("end", "00:00")

            try:
                start_h, start_m = map(int, start_str.split(":"))
                end_h, end_m = map(int, end_str.split(":"))
                
                lecture_start_minutes = (start_h * 60) + start_m
                lecture_end_minutes = (end_h * 60) + end_m

                # هل الوقت الحالي جوه وقت المحاضرة؟
                if lecture_start_minutes <= current_time_minutes <= lecture_end_minutes:
                    print(f"\n Room is BUSY (Occupied)!")
                    # ⚠️ (تعديل هام 3) استخدام الاسم الجديد (course) بدل (course_name)
                    print(f"   Course:     {course.get('course', 'Unknown')}")
                    print(f"   Instructor: {course.get('instructor', 'Unknown')}")
                    print(f"   Group:      {course.get('group', 'Unknown')}")
                    print(f"   Time:       {start_str} - {end_str}")
                    found_lecture = True
                    break 
            except ValueError:
                continue # لو صيغة الوقت غلط تخطى المحاضرة دي

    if not found_lecture:
        print(f"\n Room {target_room} is currently EMPTY. You can use it.")

import math
def generate_directions(path):
    if not path or len(path) < 2:
        return []

    directions = [f"Start at {path[0]}"]
    previous_angle = None

    for i in range(len(path) - 1):
        current = path[i]
        next_node = path[i + 1]

        x1, y1 = node_coordinates[current]
        x2, y2 = node_coordinates[next_node]

        floor_current = node_floors.get(current, 0)
        floor_next = node_floors.get(next_node, 0)

        node_type_current = node_types.get(current, "corridor")
        node_type_next = node_types.get(next_node, "corridor")

        neighbor_nodes = connections.get(next_node, [])
        if node_type_next in ["room", "department", "elevator", "stairs"]:
            next_place = next_node
        else:
            next_place = "corridor"

        # floor changes
        if floor_current != floor_next:
            if node_type_current == "stairs" or node_type_next == "stairs":
                if floor_next > floor_current:
                    directions.append(f"Take stairs UP to floor {floor_next}")
                else:
                    directions.append(f"Take stairs DOWN to floor {floor_next}")
            elif node_type_current == "elevator" or node_type_next == "elevator":
                directions.append(f"Take elevator to floor {floor_next}")

            if neighbor_nodes:
                directions.append(f"Go FORWARD until you see {next_place}")
            else:
                directions.append("Go FORWARD")

            previous_angle = None
            continue

        # Calculate angle to next point
        dx = x2 - x1
        dy = y2 - y1
        current_angle = math.atan2(dy, dx) * 180 / math.pi
        if current_angle < 0:
            current_angle += 360

        # First move on a new floor
        if previous_angle is None:
            if neighbor_nodes:
                directions.append(f"Go FORWARD until you see {next_place}")
            else:
                directions.append("Go FORWARD")
            previous_angle = current_angle
            continue

        turn_angle = current_angle - previous_angle
        while turn_angle > 180:
            turn_angle -= 360
        while turn_angle < -180:
            turn_angle += 360

        if -45 <= turn_angle <= 45:
            direction_text = "Go FORWARD"
        elif 45 < turn_angle <= 135:
            direction_text = "Turn RIGHT"
        elif turn_angle > 135 or turn_angle < -135:
            direction_text = "TURN AROUND"
        else:
            direction_text = "Turn LEFT"

        if neighbor_nodes and next_place != "corridor":
            direction_text += f" at the corridor near {next_place}"


        directions.append(direction_text)
        previous_angle = current_angle

    directions.append(f"You have arrived at {path[-1]}")
    return directions

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
    start_node = 'Admission'
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
