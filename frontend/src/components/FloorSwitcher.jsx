import React from 'react';

const FloorSwitcher = ({ currentFloor, setFloor }) => {
    const floors = [
        { id: 0, label: 'Ground Floor' },
        { id: 1, label: 'First Floor' },
        { id: 2, label: 'Second Floor' },
    ];

    return (
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 bg-white/90 backdrop-blur-sm shadow-xl rounded-full p-2 flex space-x-2 z-[1000]">
            {floors.map((f) => (
                <button
                    key={f.id}
                    onClick={() => setFloor(f.id)}
                    className={`px-6 py-2 rounded-full font-medium transition-all duration-300 ${currentFloor === f.id
                            ? 'bg-blue-600 text-white shadow-md transform scale-105'
                            : 'text-gray-600 hover:bg-gray-100 hover:text-blue-500'
                        }`}
                >
                    {f.label}
                </button>
            ))}
        </div>
    );
};

export default FloorSwitcher;
