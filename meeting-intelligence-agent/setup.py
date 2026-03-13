#!/usr/bin/env python3
"""
Quick setup script for Meeting Intelligence Agent
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run shell command"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error running command: {command}")
        sys.exit(1)

def main():
    print("🚀 Setting up Meeting Intelligence Agent...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required")
        sys.exit(1)
    
    print("✅ Python version OK")
    
    # Check if Docker is installed
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker found")
        use_docker = input("Use Docker for setup? (y/n): ").lower() == 'y'
    except:
        print("⚠️  Docker not found, using manual setup")
        use_docker = False
    
    if use_docker:
        print("\n📦 Starting services with Docker...")
        run_command("docker-compose up -d")
        print("\n✅ All services started!")
        print("\nAccess the application:")
        print("  Frontend: http://localhost:3002")
        print("  Backend:  http://localhost:8001")
        print("  API Docs: http://localhost:8001/api/v1/docs")
        
    else:
        print("\n📦 Manual setup...")
        
        # Backend setup
        print("\n1️⃣  Setting up backend...")
        backend_dir = Path("backend")
        
        if not (backend_dir / ".env").exists():
            print("Creating .env file...")
            run_command("cp .env.example .env", cwd=backend_dir)
            print("⚠️  Please edit backend/.env with your API keys!")
        
        print("Creating virtual environment...")
        run_command("python -m venv venv", cwd=backend_dir)
        
        print("Installing backend dependencies...")
        if sys.platform == "win32":
            venv_activate = "venv\\Scripts\\activate"
            pip_cmd = "venv\\Scripts\\pip"
        else:
            venv_activate = "source venv/bin/activate"
            pip_cmd = "venv/bin/pip"
        
        run_command(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir)
        
        print("\n2️⃣  Setting up frontend...")
        frontend_dir = Path("frontend")
        
        # Check if npm is installed
        try:
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
            print("Installing frontend dependencies...")
            run_command("npm install", cwd=frontend_dir)
        except:
            print("❌ npm not found. Please install Node.js")
            sys.exit(1)
        
        print("\n✅ Setup complete!")
        print("\nNext steps:")
        print("1. Configure backend/.env with your API keys")
        print("2. Start PostgreSQL and Redis")
        print("3. Run migrations: cd backend && alembic upgrade head")
        print("4. Start backend: cd backend && uvicorn app.main:app --reload")
        print("5. Start frontend: cd frontend && npm run dev")
    
    print("\n📚 Documentation:")
    print("  README.md            - Overview")
    print("  INSTALLATION.md      - Detailed setup")
    print("  API_DOCUMENTATION.md - API reference")
    print("  CONTRIBUTING.md      - Contributing guide")

if __name__ == "__main__":
    main()
