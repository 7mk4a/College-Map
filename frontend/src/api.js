const API_URL = 'http://127.0.0.1:5000/api';

export const fetchNodes = async () => {
    const response = await fetch(`${API_URL}/nodes`);
    if (!response.ok) throw new Error('Failed to fetch nodes');
    return response.json();
};

export const fetchPath = async (start, end, mode) => {
    const response = await fetch(`${API_URL}/path`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start, end, mode }),
    });
    if (!response.ok) throw new Error('Failed to fetch path');
    return response.json();
};

export const fetchRoomSchedule = async (roomName) => {
    const response = await fetch(`${API_URL}/schedule/${roomName}`);
    if (!response.ok) throw new Error('Failed to fetch schedule');
    return response.json();
};
