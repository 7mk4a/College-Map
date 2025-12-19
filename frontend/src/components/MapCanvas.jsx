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
                    segments.push([...currentSegment]);
                    currentSegment = [];
                }
            }
        }
        if (currentSegment.length > 0) segments.push(currentSegment);

        // Calculate path length for accurate animation timing
        const calculatePathLength = (seg) => {
            let length = 0;
            for (let i = 0; i < seg.length - 1; i++) {
                const dx = seg[i + 1].x - seg[i].x;
                const dy = seg[i + 1].y - seg[i].y;
                length += Math.sqrt(dx * dx + dy * dy);
            }
            return length;
        };

        // Drawing Logic:
        return segments.map((seg, sIdx) => {
            if (seg.length < 2 && segments.length > 1) {
                return null;
            }

            const pathData = seg.map((p, i) => {
                return `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`;
            }).join(' ');

            const pathLength = calculatePathLength(seg);
            const uniqueId = `gradient-${currentFloor}-${sIdx}`;

            return (
                <g key={sIdx}>
                    {/* Define animated gradient */}
                    <defs>
                        <linearGradient id={uniqueId} x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#3B82F6" stopOpacity="1">
                                <animate attributeName="stop-color"
                                    values="#3B82F6;#8B5CF6;#EC4899;#3B82F6"
                                    dur="3s"
                                    repeatCount="indefinite" />
                            </stop>
                            <stop offset="50%" stopColor="#8B5CF6" stopOpacity="1">
                                <animate attributeName="stop-color"
                                    values="#8B5CF6;#EC4899;#3B82F6;#8B5CF6"
                                    dur="3s"
                                    repeatCount="indefinite" />
                            </stop>
                            <stop offset="100%" stopColor="#EC4899" stopOpacity="1">
                                <animate attributeName="stop-color"
                                    values="#EC4899;#3B82F6;#8B5CF6;#EC4899"
                                    dur="3s"
                                    repeatCount="indefinite" />
                            </stop>
                        </linearGradient>

                        {/* Glow filter */}
                        <filter id={`glow-${sIdx}`} x="-50%" y="-50%" width="200%" height="200%">
                            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
                            <feMerge>
                                <feMergeNode in="coloredBlur" />
                                <feMergeNode in="SourceGraphic" />
                            </feMerge>
                        </filter>
                    </defs>

                    {/* Outer glow path */}
                    <path
                        d={pathData}
                        fill="none"
                        stroke={`url(#${uniqueId})`}
                        strokeWidth="12"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        opacity="0.4"
                        filter={`url(#glow-${sIdx})`}
                        style={{
                            '--path-length': pathLength,
                            strokeDasharray: pathLength,
                            strokeDashoffset: pathLength,
                            animation: `drawPath 5s ease-in-out infinite`
                        }}
                    />

                    {/* Main path */}
                    <path
                        d={pathData}
                        fill="none"
                        stroke={`url(#${uniqueId})`}
                        strokeWidth="6"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        style={{
                            '--path-length': pathLength,
                            strokeDasharray: pathLength,
                            strokeDashoffset: pathLength,
                            animation: `drawPath 5s ease-in-out infinite`
                        }}
                    />
                </g>
            );
        });
    };

    const mapImage = `/assets/floor_${currentFloor}.jpeg`;

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
                    width="1280"
                    height="960"
                    className="max-w-none pointer-events-none select-none shadow-2xl"
                    onError={(e) => { e.target.src = 'https://via.placeholder.com/1280x960?text=Map+Image+Not+Found'; }}
                />

                {/* Nodes Overlay (Optional - currently hidden for clean look, just drawing path) */}

                {/* Path Overlay - Must match exact image dimensions for coordinate alignment */}
                <svg
                    className="absolute top-0 left-0 pointer-events-none"
                    width="1280"
                    height="960"
                    viewBox="0 0 1280 960"
                >
                    {renderPath()}

                    {/* Start/End Markers */}
                    {pathDetails && pathDetails.length > 0 && (
                        <>
                            {/* Start Marker */}
                            {pathDetails[0].floor === currentFloor && (
                                <g>
                                    {/* Pulsing ring */}
                                    <circle
                                        cx={pathDetails[0].x}
                                        cy={pathDetails[0].y}
                                        r="12"
                                        fill="none"
                                        stroke="#22c55e"
                                        strokeWidth="2"
                                        opacity="0.6"
                                    >
                                        <animate attributeName="r" values="12;20;12" dur="2s" repeatCount="indefinite" />
                                        <animate attributeName="opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite" />
                                    </circle>
                                    {/* Solid marker */}
                                    <circle
                                        cx={pathDetails[0].x}
                                        cy={pathDetails[0].y}
                                        r="8"
                                        fill="#22c55e"
                                        stroke="white"
                                        strokeWidth="3"
                                    />
                                </g>
                            )}

                            {/* End Marker */}
                            {pathDetails[pathDetails.length - 1].floor === currentFloor && (
                                <g>
                                    {/* Pulsing ring */}
                                    <circle
                                        cx={pathDetails[pathDetails.length - 1].x}
                                        cy={pathDetails[pathDetails.length - 1].y}
                                        r="12"
                                        fill="none"
                                        stroke="#ef4444"
                                        strokeWidth="2"
                                        opacity="0.6"
                                    >
                                        <animate attributeName="r" values="12;20;12" dur="2s" repeatCount="indefinite" />
                                        <animate attributeName="opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite" />
                                    </circle>
                                    {/* Solid marker */}
                                    <circle
                                        cx={pathDetails[pathDetails.length - 1].x}
                                        cy={pathDetails[pathDetails.length - 1].y}
                                        r="8"
                                        fill="#ef4444"
                                        stroke="white"
                                        strokeWidth="3"
                                    />
                                </g>
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
