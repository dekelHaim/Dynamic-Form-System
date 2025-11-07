from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict, Any, List

class FormSubmissionValidator(BaseModel):
    """Validate form submission"""
    form_schema_id: int
    data: Dict[str, Any]
    user_email: Optional[str] = None

class FormSchemaValidator(BaseModel):
    """Validate form schema"""
    name: str
    description: Optional[str] = None
    schema_definition: Dict[str, Any]
    data: Optional[Dict[str, Any]] = None
    user_details: Optional[Dict[str, Any]] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v) < 3:
            raise ValueError('Name must be at least 3 characters')
        return v

    @field_validator('schema_definition')
    @classmethod
    def validate_schema(cls, v):
        if not v:
            raise ValueError('Schema cannot be empty')
        return v

def validate_form_data(data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate form data against schema - SERVER SIDE"""
    errors = []
    
    for field_name, field_config in schema.items():
        value = data.get(field_name)
        field_type = field_config.get("type")
        required = field_config.get("required", False)
        

        if required and (value is None or value == ""):
            errors.append(f"{field_name} is required")
            continue
        

        if not value:
            continue
        

        value_str = str(value).strip()
        

        if field_type == "string" or field_type == "text":
            min_len = field_config.get("minLength", 0)
            max_len = field_config.get("maxLength", float("inf"))
            if len(value_str) < min_len:
                errors.append(f"{field_name} must be at least {min_len} characters")
            if len(value_str) > max_len:
                errors.append(f"{field_name} must be no more than {max_len} characters")
        

        elif field_type == "email":

            if "@" not in value_str or "." not in value_str.split("@")[-1]:
                errors.append(f"{field_name} must be a valid email address")
        

        elif field_type == "password":
            min_len = field_config.get("minLength", 6)
            if len(value_str) < min_len:
                errors.append(f"{field_name} must be at least {min_len} characters")
        

        elif field_type == "date":

            try:
                from datetime import datetime
                datetime.strptime(value_str, "%Y-%m-%d")
            except:
                errors.append(f"{field_name} must be in YYYY-MM-DD format")
        

        elif field_type == "number":
            try:
                num = float(value_str)
                min_val = field_config.get("min", float("-inf"))
                max_val = field_config.get("max", float("inf"))
                if num < min_val:
                    errors.append(f"{field_name} must be at least {min_val}")
                if num > max_val:
                    errors.append(f"{field_name} must be at most {max_val}")
            except:
                errors.append(f"{field_name} must be a number")
        

        elif field_type == "dropdown":
            options = field_config.get("options", [])
            if value_str not in options:
                errors.append(f"{field_name} must be one of: {', '.join(map(str, options))}")
    
    return len(errors) == 0, errors

def check_duplicate_email(email: str, form_id: int, existing_submissions: List) -> bool:
    """Check if email already exists for this form (SERVER SIDE)"""
    if not email:
        return False
    
    for submission in existing_submissions:
        # Check if same email exists
        if submission.user_email and submission.user_email.lower() == email.lower():
            return True
    
    return False

def is_duplicate(new_data: Dict[str, Any], existing_submissions: List) -> bool:
    """Check if submission data is duplicate - EXACT MATCH"""
    for submission in existing_submissions:
        if new_data == submission.data:
            return True
    
    return False