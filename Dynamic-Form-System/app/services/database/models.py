from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey, Boolean
from datetime import datetime
from app.services.database.database import Base

class FormSchema(Base):
    """Form schema model"""
    __tablename__ = "forms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    schema_definition = Column(JSON, nullable=False)
    

    data = Column(JSON, nullable=True, default={})
    user_details = Column(JSON, nullable=True, default={})  
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<FormSchema(id={self.id}, name={self.name})>"


class Submission(Base):
    """Submission model"""
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    form_schema_id = Column(Integer, ForeignKey("forms.id", ondelete="CASCADE"), nullable=False)
    form_name = Column(String(255), index=True, nullable=False)
    data = Column(JSON, nullable=False)
    user_email = Column(String(255), nullable=True, index=True)
    validation_status = Column(String(50), default="valid")
    is_duplicate = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Submission(id={self.id}, form_id={self.form_schema_id})>"