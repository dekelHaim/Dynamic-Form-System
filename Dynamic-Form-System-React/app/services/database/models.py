# models.py - SQLAlchemy ORM models for form submissions
from sqlalchemy import Column, Integer, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class FormSubmission(Base):

    __tablename__ = "form_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    form_data = Column(JSON, nullable=False)
    is_duplicate = Column(Boolean, default=False, index=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    
    def __repr__(self) -> str:
        return f"<FormSubmission(id={self.id}, is_duplicate={self.is_duplicate}, submitted_at={self.submitted_at})>"
