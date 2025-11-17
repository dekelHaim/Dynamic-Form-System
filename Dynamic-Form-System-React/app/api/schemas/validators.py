from pydantic import  ValidationError
from typing import Dict, Any, List, Optional
from datetime import datetime
import re


class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class FormValidator:

    # Allowed values for specific fields
    ALLOWED_GENDERS = {"male", "female", "other"}
    ALLOWED_GENDER_VALUES = ["male", "female", "other"]
    
    # Default constraints
    NAME_MIN_LENGTH = 2
    NAME_MAX_LENGTH = 50
    AGE_MIN = 18
    AGE_MAX = 120
    PASSWORD_MIN_LENGTH = 6
    
    @staticmethod
    def validate_empty_data(data: Optional[Dict[str, Any]]) -> None:
        if not data:
            raise ValidationError("form_data", "Form data cannot be empty")
    
    @staticmethod
    def validate_email_format(email: str) -> None:
        if not isinstance(email, str):
            raise ValidationError("email", "Email must be a string")
        
        if not email.strip():
            raise ValidationError("email", "Email cannot be empty")
        
        # Simple email validation pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("email", "Invalid email format")
    
    @staticmethod
    def validate_name(name: Optional[str]) -> None:
        if name is None:
            return  # Optional field
        
        if not isinstance(name, str):
            raise ValidationError("name", "Name must be a string")
        
        name_stripped = name.strip()
        if not name_stripped:
            raise ValidationError("name", "Name cannot be empty")
        
        if len(name_stripped) < FormValidator.NAME_MIN_LENGTH:
            raise ValidationError(
                "name", 
                f"Name must be at least {FormValidator.NAME_MIN_LENGTH} characters"
            )
        
        if len(name_stripped) > FormValidator.NAME_MAX_LENGTH:
            raise ValidationError(
                "name",
                f"Name must be at most {FormValidator.NAME_MAX_LENGTH} characters"
            )
    
    @staticmethod
    def validate_age(age: Optional[Any]) -> None:
        if age is None:
            return  # Optional field
        
        try:
            age_int = int(age)
        except (ValueError, TypeError):
            raise ValidationError("age", "Age must be a number")
        
        if age_int < FormValidator.AGE_MIN or age_int > FormValidator.AGE_MAX:
            raise ValidationError(
                "age",
                f"Age must be between {FormValidator.AGE_MIN} and {FormValidator.AGE_MAX}"
            )
    
    @staticmethod
    def validate_gender(gender: Optional[str]) -> None:
        if gender is None:
            return  # Optional field
        
        if not isinstance(gender, str):
            raise ValidationError("gender", "Gender must be a string")
        
        if gender.lower() not in FormValidator.ALLOWED_GENDERS:
            raise ValidationError(
                "gender",
                f"Gender must be one of: {', '.join(FormValidator.ALLOWED_GENDER_VALUES)}"
            )
    
    @staticmethod
    def validate_password(password: Optional[str]) -> None:
        if password is None:
            return  # Optional field
        
        if not isinstance(password, str):
            raise ValidationError("password", "Password must be a string")
        
        if len(password) < FormValidator.PASSWORD_MIN_LENGTH:
            raise ValidationError(
                "password",
                f"Password must be at least {FormValidator.PASSWORD_MIN_LENGTH} characters"
            )
    
    @staticmethod
    def validate_date(date_str: Optional[str]) -> None:
        """Validate date field (YYYY-MM-DD format)."""
        if date_str is None:
            return  # Optional field
        
        try:
            datetime.strptime(str(date_str), "%Y-%m-%d")
        except (ValueError, TypeError):
            raise ValidationError(
                "date",
                "Date must be in format YYYY-MM-DD"
            )
    
    @classmethod
    def validate_form_data(cls, form_data: Dict[str, Any]) -> None:

        # Basic validation
        cls.validate_empty_data(form_data)
        
        # Email validation (usually required)
        email = form_data.get("email")
        if email:
            cls.validate_email_format(email)
        
        # Optional field validations
        cls.validate_name(form_data.get("name"))
        cls.validate_age(form_data.get("age"))
        cls.validate_gender(form_data.get("gender"))
        cls.validate_password(form_data.get("password"))
        cls.validate_date(form_data.get("date"))


def check_duplicate_email(email: str, existing_submissions: List[Any]) -> bool:
    if not email:
        return False
    
    for submission in existing_submissions:
        if submission.form_data.get("email") == email:
            return True
    return False


def check_duplicate_submission(
    new_data: Dict[str, Any],
    existing_submissions: List[Any]
) -> bool:
    if not new_data or not existing_submissions:
        return False
    
    for submission in existing_submissions:
        if new_data == submission.form_data:
            return True
    return False