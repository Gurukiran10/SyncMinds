"""
Script to create admin user
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def create_admin():
    """Create admin user"""
    with SessionLocal() as db:
        # Check if admin exists
        from sqlalchemy import select
        result = db.execute(
            select(User).where(User.username == "admin")
        )
        
        if result.scalar_one_or_none():
            print("Admin user already exists!")
            return
        
        # Create admin
        admin = User(
            email="admin@meetingintel.ai",
            username="admin",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_superuser=True,
            is_active=True,
            is_verified=True,
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("⚠️  Please change the password after first login")


if __name__ == "__main__":
    create_admin()
