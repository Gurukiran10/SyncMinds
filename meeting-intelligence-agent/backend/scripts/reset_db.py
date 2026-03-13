"""Script to reset database - removes all data except admin user"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.meeting import Meeting
from app.models.action_item import ActionItem
from app.models.mention import Mention

def reset_database():
    """Reset database to clean state"""
    with SessionLocal() as db:
        # Delete all data except admin user
        db.query(Mention).delete()
        db.query(ActionItem).delete()
        db.query(Meeting).delete()
        
        db.commit()
        print("✅ Database reset complete!")
        print("   - All meetings, action items, and mentions deleted")
        print("   - Admin user preserved (username: admin, password: admin123)")

if __name__ == "__main__":
    response = input("⚠️  This will delete ALL meetings and action items. Continue? (yes/no): ")
    if response.lower() == 'yes':
        reset_database()
    else:
        print("Reset cancelled.")
