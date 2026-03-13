#!/usr/bin/env python3
"""
Meeting Intelligence Agent - Application Startup Script
Handles environment setup, database initialization, and server launch
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from dotenv import load_dotenv

# Project paths
PROJECT_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_DIR / "backend"

def print_header(text):
    """Print colored header"""
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'
    print(f"\n{BLUE}{text}{NC}")

def print_success(text):
    """Print success message"""
    GREEN = '\033[0;32m'
    NC = '\033[0m'
    print(f"{GREEN}✓ {text}{NC}")

def print_info(text):
    """Print info message"""
    YELLOW = '\033[1;33m'
    NC = '\033[0m'
    print(f"{YELLOW}ℹ️  {text}{NC}")

def print_error(text):
    """Print error message"""
    RED = '\033[0;31m'
    NC = '\033[0m'
    print(f"{RED}❌ {text}{NC}")

def check_python():
    """Check Python version"""
    print_header("1. Checking Python installation...")
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 9):
        print_error(f"Python 3.9+ required, but {sys.version} found")
        return False
    print_success(f"Python {sys.version.split()[0]} found")
    return True

def check_dependencies():
    """Check and install required packages"""
    print_header("2. Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'python-dotenv',
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} installed")
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print_info(f"Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-q'
            ] + missing_packages)
            print_success("Dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print_error("Failed to install dependencies")
            return False
    
    print_success("All dependencies satisfied")
    return True

def setup_environment():
    """Setup environment variables"""
    print_header("3. Setting up environment...")
    
    env_file = BACKEND_DIR / ".env"
    
    if not env_file.exists():
        print_info("Creating .env file...")
        env_template = """# Application Settings
APP_NAME=Meeting Intelligence Agent
ENVIRONMENT=development
DEBUG=True

# Security (Change these in production!)
SECRET_KEY=dev-secret-key-change-in-production-minimum-32-characters
JWT_SECRET_KEY=dev-jwt-key-change-in-production-minimum-32-characters

# Database
DATABASE_URL=sqlite:///./app.db

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6380/0
CELERY_RESULT_BACKEND=redis://localhost:6380/1
REDIS_URL=redis://localhost:6380/0

# Optional: Add API keys when ready
# OPENAI_API_KEY=sk-...
# SLACK_BOT_TOKEN=xoxb-...

# Demo credentials
ADMIN_USER_EMAIL=admin@meetingintel.ai
ADMIN_USER_PASSWORD=admin123
DEMO_USER_EMAIL=demo@meetingintel.ai
DEMO_USER_PASSWORD=demo123
"""
        with open(env_file, 'w') as f:
            f.write(env_template)
        print_success(".env file created")
    else:
        print_success(".env file exists")
    
    # Load environment
    load_dotenv(env_file)
    return True

def setup_database():
    """Initialize database"""
    print_header("4. Setting up database...")
    
    # Create uploads directory
    uploads_dir = BACKEND_DIR / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    print_success("Upload directory ready")
    
    # Database will be created automatically by SQLAlchemy
    db_file = BACKEND_DIR / "app.db"
    if db_file.exists():
        print_success("Database already initialized")
    else:
        print_info("Database will be created on first startup")
    
    return True

def start_server():
    """Start the FastAPI server"""
    print_header("5. Starting application server...")
    
    print("\n" + "="*60)
    print("🚀 Meeting Intelligence Agent Started")
    print("="*60)
    print("\n📍 Access Points:")
    print("   • Frontend: http://localhost:3002")
    print("   • API: http://localhost:8001")
    print("   • API Docs: http://localhost:8001/docs")
    print("   • Alternative Docs: http://localhost:8001/redoc")
    print("\n👤 Default Credentials:")
    print("   • Admin: admin@meetingintel.ai / admin123")
    print("   • Demo: demo@meetingintel.ai / demo123")
    print("\n💡 Tips:")
    print("   • Press Ctrl+C to stop the server")
    print("   • Reload auto-enabled for code changes")
    print("   • Check http://localhost:8001/docs for API exploration")
    print("\n" + "="*60 + "\n")
    
    # Change to backend directory
    os.chdir(str(BACKEND_DIR))
    
    # Start server with uvicorn
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--reload',
            '--host', '0.0.0.0',
            '--port', '8001'
        ], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print_error(f"Server failed to start: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("\n" + "="*60)
    print("Meeting Intelligence Agent - Local Setup")
    print("="*60)
    
    # Run setup steps
    if not check_python():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    if not setup_environment():
        sys.exit(1)
    
    if not setup_database():
        sys.exit(1)
    
    # Start server
    if not start_server():
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutdown initiated by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
