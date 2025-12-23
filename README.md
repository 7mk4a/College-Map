# UniMap - University Indoor Navigation System

A Google Maps-like indoor navigation application for university buildings with multi-floor support, A* pathfinding algorithm, and real-time room occupancy checking.

## Features

- 🗺️ **Interactive Map**: Visual floor plans for Ground, First, and Second floors
- 🧭 **Smart Navigation**: A* algorithm for optimal pathfinding
- 📷 **QR Code Scanner**: Scan QR codes to automatically set your starting location
- ♿ **Accessibility Modes**:
  - Normal Mode (Fastest route)
  - Stairs Mode (Favors stairs over elevators)
  - Wheelchair Mode (Elevator-only, no stairs)
- 📍 **Step-by-Step Directions**: Turn-by-turn navigation instructions
- 📅 **Room Occupancy**: Real-time room availability based on class schedules
- 🎨 **Modern UI**: Clean, responsive design with smooth animations

## Prerequisites

Before you begin, ensure you have the following installed:

### 1. Python (3.8 or higher)
**Download:** https://www.python.org/downloads/

**Verify installation:**
```bash
python --version
```

### 2. Node.js (18.0 or higher) and npm
**Download:** https://nodejs.org/

**Verify installation:**
```bash
node --version
npm --version
```

### 3. Git (Optional, for cloning)
**Download:** https://git-scm.com/downloads

---

## Installation Steps

### Step 1: Clone or Download the Project

**Option A: Clone with Git**
```bash
git clone <your-repository-url>
cd College-Map
```

**Option B: Download ZIP**
- Download the project as a ZIP file
- Extract it to your desired location
- Open terminal/command prompt in the extracted folder

### Step 2: Install Python Dependencies

Open a terminal in the project root directory and run:

```bash
pip install flask flask-cors
```

**What this does:** Installs the backend API framework (Flask) and enables cross-origin requests (flask-cors).

### Step 3: Install Frontend Dependencies

Navigate to the frontend folder and install packages:

```bash
cd frontend
npm install
cd ..
```

**What this does:** Installs all required JavaScript packages including:
- **React 19**: UI framework
- **Vite**: Build tool and dev server  
- **Tailwind CSS 4**: Styling framework
- **Lucide React**: Icon library
- **html5-qrcode**: QR code scanning library for camera-based location detection

---

## Running the Application

### Option 1: Quick Start (Windows)

Double-click the `start_app.bat` file in the project root.

This will automatically:
- Start the Flask backend server on `http://127.0.0.1:5000`
- Start the React frontend on `http://localhost:5173`

### Option 2: Manual Start

**Terminal 1 - Start Backend:**
```bash
python backend/server.py
```
You should see:
```
* Running on http://127.0.0.1:5000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```
You should see:
```
➜  Local:   http://localhost:5173/
```

**Access the Application:**
Open your browser and go to: **http://localhost:5173**

---

## Project Structure

```
College-Map/
├── backend/
│   ├── server.py              # Flask API server
│   ├── college_map_core.py    # A* pathfinding logic
│   ├── college_map_data.json  # Building map data (nodes, edges)
│   └── schedule.json          # Room schedule data
├── frontend/
│   ├── public/
│   │   └── assets/            # Floor plan images
│   │       ├── floor_0.jpg    # Ground floor map
│   │       ├── floor_1.jpg    # First floor map
│   │       └── floor_2.jpg    # Second floor map
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── MapCanvas.jsx       # Map display with zoom/pan
│   │   │   ├── FloorSwitcher.jsx   # Floor selection tabs
│   │   │   └── NavigationControls.jsx  # Route input/output
│   │   ├── QRCodeScanner.jsx  # QR code scanner modal
│   │   ├── App.jsx            # Main application
│   │   ├── api.js             # Backend API calls
│   │   └── index.css          # Tailwind CSS styles
│   ├── package.json           # Node dependencies
│   └── vite.config.js         # Vite configuration
├── start_app.bat              # Windows startup script
└── README.md                  # This file
```

