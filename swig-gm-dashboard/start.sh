#!/bin/bash

# Swig GM Dashboard Startup Script
# This script starts both the backend API and frontend development server

set -e

echo "======================================"
echo "   Swig GM Dashboard - Startup"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check for .env file
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    echo -e "${YELLOW}Warning: backend/.env file not found!${NC}"
    echo "Creating from template..."
    if [ -f "$SCRIPT_DIR/backend/.env.example" ]; then
        cp "$SCRIPT_DIR/backend/.env.example" "$SCRIPT_DIR/backend/.env"
        echo -e "${YELLOW}Please edit backend/.env and add your ANTHROPIC_API_KEY${NC}"
        echo ""
    fi
fi

# Check if Python venv exists for backend
if [ ! -d "$SCRIPT_DIR/backend/venv" ]; then
    echo "Creating Python virtual environment..."
    cd "$SCRIPT_DIR/backend"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd "$SCRIPT_DIR"
else
    source "$SCRIPT_DIR/backend/venv/bin/activate"
fi

# Check if node_modules exists for frontend
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$SCRIPT_DIR/frontend"
    npm install
    cd "$SCRIPT_DIR"
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${GREEN}Starting backend API...${NC}"
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 3

# Start frontend
echo -e "${GREEN}Starting frontend dev server...${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "======================================"
echo -e "${GREEN}   Services Running!${NC}"
echo "======================================"
echo ""
echo -e "  Dashboard:  ${GREEN}http://localhost:5173${NC}"
echo -e "  API Docs:   ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait
