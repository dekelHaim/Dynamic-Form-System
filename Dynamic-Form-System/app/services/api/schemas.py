from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class FormCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    schema_definition: Dict[str, Any]
    data: Optional[Dict[str, Any]] = None 
    user_details: Optional[Dict[str, Any]] = None  

class FormResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    schema_definition: Dict[str, Any]
    data: Optional[Dict[str, Any]] = None  
    user_details: Optional[Dict[str, Any]] = None 
    is_active: bool
    created_at: datetime # 

    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    form_schema_id: int
    data: Dict[str, Any]
    user_email: str

class SubmissionResponse(BaseModel):
    id: int
    form_schema_id: int
    form_name: str
    data: Dict[str, Any]
    user_email: str
    validation_status: str
    is_duplicate: bool
    created_at: datetime #

    class Config:
        from_attributes = True