#!/bin/bash

echo "Starting DMS Data Monitoring System..."
echo "========================================"

# Start backend
echo "[1/2] Starting backend service..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "[2/2] Starting frontend service..."
cd ../frontend
bun run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
