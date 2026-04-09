import React, { useState } from 'react';
import { Search, MapPin, Navigation, Info, QrCode, Clock } from 'lucide-react';
import QRCodeScanner from '../QRCodeScanner';
import { searchSchedule } from '../api';

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
    const [showScanner, setShowScanner] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [showSearchResults, setShowSearchResults] = useState(false);

    const handleSearchInput = async (val) => {
        setSearchQuery(val);
        if (val.length > 1) {
            setIsSearching(true);
            setShowSearchResults(true);
            try {
                const results = await searchSchedule(val);
                setSearchResults(results);
            } catch (e) {
                console.error(e);
            } finally {
                setIsSearching(false);
            }
        } else {
            setSearchResults([]);
            setShowSearchResults(false);
        }
    };

    const selectSearchResult = (result) => {
        setEndNode(result.room);
        setSearchQuery(result.course);
        setShowSearchResults(false);
    };

    return (
        <div className="absolute top-4 left-4 w-96 bg-white/95 backdrop-blur-md shadow-2xl rounded-2xl p-6 z-[1000] max-h-[90vh] overflow-y-auto border border-white/20">
            <h1 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <Navigation className="w-6 h-6 mr-2 text-blue-600" />
                UniMap
            </h1>

            <div className="space-y-4">
                {/* Lecture Search */}
                <div className="relative">
                    <div className="relative">
                        <Search className="absolute left-3 top-3 w-5 h-5 text-blue-500" />
                        <input
                            type="text"
                            placeholder="Search lectures, instructors, or rooms..."
                            value={searchQuery}
                            onChange={(e) => handleSearchInput(e.target.value)}
                            onFocus={() => searchQuery && setShowSearchResults(true)}
                            className="w-full pl-10 pr-4 py-3 bg-blue-50/50 border border-blue-100 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all placeholder:text-gray-400 font-medium"
                        />
                        {isSearching && (
                            <div className="absolute right-3 top-3.5">
                                <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
                            </div>
                        )}
                    </div>

                    {showSearchResults && searchResults.length > 0 && (
                        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-2xl border border-gray-100 overflow-hidden z-[1001] max-h-60 overflow-y-auto custom-scrollbar">
                            {searchResults.map((res, i) => (
                                <button
                                    key={i}
                                    onClick={() => selectSearchResult(res)}
                                    className="w-full text-left p-3 hover:bg-blue-50 border-b border-gray-50 last:border-0 transition-colors"
                                >
                                    <p className="font-bold text-gray-800 text-sm">{res.course}</p>
                                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                                        <span className="flex items-center gap-1">
                                            <MapPin className="w-3 h-3 text-red-400" /> {res.room}
                                        </span>
                                        <span className="flex items-center gap-1">
                                            <Clock className="w-3 h-3 text-blue-400" /> {res.day}, {res.start}-{res.end}
                                        </span>
                                    </div>
                                    <p className="text-[10px] text-gray-400 mt-1 uppercase tracking-wider font-semibold">{res.instructor || 'Staff'}</p>
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-4 py-2">
                    <div className="h-px flex-1 bg-gray-100"></div>
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Or Navigate Directly</span>
                    <div className="h-px flex-1 bg-gray-100"></div>
                </div>
                {/* Start Node */}
                <div className="space-y-2">
                    <div className="flex gap-2">
                        <div className="relative flex-1">
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
                        <button
                            onClick={() => setShowScanner(true)}
                            className="px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-xl shadow-lg hover:shadow-blue-500/30 transition-all transform active:scale-95 flex items-center gap-2 font-semibold"
                            title="Scan QR Code"
                        >
                            <QrCode className="w-5 h-5" />
                        </button>
                    </div>
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
                        { id: 'stairs', label: 'Stairs' },
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
                        onClick={() => {
                            reset();
                            setSearchQuery('');
                            setSearchResults([]);
                        }}
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

            {/* QR Scanner Modal */}
            {showScanner && (
                <QRCodeScanner
                    setStartNode={setStartNode}
                    onClose={() => setShowScanner(false)}
                />
            )}
        </div>
    );
};

export default NavigationControls;