---

## Usage Guide

### 1. Select Start Location

**Option A: Manual Selection**
- Click the "Choose start location..." dropdown
- Select your current position (e.g., "VIP", "Library-door1")

**Option B: QR Code Scanning** 📷
- Click the QR code button (blue button next to start location dropdown)
- Grant camera permissions when prompted
- Point your camera at a QR code containing a location identifier
- The scanned location will automatically populate as your start point
- The camera will stop automatically after a successful scan

### 2. Select Destination
- Click the "Choose destination..." dropdown
- Select where you want to go

### 3. Choose Navigation Mode
- **Fastest**: Shortest time route (may include stairs)
- **Stairs**: Favors stairs when possible
- **Elevator**: Only uses elevators (no stairs at all)

### 4. Navigate
- Click the "Navigate" button
- View the route on the map (blue path)
- Follow the step-by-step directions in the sidebar

### 5. Floor Switching
- Use the floor selector buttons at the bottom of the map
- The path will update to show the route on the selected floor

---

## Customization

### Adding/Updating Floor Maps

1. Navigate to `frontend/public/assets/`
2. Replace the images:
   - `floor_0.jpg` → Ground floor
   - `floor_1.jpg` → First floor
   - `floor_2.jpg` → Second floor
3. Refresh the browser

### Updating Map Data

Edit `backend/college_map_data.json` to:
- Add new rooms/nodes
- Modify coordinates
- Update connections between nodes

### Updating Schedule

Edit `backend/schedule.json` to update room occupancy schedules.

---

## Troubleshooting

### Frontend won't start / Tailwind CSS errors

**Problem:** `Cannot find module '@tailwindcss/postcss'`

**Solution:**
```bash
cd frontend
npm install @tailwindcss/postcss
npm run dev
```

### Backend won't start

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
pip install flask flask-cors
```

### Port already in use

**Problem:** `Error: Port 5000 is already in use`

**Solution:**
- Close other applications using port 5000
- Or modify the port in `backend/server.py` (line: `app.run(debug=True, port=5000)`)

### Images not loading

**Problem:** Map images appear broken

**Solution:**
- Ensure images exist in `frontend/public/assets/`
- Image names must be exactly: `floor_0.jpg`, `floor_1.jpg`, `floor_2.jpg`
- Clear browser cache (Ctrl+Shift+R)

---

## Technologies Used

### Backend
- **Python 3.x**: Core programming language
- **Flask**: Web framework for API
- **A* Algorithm**: Pathfinding algorithm

### Frontend
- **React 19**: UI framework
- **Vite**: Build tool and dev server
- **Tailwind CSS 4**: Styling framework
- **Lucide React**: Icon library
- **html5-qrcode**: QR code scanning library

---

## API Endpoints

### GET `/api/nodes`
Returns all map nodes with coordinates, types, and floor information.

**Response:**
```json
[
  {
    "name": "VIP",
    "x": 420,
    "y": 536,
    "type": "department",
    "floor": 0
  }
]
```

### POST `/api/path`
Calculates the shortest path between two nodes.

**Request:**
```json
{
  "start": "VIP",
  "end": "318A",
  "mode": "normal"
}
```

**Response:**
```json
{
  "path": ["VIP", "Point7", "..."],
  "path_details": [...],
  "total_time_seconds": 125.5,
  "total_distance_meters": 85.3,
  "directions": ["Start at VIP", "Go FORWARD", "..."]
}
```

### GET `/api/schedule/<room_name>`
Checks if a room is currently occupied.

**Response:**
```json
{
  "status": "Occupied",
  "details": {
    "course": "Data Structures",
    "instructor": "Dr. Smith",
    "time": "10:00 - 11:30"
  }
}
```

---

## Contributing

Feel free to fork this project and submit pull requests for improvements!

## License

This project is open source and available for educational purposes.

---

## Authors

Developed as a university project for indoor navigation.

## Support

For issues or questions, please open an issue on the GitHub repository.

---

**Happy Navigating! 🎯**