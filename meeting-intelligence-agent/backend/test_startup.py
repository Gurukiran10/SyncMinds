#!/usr/bin/env python3
"""Quick application startup test"""
import sys
import os

sys.path.insert(0, os.getcwd())

try:
    print("Testing Application Startup...")
    print()
    
    # Test imports
    print("[1/3] Testing imports...")
    from fastapi import FastAPI
    from app.core.config import settings
    print(f"    ✓ Config loaded: {settings.APP_NAME}")
    
    print("[2/3] Testing database...")
    from app.core.database import engine, Base
    print("    ✓ Database initialized")
    
    print("[3/3] Creating application...")
    from app.main import app
    print("    ✓ Application created")
    print()
    print("✅ Success! Application is ready to run!")
    print()
    print("Start the server with:")
    print("  python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
