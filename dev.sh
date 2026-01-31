#!/bin/bash

# Development script to run both frontend and backend concurrently

echo "Starting LeetCode Analysis Website development servers..."

# Function to cleanup background processes on exit
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Start backend
echo "Starting FastAPI backend on http://localhost:8000"
cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting Vite frontend on http://localhost:5173"
cd frontend && npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait
