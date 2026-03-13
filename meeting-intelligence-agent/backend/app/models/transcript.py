"""
Transcript Model
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base
from app.models.types import GUID


class Transcript(Base):
    """Meeting transcript model"""
    __tablename__ = "transcripts"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    meeting_id = Column(GUID(), ForeignKey("meetings.id"), nullable=False, index=True)
    
    # Segment Info
    segment_number = Column(Integer, nullable=False)
    speaker_id = Column(String(100))  # Diarization speaker ID
    speaker_name = Column(String(255))
    user_id = Column(GUID(), ForeignKey("users.id"))  # Matched user
    
    # Content
    text = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    
    # Timing
    start_time = Column(Float, nullable=False)  # Seconds from meeting start
    end_time = Column(Float, nullable=False)
    duration = Column(Float)
    
    # Confidence
    confidence = Column(Float)  # 0 to 1
    
    # Analysis
    sentiment = Column(String(20))  # positive, negative, neutral
    sentiment_score = Column(Float)  # -1 to 1
    contains_question = Column(Boolean, default=False)
    contains_action_item = Column(Boolean, default=False)
    contains_decision = Column(Boolean, default=False)
    
    # Embeddings for semantic search
    embedding_vector = Column(JSON)  # Stored as JSON, can use pgvector extension
    
    # Metadata
    transcript_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="transcripts")
    mentions = relationship("Mention", back_populates="transcript")


class TranscriptWord(Base):
    """Word-level transcript for precise timestamps"""
    __tablename__ = "transcript_words"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(GUID(), ForeignKey("transcripts.id"), nullable=False, index=True)
    
    word = Column(String(255), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    confidence = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
