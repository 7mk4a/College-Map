import React from 'react';
import { Search, MapPin, Navigation, Info } from 'lucide-react';

const NavigationControls = ({
    nodes,
    startNode,
    setStartNode,
    endNode,
    setEndNode,
    mode,
    setMode,
    onGo,
    routeStats,
    directions,
    occupancy,
    reset
}) => {
    return (
        <div className="absolute top-4 left-4 w-96 bg-white/95 backdrop-blur-md shadow-2xl rounded-2xl p-6 z-[1000] max-h-[90vh] overflow-y-auto border border-white/20">
            <h1 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <Navigation className="w-6 h-6 mr-2 text-blue-600" />
                UniMap
            </h1>

            <div className="space-y-4">
                {/* Start Node */}
                <div className="relative">
                    <MapPin className="absolute left-3 top-3 w-5 h-5 text-green-500" />
                    <select
                        value={startNode}
                        onChange={(e) => setStartNode(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all appearance-none cursor-pointer text-gray-700 font-medium"
                    >
                        <option value="">Choose start location...</option>
                        {nodes.map((n) => (
                            <option key={n.name} value={n.name}>
                                {n.name} ({n.floor === 0 ? 'G' : n.floor})
                            </option>
                        ))}
                    </select>
                </div>

                {/* End Node */}
                <div className="relative">
                    <MapPin className="absolute left-3 top-3 w-5 h-5 text-red-500" />
                    <select
                        value={endNode}
                        onChange={(e) => setEndNode(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all appearance-none cursor-pointer text-gray-700 font-medium"
                    >
                        <option value="">Choose destination...</option>
                        {nodes.map((n) => (
                            <option key={n.name} value={n.name}>
                                {n.name} ({n.floor === 0 ? 'G' : n.floor})
                            </option>
                        ))}
                    </select>
                </div>

                {/* Mode Selection */}
                <div className="grid grid-cols-3 gap-2 bg-gray-100 p-1 rounded-xl">
                    {[
                        { id: 'normal', label: 'Fastest' },
                        { id: 'energy_saver', label: 'No Stairs' },
                        { id: 'wheelchair', label: 'Elevator' },
                    ].map((m) => (
                        <button
                            key={m.id}
                            onClick={() => setMode(m.id)}
                            className={`py-2 text-xs font-bold rounded-lg transition-all ${mode === m.id
                                    ? 'bg-white text-blue-600 shadow-sm'
                                    : 'text-gray-500 hover:text-gray-700'
                                }`}
                        >
                            {m.label}
                        </button>
                    ))}
                </div>

                <button
                    onClick={onGo}
                    disabled={!startNode || !endNode}
                    className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg hover:shadow-blue-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed transform active:scale-95"
                >
                    Navigate
                </button>

                {routeStats && (
                    <button
                        onClick={reset}
                        className="w-full py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-xl text-sm transition-all"
                    >
                        Clear Route
                    </button>
                )}
            </div>

            {/* Route Stats & Directions */}
            {routeStats && (
                <div className="mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className='flex justify-between items-center bg-blue-50 p-4 rounded-xl border border-blue-100 mb-6'>
                        <div>
                            <p className="text-gray-500 text-xs uppercase tracking-wider font-semibold">Time</p>
                            <p className="text-2xl font-bold text-blue-700">{(routeStats.total_time_seconds / 60).toFixed(1)} <span className='text-sm font-normal text-blue-500'>min</span></p>
                        </div>
                        <div>
                            <p className="text-gray-500 text-xs uppercase tracking-wider font-semibold text-right">Distance</p>
                            <p className="text-2xl font-bold text-gray-700 text-right">{Math.round(routeStats.total_distance_meters)} <span className='text-sm font-normal text-gray-400'>m</span></p>
                        </div>
                    </div>

                    {occupancy && occupancy.status === "Occupied" && (
                        <div className="mb-6 p-4 bg-red-50 border border-red-100 rounded-xl">
                            <h3 className="text-red-800 font-bold flex items-center mb-2">
                                <Info className="w-4 h-4 mr-2" /> Room Occupied
                            </h3>
                            <div className="text-sm text-red-700 space-y-1">
                                <p><span className="font-semibold">Course:</span> {occupancy.details?.course}</p>
                                <p><span className="font-semibold">By:</span> {occupancy.details?.instructor}</p>
                                <p><span className="font-semibold">Until:</span> {occupancy.details?.time?.split('-')[1]}</p>
                            </div>
                        </div>
                    )}
                    {occupancy && occupancy.status !== "Occupied" && occupancy.status !== "unknown" && (
                        <div className="mb-6 p-3 bg-green-50 border border-green-100 rounded-xl flex items-center text-green-800">
                            <Info className="w-4 h-4 mr-2" /> Room Available
                        </div>
                    )}

                    <div className="space-y-3">
                        <h3 className="font-bold text-gray-800 border-b pb-2">Directions</h3>
                        <div className="max-h-64 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
                            {directions.map((step, idx) => (
                                <div key={idx} className="flex items-start group">
                                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-100 text-gray-500 flex items-center justify-center text-xs font-bold mr-3 group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
                                        {idx + 1}
                                    </span>
                                    <p className="text-sm text-gray-600 leading-snug pt-0.5">{step}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default NavigationControls;
