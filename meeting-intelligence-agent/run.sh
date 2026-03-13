#!/bin/bash

# Meeting Intelligence Agent - Quick Launch Script
# This script sets up and runs the application locally

set -e  # Exit on error

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "🚀 Meeting Intelligence Agent - Local Launch"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Found $PYTHON_VERSION${NC}"

echo -e "\n${BLUE}2. Checking FastAPI installation...${NC}"
if python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${GREEN}✓ FastAPI is installed${NC}"
else
    echo "⚠️  Installing FastAPI and dependencies..."
    python3 -m pip install -q fastapi uvicorn sqlalchemy pydantic python-dotenv
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

echo -e "\n${BLUE}3. Setting up environment...${NC}"
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "⚠️  Creating .env file from template..."
    if [ -f "$BACKEND_DIR/.env.example" ]; then
        cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
        echo -e "${GREEN}✓ .env file created${NC}"
    else
        echo "⚠️  .env.example not found, creating minimal .env..."
        cat > "$BACKEND_DIR/.env" << 'EOF'
SECRET_KEY=dev-key-change-in-production-minimum-32-char
JWT_SECRET_KEY=jwt-dev-key-change-in-production-32-char
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
DEBUG=True
EOF
        echo -e "${GREEN}✓ .env file created with defaults${NC}"
    fi
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo -e "\n${BLUE}4. Initializing database...${NC}"
cd "$BACKEND_DIR"
python3 << 'PYTHON_SCRIPT'
import os
from pathlib import Path

# Create uploads directory
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Create SQLite database directory
db_path = Path("app.db")
if not db_path.exists():
    # Database will be created on first connection
    print("✓ Database will be initialized on startup")
else:
    print("✓ Database already exists")

# Check if migrations are needed
migrations_dir = Path("alembic/versions")
if migrations_dir.exists() and len(list(migrations_dir.glob("*.py"))) > 0:
    print("✓ Database migrations found")
else:
    print("ℹ️  No migrations yet - creating fresh database on startup")
PYTHON_SCRIPT
echo -e "${GREEN}✓ Database setup complete${NC}"

echo -e "\n${BLUE}5. Starting application...${NC}"
echo -e "${YELLOW}📍 Application will run on: http://localhost:8000${NC}"
echo -e "${YELLOW}📍 API Docs: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}📍 ReDoc: http://localhost:8000/redoc${NC}"
echo ""
echo -e "${YELLOW}Default credentials:${NC}"
echo "  Admin: admin@meetingintel.ai / admin123"
echo "  Demo: demo@meetingintel.ai / demo123"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo "=============================================="
echo ""

# Run the application
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
