"""
User Model
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base
from app.models.types import GUID


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    avatar_url = Column(String(500))
    timezone = Column(String(50), default="UTC")
    role = Column(String(50), default="user")  # user, admin, manager
    department = Column(String(100))
    job_title = Column(String(100))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Preferences
    preferences = Column(JSON, default={})
    notification_settings = Column(JSON, default={
        "email_enabled": True,
        "slack_enabled": True,
        "real_time_mentions": True,
        "daily_digest": True,
        "action_reminders": True,
    })
    
    # Integrations
    integrations = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    meetings = relationship("Meeting", back_populates="organizer", foreign_keys="Meeting.organizer_id")
    action_items = relationship("ActionItem", back_populates="owner", foreign_keys="ActionItem.owner_id")
    mentions = relationship("Mention", back_populates="user")
