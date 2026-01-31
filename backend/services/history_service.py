"""
History service for storing and managing analysis history.

This service provides:
- SQLite database storage using SQLAlchemy
- 1-week retention policy with automatic cleanup
- Entry creation and retrieval functions
- Pydantic models for data validation
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field
from apscheduler.schedulers.background import BackgroundScheduler
from config import config
import json

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Database Models
class HistoryEntryDB(Base):
    """SQLAlchemy model for history entries."""
    __tablename__ = "history_entries"
    
    id = Column(String, primary_key=True, index=True)
    problem_slug = Column(String, index=True, nullable=False)
    problem_title = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    analysis_type = Column(String, nullable=False)
    result = Column(Text, nullable=False)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String, nullable=True, index=True)


# Pydantic Models
class HistoryEntry(BaseModel):
    """Pydantic model for history entry validation and serialization."""
    id: str
    problem_slug: str
    problem_title: str
    code: str
    language: str
    analysis_type: str
    result: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class HistoryCreateRequest(BaseModel):
    """Request model for creating a history entry."""
    problem_slug: str
    problem_title: str
    code: str
    language: str
    analysis_type: str
    result: Dict[str, Any]
    user_id: Optional[str] = None


class HistoryResponse(BaseModel):
    """Response model for history queries."""
    entries: List[HistoryEntry]
    total_count: int
    has_more: bool = False


# History Service
class HistoryService:
    """Service for managing analysis history."""
    
    def __init__(self):
        """Initialize the history service and create database tables."""
        Base.metadata.create_all(bind=engine)
        self.scheduler = BackgroundScheduler()
        self._setup_cleanup_job()
    
    def _setup_cleanup_job(self):
        """Set up automatic cleanup job for expired entries."""
        # Run cleanup daily at 2 AM
        self.scheduler.add_job(
            self.delete_expired_entries,
            'cron',
            hour=2,
            minute=0,
            id='cleanup_expired_entries'
        )
        self.scheduler.start()
    
    def _get_db(self) -> Session:
        """Get a database session."""
        return SessionLocal()
    
    def save_analysis(self, entry_data: HistoryCreateRequest) -> HistoryEntry:
        """
        Save an analysis entry to the database.
        
        Args:
            entry_data: History entry data to save
            
        Returns:
            Created HistoryEntry
        """
        db = self._get_db()
        try:
            # Generate unique ID
            entry_id = f"{entry_data.problem_slug}_{datetime.utcnow().timestamp()}"
            
            # Create database entry
            db_entry = HistoryEntryDB(
                id=entry_id,
                problem_slug=entry_data.problem_slug,
                problem_title=entry_data.problem_title,
                code=entry_data.code,
                language=entry_data.language,
                analysis_type=entry_data.analysis_type,
                result=json.dumps(entry_data.result),
                timestamp=datetime.utcnow(),
                user_id=entry_data.user_id
            )
            
            db.add(db_entry)
            db.commit()
            db.refresh(db_entry)
            
            # Convert to Pydantic model
            return self._db_to_pydantic(db_entry)
        finally:
            db.close()
    
    def get_history(
        self, 
        user_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> HistoryResponse:
        """
        Get analysis history entries.
        
        Args:
            user_id: Optional user ID to filter by
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            
        Returns:
            HistoryResponse with entries and metadata
        """
        db = self._get_db()
        try:
            # Build query
            query = db.query(HistoryEntryDB)
            
            if user_id:
                query = query.filter(HistoryEntryDB.user_id == user_id)
            
            # Get total count
            total_count = query.count()
            
            # Get entries with pagination, ordered by timestamp descending
            entries = query.order_by(HistoryEntryDB.timestamp.desc()).limit(limit).offset(offset).all()
            
            # Convert to Pydantic models
            pydantic_entries = [self._db_to_pydantic(entry) for entry in entries]
            
            return HistoryResponse(
                entries=pydantic_entries,
                total_count=total_count,
                has_more=(offset + len(entries)) < total_count
            )
        finally:
            db.close()
    
    def get_history_by_problem(
        self, 
        problem_slug: str,
        user_id: Optional[str] = None
    ) -> List[HistoryEntry]:
        """
        Get history entries for a specific problem.
        
        Args:
            problem_slug: Problem slug to filter by
            user_id: Optional user ID to filter by
            
        Returns:
            List of HistoryEntry objects for the problem
        """
        db = self._get_db()
        try:
            query = db.query(HistoryEntryDB).filter(
                HistoryEntryDB.problem_slug == problem_slug
            )
            
            if user_id:
                query = query.filter(HistoryEntryDB.user_id == user_id)
            
            entries = query.order_by(HistoryEntryDB.timestamp.desc()).all()
            
            return [self._db_to_pydantic(entry) for entry in entries]
        finally:
            db.close()
    
    def delete_entry(self, entry_id: str, user_id: Optional[str] = None) -> bool:
        """
        Delete a specific history entry.
        
        Args:
            entry_id: ID of the entry to delete
            user_id: Optional user ID for ownership validation
            
        Returns:
            True if deleted, False if not found
        """
        db = self._get_db()
        try:
            query = db.query(HistoryEntryDB).filter(HistoryEntryDB.id == entry_id)
            
            if user_id:
                query = query.filter(HistoryEntryDB.user_id == user_id)
            
            entry = query.first()
            
            if entry:
                db.delete(entry)
                db.commit()
                return True
            
            return False
        finally:
            db.close()
    
    def delete_expired_entries(self) -> int:
        """
        Delete entries older than the retention period.
        
        Returns:
            Number of entries deleted
        """
        db = self._get_db()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=config.HISTORY_RETENTION_DAYS)
            
            deleted_count = db.query(HistoryEntryDB).filter(
                HistoryEntryDB.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            
            return deleted_count
        finally:
            db.close()
    
    def _db_to_pydantic(self, db_entry: HistoryEntryDB) -> HistoryEntry:
        """
        Convert database model to Pydantic model.
        
        Args:
            db_entry: SQLAlchemy database entry
            
        Returns:
            Pydantic HistoryEntry
        """
        return HistoryEntry(
            id=db_entry.id,
            problem_slug=db_entry.problem_slug,
            problem_title=db_entry.problem_title,
            code=db_entry.code,
            language=db_entry.language,
            analysis_type=db_entry.analysis_type,
            result=json.loads(db_entry.result),
            timestamp=db_entry.timestamp,
            user_id=db_entry.user_id
        )
    
    def shutdown(self):
        """Shutdown the scheduler gracefully."""
        if self.scheduler.running:
            self.scheduler.shutdown()


# Global history service instance
history_service = HistoryService()
