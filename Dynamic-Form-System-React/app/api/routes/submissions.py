from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.services.database.database import get_db
from app.services.database.models import FormSubmission
from app.api.schemas.schemas import (
    FormDataSubmission,
    FormSubmissionResponse,
    FormSubmissionsListResponse,
)

from app.api.schemas.validators import (
    FormValidator,
    ValidationError as CustomValidationError,
    check_duplicate_email,
    check_duplicate_submission,
)

from typing import Dict, Any, Optional

router = APIRouter(prefix="/submissions", tags=["Submissions"])


# ============================================================================
# ✅ ORDER FIXED: POST ROUTES FIRST, THEN SPECIFIC GETS, THEN GENERIC, THEN DYNAMIC
# ============================================================================


# 1️⃣ POST ENDPOINT - FIRST
@router.post(
    "/submit",
    response_model=FormSubmissionResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_form(
    submission: FormDataSubmission,
    db: Session = Depends(get_db)
):
    """
    Submit form data with professional validation.
    
    Validates:
    - Form data is not empty
    - Email format is valid
    - Email is unique (not duplicated)
    - Name, age, gender are valid if present
    - Detects duplicate submissions
    
    Returns:
    - 201 Created: Submission successful
    - 400 Bad Request: Validation error with clear field message
    - 500 Internal Server Error: Database error
    """
    try:
        form_data = submission.data
        
        # ============ MAIN VALIDATION ============
        try:
            FormValidator.validate_form_data(form_data)
        except CustomValidationError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ve.message
            )
        
        # ============ EMAIL UNIQUENESS CHECK ============
        email = form_data.get("email")
        if email:
            existing_submissions = db.query(FormSubmission).all()
            if check_duplicate_email(email, existing_submissions):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Email '{email}' already registered. Please use a different email."
                )
        
        # ============ DUPLICATE SUBMISSION CHECK ============
        existing_submissions = db.query(FormSubmission).all()
        is_duplicate = check_duplicate_submission(form_data, existing_submissions)
        
        # ============ SAVE TO DATABASE ============
        new_submission = FormSubmission(
            form_data=form_data,
            is_duplicate=is_duplicate
        )
        
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
        
        response = FormSubmissionResponse(
            id=new_submission.id,
            form_data=new_submission.form_data,
            is_duplicate=new_submission.is_duplicate,
            submitted_at=new_submission.submitted_at
        )
        
        return response
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error in submit_form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error: Could not process submission"
        )


# 2️⃣ SPECIFIC GET ENDPOINTS - SECOND (More specific routes first)
@router.get(
    "/stats/duplicate-count",
    status_code=status.HTTP_200_OK
)
def get_duplicate_stats(db: Session = Depends(get_db)):
    """Get duplicate statistics."""
    try:
        total = db.query(FormSubmission).count()
        duplicates = (
            db.query(FormSubmission)
            .filter(FormSubmission.is_duplicate == True)
            .count()
        )
        
        return {
            "total": total,
            "duplicates": duplicates,
            "unique": total - duplicates,
            "duplicate_percentage": (
                round((duplicates / total * 100), 2) if total > 0 else 0
            )
        }
    except Exception as e:
        print(f"❌ Error in get_duplicate_stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error: Could not retrieve statistics"
        )


@router.get(
    "/existing-emails",
    status_code=status.HTTP_200_OK
)
def get_existing_emails(db: Session = Depends(get_db)):
    """Get list of all unique emails in system."""
    try:
        submissions = db.query(FormSubmission).all()
        emails = [
            s.form_data.get("email")
            for s in submissions
            if s.form_data.get("email")
        ]
        
        unique_emails = list(set(emails))
        return {
            "emails": unique_emails,
            "count": len(unique_emails)
        }
    except Exception as e:
        print(f"❌ Error in get_existing_emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error: Could not retrieve emails"
        )


# 3️⃣ GENERIC GET ENDPOINT - THIRD
@router.get(
    "/",
    response_model=FormSubmissionsListResponse,
    status_code=status.HTTP_200_OK
)
def get_submissions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Records per page"),
    sort_by: str = Query(
        "submitted_at",
        description="Sort field: id, submitted_at, is_duplicate"
    ),
    order: str = Query(
        "desc",
        regex="^(asc|desc)$",
        description="Sort order: asc or desc"
    ),
    is_duplicate: Optional[bool] = Query(
        None,
        description="Filter: true for duplicates only, false for unique only"
    ),
    db: Session = Depends(get_db)
):
    """Get list of form submissions with pagination, sorting, and filtering."""
    try:
        query = db.query(FormSubmission)
        
        # Apply filter if specified
        if is_duplicate is not None:
            query = query.filter(FormSubmission.is_duplicate == is_duplicate)
        
        total = query.count()
        
        # Apply sorting
        if sort_by == "is_duplicate":
            sort_column = FormSubmission.is_duplicate
        elif sort_by == "id":
            sort_column = FormSubmission.id
        else:
            sort_column = FormSubmission.submitted_at
        
        if order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Apply pagination
        submissions = query.offset(skip).limit(limit).all()
        
        return FormSubmissionsListResponse(
            submissions=[
                FormSubmissionResponse(
                    id=s.id,
                    form_data=s.form_data,
                    is_duplicate=s.is_duplicate,
                    submitted_at=s.submitted_at
                )
                for s in submissions
            ],
            total=total
        )
    except Exception as e:
        print(f"❌ Error in get_submissions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error: Could not retrieve submissions"
        )


# 4️⃣ DYNAMIC ROUTES - LAST (These use path parameters and are most generic)
@router.get(
    "/{submission_id}",
    response_model=FormSubmissionResponse,
    status_code=status.HTTP_200_OK
)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db)
):
    """Get a single submission by ID."""
    submission = (
        db.query(FormSubmission)
        .filter(FormSubmission.id == submission_id)
        .first()
    )
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission {submission_id} not found"
        )
    
    return FormSubmissionResponse(
        id=submission.id,
        form_data=submission.form_data,
        is_duplicate=submission.is_duplicate,
        submitted_at=submission.submitted_at
    )


@router.delete(
    "/{submission_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db)
):
    """Delete a submission by ID."""
    submission = (
        db.query(FormSubmission)
        .filter(FormSubmission.id == submission_id)
        .first()
    )
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission {submission_id} not found"
        )
    
    db.delete(submission)
    db.commit()
    print(f"🗑️ Deleted submission {submission_id}")
    return None