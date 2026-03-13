#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Meeting Intelligence Agent${NC}"
echo -e "${BLUE}     Full Stack Launcher${NC}"
echo -e "${BLUE}================================${NC}\n"

# Check Node.js
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

if command -v npm &> /dev/null; then
    echo -e "${GREEN}✅ Node.js/npm found${NC}"
else
    echo -e "${YELLOW}⚠️  Node.js/npm not found${NC}"
    echo -e "${YELLOW}Install from: https://nodejs.org/${NC}"
    echo -e "${YELLOW}Or: brew install node${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Function to start backend
start_backend() {
    echo -e "\n${BLUE}Starting Backend Server...${NC}"
    cd "$PROJECT_ROOT/backend"
    
    # Kill existing process on port 8000
    lsof -ti :8000 2>/dev/null | xargs kill -9 2>/dev/null || true
    sleep 1
    
    python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Function to start frontend
start_frontend() {
    echo -e "\n${BLUE}Starting Frontend Server...${NC}"
    cd "$PROJECT_ROOT/frontend"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing npm dependencies...${NC}"
        npm install || {
            echo -e "${RED}❌ Failed to install npm packages${NC}"
            exit 1
        }
    fi
    
    npm run dev
}

# Main logic
if [ "$1" == "backend" ]; then
    start_backend
elif [ "$1" == "frontend" ]; then
    start_frontend
elif [ "$1" == "both" ]; then
    echo -e "${YELLOW}Starting both servers...${NC}"
    echo -e "${YELLOW}⚠️  Open 2 terminal windows for this to work${NC}"
    echo -e "${YELLOW}Terminal 1: ./launch.sh backend${NC}"
    echo -e "${YELLOW}Terminal 2: ./launch.sh frontend${NC}"
    sleep 2
    
    # Try to start both in background
    start_backend &
    BACKEND_PID=$!
    sleep 3
    start_frontend &
    FRONTEND_PID=$!
    
    echo -e "\n${GREEN}================================${NC}"
    echo -e "${GREEN}✅ Both servers started!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo -e "Backend:  ${BLUE}http://localhost:8000${NC}"
    echo -e "Frontend: ${BLUE}http://localhost:5173${NC}"
    echo -e "\nPress Ctrl+C to stop both servers"
    
    wait
else
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  ./launch.sh backend     - Start backend only"
    echo -e "  ./launch.sh frontend    - Start frontend only"
    echo -e "  ./launch.sh both        - Start both (in background)"
    echo ""
    echo -e "${YELLOW}Quick Start (separate terminals):${NC}"
    echo -e "  Terminal 1: ${BLUE}cd backend && python3 -m uvicorn app.main:app --reload${NC}"
    echo -e "  Terminal 2: ${BLUE}cd frontend && npm install && npm run dev${NC}"
fi
