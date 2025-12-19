import React, { useState, useEffect } from 'react';
import MapCanvas from './components/MapCanvas';
import NavigationControls from './components/NavigationControls';
import FloorSwitcher from './components/FloorSwitcher';
import { fetchNodes, fetchPath, fetchRoomSchedule } from './api';

function App() {
  const [nodes, setNodes] = useState([]);
  const [currentFloor, setCurrentFloor] = useState(0); // 0: Ground, 1: First, 2: Second
  const [startNode, setStartNode] = useState('');
  const [endNode, setEndNode] = useState('');
  const [mode, setMode] = useState('normal');
  const [routeStats, setRouteStats] = useState(null);
  const [pathDetails, setPathDetails] = useState([]);
  const [directions, setDirections] = useState([]);
  const [occupancy, setOccupancy] = useState(null);

  useEffect(() => {
    fetchNodes().then(setNodes).catch(console.error);
  }, []);

  const handleGo = async () => {
    if (!startNode || !endNode) return;
    try {
      const data = await fetchPath(startNode, endNode, mode);
      setRouteStats({
        total_time_seconds: data.total_time_seconds,
        total_distance_meters: data.total_distance_meters
      });
      setPathDetails(data.path_details);
      setDirections(data.directions);

      // Check occupancy if destination is a room
      // Basic check: if endNode type is not corridor/stairs/elevator (approximated by name for now or check data)
      // The API returns type in node list, we can look it up.
      const targetNode = nodes.find(n => n.name === endNode);
      if (targetNode && ['room', 'department'].includes(targetNode.type)) {
        try {
          const occ = await fetchRoomSchedule(endNode);
          setOccupancy(occ);
        } catch (e) { console.error(e); setOccupancy(null); }
      } else {
        setOccupancy(null);
      }

      // Auto-switch to start floor
      const startN = nodes.find(n => n.name === startNode);
      if (startN) setCurrentFloor(startN.floor);

    } catch (error) {
      console.error("Path calculation failed:", error);
      alert("Could not calculate path. Please try again.");
    }
  };

  const handleReset = () => {
    setRouteStats(null);
    setPathDetails([]);
    setDirections([]);
    setOccupancy(null);
    setStartNode('');
    setEndNode('');
  };

  return (
    <div className="relative w-screen h-screen bg-gray-50 flex overflow-hidden font-sans text-gray-900">
      <NavigationControls
        nodes={nodes}
        startNode={startNode}
        setStartNode={setStartNode}
        endNode={endNode}
        setEndNode={setEndNode}
        mode={mode}
        setMode={setMode}
        onGo={handleGo}
        routeStats={routeStats}
        directions={directions}
        occupancy={occupancy}
        reset={handleReset}
      />

      <main className="flex-1 relative">
        <MapCanvas
          currentFloor={currentFloor}
          pathDetails={pathDetails}
        />

        <FloorSwitcher
          currentFloor={currentFloor}
          setFloor={setCurrentFloor}
        />
      </main>
    </div>
  );
}

export default App;
