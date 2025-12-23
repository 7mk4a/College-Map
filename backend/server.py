from flask import Flask, request, jsonify
from flask_cors import CORS
import college_map_core as map_logic
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Helper to ensure data is loaded
map_logic.load_map_data()

map_logic.time()
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    # Filter to return only meaningful destinations for start/end points
    # Include: rooms, departments, stairs, elevators
    # Exclude: corridors, waypoints (b_point, c_point, C_GF_XX, etc.)
    
    nodes = []
    for name, data in map_logic.node_coordinates.items():
        node_type = map_logic.node_types.get(name, "corridor")
        floor = map_logic.node_floors.get(name, 0)
        
        # Skip corridor nodes
        if node_type == "corridor":
            continue
            
        # Skip waypoint-style names (b_point, c_point, C_GF_05, etc.)
        name_lower = name.lower()
        if any(pattern in name_lower for pattern in ['_point', 'c_gf_', 'c_ff_', 'c_sf_', '_corridor']):
            continue
        
        nodes.append({
            "name": name,
            "x": data[0],
            "y": data[1],
            "type": node_type,
            "floor": floor
        })
    
    # Sort by name for easier dropdown navigation
    nodes.sort(key=lambda x: x["name"])
    return jsonify(nodes)

@app.route('/api/path', methods=['POST'])
def calculate_path():
    data = request.json
    start = data.get('start')
    end = data.get('end')
    mode = data.get('mode', 'normal')

    if not start or not end:
        return jsonify({"error": "Missing start or end node"}), 400

    path, total_time, total_distance = map_logic.a_star(start, end, mode)

    if not path:
        return jsonify({"error": "No path found"}), 404

    # Build response with full path details including coordinates for drawing
    path_details = []
    for node in path:
        coords = map_logic.node_coordinates.get(node)
        floor = map_logic.node_floors.get(node, 0)
        path_details.append({
            "name": node,
            "x": coords[0],
            "y": coords[1],
            "floor": floor
        })

    directions = map_logic.generate_directions(path)

    return jsonify({
        "path": path,
        "path_details": path_details,
        "total_time_seconds": total_time,
        "total_distance_meters": total_distance,
        "directions": directions
    })

@app.route('/api/schedule/<room_name>', methods=['GET'])
def check_schedule(room_name):
    # This logic is a bit print-heavy in the original script. 
    # We might need to parse the JSON directly here or adjust the helper.
    # The original check_room_status prints to stdout. We should probably just read the json here or refactor.
    # Let's read the json directly to avoid stdout capture mess.
    
    # Try to find schedule.json in here or parent dir
    here = os.path.dirname(__file__)
    schedule_file = os.path.join(here, "schedule.json")
    if not os.path.exists(schedule_file):
        schedule_file = os.path.join(here, "..", "schedule.json")

    if not os.path.exists(schedule_file):
        return jsonify({"status": "unknown", "message": "Schedule file missing"})

    import json
    
    current_hour, current_minute, today_str = map_logic.show_current_time()
    current_time_minutes = (current_hour * 60) + current_minute

    with open(schedule_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    schedule_data = data.get("schedule", []) if isinstance(data, dict) else data
    
    occupancy = {"status": "Available", "details": None}
    
    for course in schedule_data:
        room_in_json = str(course.get("room", ""))
        day_in_json = course.get("day", "")
        
        if room_name in room_in_json and day_in_json == today_str:
            start_str = course.get("start", "00:00")
            end_str = course.get("end", "00:00")
            
            try:
                start_h, start_m = map(int, start_str.split(":"))
                end_h, end_m = map(int, end_str.split(":"))
                lecture_start = (start_h * 60) + start_m
                lecture_end = (end_h * 60) + end_m
                
                if lecture_start <= current_time_minutes <= lecture_end:
                    occupancy = {
                        "status": "Occupied",
                        "details": {
                            "course": course.get("course"),
                            "instructor": course.get("instructor"),
                            "time": f"{start_str} - {end_str}",
                            "type": course.get("type", "Lecture")
                        }
                    }
                    break
            except ValueError:
                continue
                
    return jsonify(occupancy)
@app.route('/api/schedule/search', methods=['GET'])
def search_schedule():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    results = map_logic.search_schedule(query)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
