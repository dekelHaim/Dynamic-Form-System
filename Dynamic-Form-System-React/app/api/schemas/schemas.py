from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, Optional, List
from datetime import datetime


class FieldDefinition(BaseModel):
    """Schema definition for a single form field."""
    type: str = Field(..., description="Field type: text, email, password, date, number, dropdown")
    required: Optional[bool] = Field(default=False, description="Whether field is required")
    minLength: Optional[int] = Field(default=None, description="Minimum string length")
    maxLength: Optional[int] = Field(default=None, description="Maximum string length")
    min: Optional[float] = Field(default=None, description="Minimum numeric value")
    max: Optional[float] = Field(default=None, description="Maximum numeric value")
    options: Optional[List[str]] = Field(default=None, description="Available options for dropdown")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid_types = {'text', 'email', 'password', 'date', 'number', 'dropdown', 'string'}
        if v not in valid_types:
            raise ValueError(f"Field type must be one of: {', '.join(valid_types)}")
        return v


class FormDataSubmission(BaseModel):
    data: Dict[str, Any] = Field(..., description="Form data matching the schema")


class FormSubmissionResponse(BaseModel):

    id: int = Field(..., description="Submission ID")
    form_data: Dict[str, Any] = Field(..., description="Submitted form data")
    is_duplicate: bool = Field(..., description="Whether this is a duplicate submission")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    
    class Config:
        from_attributes = True


class FormSubmissionsListResponse(BaseModel):
    """Response schema for list of submissions."""
    submissions: List[FormSubmissionResponse] = Field(..., description="List of submissions")
    total: int = Field(..., description="Total number of submissions")


class ErrorResponse(BaseModel):

    error: str = Field(..., description="Error message")
    details: Optional[List[str]] = Field(default=None, description="Detailed error messages")
