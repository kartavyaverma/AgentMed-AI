#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

echo "Starting AgentMed AI Unified Service..."

# Start the FastAPI backend in the background on port 8000
echo "Starting FastAPI backend on port 8000..."
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait briefly for backend to spin up
sleep 3

# Start the Streamlit frontend in the foreground
# It binds to $PORT (defined by Render) and connects to the backend locally
echo "Starting Streamlit frontend on port ${PORT}..."
export BACKEND_BASE_URL="http://127.0.0.1:8000"
export PYTHONPATH="."
uv run streamlit run frontend/streamlit_app.py --server.port ${PORT} --server.address 0.0.0.0

# If Streamlit stops, kill the backend
kill $BACKEND_PID
