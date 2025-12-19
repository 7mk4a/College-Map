@echo off
echo Starting UniMap Backend...
start "UniMap Backend" cmd /k "python backend/server.py"

echo Starting UniMap Frontend...
cd frontend
start "UniMap Frontend" cmd /k "npm run dev"

echo.
echo Application starting...
echo Backend will be at: http://127.0.0.1:5000
echo Frontend will be at: http://localhost:5173
echo.
pause
