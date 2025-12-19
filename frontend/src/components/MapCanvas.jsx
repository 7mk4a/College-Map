import React, { useRef, useEffect, useState } from 'react';

const MapCanvas = ({ currentFloor, pathDetails, startNodeName, endNodeName }) => {
    const containerRef = useRef(null);
    const [scale, setScale] = useState(1);
    const [offset, setOffset] = useState({ x: 0, y: 0 });
    const [isDragging, setIsDragging] = useState(false);
    const [lastPos, setLastPos] = useState({ x: 0, y: 0 });

    // Reset view when floor changes
    useEffect(() => {
        // Optional: Reset zoom/pan on floor switch? 
        // Or keep context. Let's keep context for smoother feel, but maybe reset if off screen.
    }, [currentFloor]);

    const handleWheel = (e) => {
        e.preventDefault();
        const zoomSensitivity = 0.001;
        const newScale = Math.min(Math.max(0.5, scale - e.deltaY * zoomSensitivity), 4);

        // Zoom towards mouse pointer logic could be added here, 
        // but simple zoom is fine for now.
        setScale(newScale);
    };

    const handleMouseDown = (e) => {
        setIsDragging(true);
        setLastPos({ x: e.clientX, y: e.clientY });
    };

    const handleMouseMove = (e) => {
        if (!isDragging) return;
        const dx = e.clientX - lastPos.x;
        const dy = e.clientY - lastPos.y;
        setOffset((prev) => ({ x: prev.x + dx, y: prev.y + dy }));
        setLastPos({ x: e.clientX, y: e.clientY });
    };

    const handleMouseUp = () => {
        setIsDragging(false);
    };

    // Filter path for current floor
    // If path goes Floor 0 -> Floor 1 -> Floor 0, we should handle that segments.
    // We need to draw lines between consecutive points IF they are on the same floor.
    // If adjacent points are different floors, it's a transition (stairs/elevator).

    const renderPath = () => {
        if (!pathDetails || pathDetails.length < 2) return null;

        const segments = [];
        let currentSegment = [];

        for (let i = 0; i < pathDetails.length; i++) {
            const point = pathDetails[i];
            if (point.floor === currentFloor) {
                currentSegment.push(point);
            } else {
                if (currentSegment.length > 0) {
                    // If the NEXT point is on a different floor, we still want to indicate "exit" at the last point of this floor
                    // But looking at consecutive check:
                    // If i'm at floor 0, and next is floor 1. 
                    // The currentSegment has [ ..., elevator_floor_0 ].
                    // We draw up to elevator_floor_0.
                    segments.push([...currentSegment]);
                    currentSegment = [];
                }
            }
        }
        if (currentSegment.length > 0) segments.push(currentSegment);

        // Also need to handle "gap" where we might just be passing through a floor?
        // A* usually gives contiguous path. 
        // Wait, if node A (F0) -> node B (F1).
        // On F0 view: Draw line to Node A. 
        // on F1 view: Draw line from Node B.

        // Drawing Logic:
        return segments.map((seg, sIdx) => {
            if (seg.length < 2 && segments.length > 1) {
                // Single point on this floor? (e.g. just landing on stairs and going back?)
                // Draw a dot?
                return null;
            }

            const pathData = seg.map((p, i) => {
                return `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`;
            }).join(' ');

            return (
                <path
                    key={sIdx}
                    d={pathData}
                    fill="none"
                    stroke="#3B82F6"
                    strokeWidth="6"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="drop-shadow-md animate-draw"
                    style={{
                        strokeDasharray: 1000,
                        strokeDashoffset: 0,
                        animation: 'dash 3s linear forwards'
                    }}
                />
            );
        });
    };

    const mapImage = `/assets/floor_${currentFloor}.jpg`;

    return (
        <div
            ref={containerRef}
            className="w-full h-full bg-gray-100 overflow-hidden cursor-move relative"
            onWheel={handleWheel}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
        >
            <div
                style={{
                    transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale})`,
                    transformOrigin: '0 0',
                    transition: isDragging ? 'none' : 'transform 0.1s ease-out'
                }}
                className="relative inline-block"
            >
                <img
                    src={mapImage}
                    alt={`Floor ${currentFloor}`}
                    className="max-w-none pointer-events-none select-none shadow-2xl"
                    onError={(e) => { e.target.src = 'https://via.placeholder.com/800x600?text=Map+Image+Not+Found'; }}
                />

                {/* Nodes Overlay (Optional - currently hidden for clean look, just drawing path) */}

                {/* Path Overlay */}
                <svg className="absolute top-0 left-0 w-full h-full pointer-events-none">
                    {renderPath()}

                    {/* Start/End Markers */}
                    {pathDetails && pathDetails.length > 0 && (
                        <>
                            {/* Start Marker */}
                            {pathDetails[0].floor === currentFloor && (
                                <circle cx={pathDetails[0].x} cy={pathDetails[0].y} r="8" fill="#22c55e" stroke="white" strokeWidth="3" />
                            )}

                            {/* End Marker */}
                            {pathDetails[pathDetails.length - 1].floor === currentFloor && (
                                <circle cx={pathDetails[pathDetails.length - 1].x} cy={pathDetails[pathDetails.length - 1].y} r="8" fill="#ef4444" stroke="white" strokeWidth="3" />
                            )}
                        </>
                    )}
                </svg>
            </div>

            <div className="absolute bottom-4 right-4 bg-white/80 backdrop-blur rounded-lg p-2 text-xs text-gray-500 z-50">
                Scroll to Zoom • Drag to Pan
            </div>
        </div>
    );
};

export default MapCanvas;
