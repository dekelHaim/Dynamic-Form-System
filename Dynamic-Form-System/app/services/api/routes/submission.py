from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.services.database.database import get_db
from app.services.database.models import Submission, FormSchema
from app.services.api.schemas import SubmissionCreate, SubmissionResponse
from app.services.api.validators import validate_form_data

router = APIRouter(prefix="/submissions", tags=["Submissions"])

# ═══════════════════════════════════════════════════════════
# POST /api/submissions/ - CREATE SUBMISSION WITH VALIDATION
# ═══════════════════════════════════════════════════════════

@router.post("/", response_model=SubmissionResponse)
def create_submission(submission: SubmissionCreate, db: Session = Depends(get_db)):
    """Create a new submission with validation"""
    
    # ✅ 1. Verify form exists
    form = db.query(FormSchema).filter(FormSchema.id == submission.form_schema_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # ✅ 2. VALIDATE submitted data against form schema
    is_valid, errors = validate_form_data(submission.data, form.schema_definition)
    if not is_valid:
        raise HTTPException(
            status_code=422,
            detail={"message": "Validation failed", "errors": errors}
        )
    
    # ✅ 3. Check for duplicates by email
    is_duplicate = False
    if submission.data and submission.data.get('email'):
        email = submission.data.get('email')
        existing = db.query(Submission).filter(
            and_(
                Submission.form_schema_id == submission.form_schema_id,
                Submission.data.contains({'email': email})
            )
        ).first()
        is_duplicate = existing is not None
    
    # ✅ 4. Create submission
    db_submission = Submission(
        form_schema_id=submission.form_schema_id,
        form_name=form.name,
        data=submission.data,
        user_email=submission.data.get('email') if submission.data else '',
        validation_status="valid",
        is_duplicate=is_duplicate
    )
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    return db_submission


# ═══════════════════════════════════════════════════════════
# GET /api/submissions/ - LIST SUBMISSIONS WITH PAGINATION
# ═══════════════════════════════════════════════════════════

@router.get("/")
def list_submissions(
    form_id: int = Query(None, description="Filter by form ID"),
    email: str = Query("", description="Filter by email"),
    sort: str = Query("created_at", description="Sort: created_at, email, is_duplicate"),
    order: str = Query("desc", description="asc or desc"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=5, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List submissions with smart pagination
    
    - Page-based pagination
    - Efficient filtering
    - Sorting support
    """
    
    # ✅ 1. Form ID required
    if not form_id:
        raise HTTPException(status_code=400, detail="form_id required")
    
    # ✅ 2. Verify form exists
    form = db.query(FormSchema).filter(FormSchema.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # ✅ 3. Build query
    query = db.query(Submission).filter(Submission.form_schema_id == form_id)
    
    # ✅ 4. Apply email filter
    if email:
        query = query.filter(Submission.user_email.ilike(f"%{email}%"))
    
    # ✅ 5. Get total count
    total = query.count()
    
    # ✅ 6. Apply sorting
    sort_map = {
        "created_at": Submission.created_at,
        "email": Submission.user_email,
        "is_duplicate": Submission.is_duplicate
    }
    
    sort_field = sort_map.get(sort, Submission.created_at)
    if order.lower() == "asc":
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())
    
    # ✅ 7. PAGE-BASED PAGINATION
    skip = (page - 1) * limit
    submissions = query.offset(skip).limit(limit).all()
    
    # ✅ 8. Calculate pagination info
    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "form_id": form_id,
        "form_name": form.name,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "submissions": submissions
    }


# ═══════════════════════════════════════════════════════════
# GET /api/submissions/{submission_id} - GET SINGLE SUBMISSION
# ═══════════════════════════════════════════════════════════

@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    """Get a specific submission by ID"""
    
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return submission


# ═══════════════════════════════════════════════════════════
# DELETE /api/submissions/{submission_id} - DELETE SUBMISSION
# ═══════════════════════════════════════════════════════════

@router.delete("/{submission_id}")
def delete_submission(submission_id: int, db: Session = Depends(get_db)):
    """Delete a submission"""
    
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    db.delete(submission)
    db.commit()
    
    return {"ok": True, "message": f"Submission {submission_id} deleted"}


# ═══════════════════════════════════════════════════════════
# GET /api/submissions/analytics/{form_id} - ANALYTICS & STATS
# ═══════════════════════════════════════════════════════════

@router.get("/analytics/{form_id}")
def get_submission_analytics(form_id: int, db: Session = Depends(get_db)):
    """Get quick analytics for a form's submissions"""
    
    # ✅ 1. Verify form exists
    form = db.query(FormSchema).filter(FormSchema.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    # ✅ 2. Get stats
    total = db.query(func.count(Submission.id)).filter(
        Submission.form_schema_id == form_id
    ).scalar() or 0
    
    duplicates = db.query(func.count(Submission.id)).filter(
        and_(
            Submission.form_schema_id == form_id,
            Submission.is_duplicate == True
        )
    ).scalar() or 0
    
    unique = total - duplicates if total > 0 else 0
    duplicate_percentage = round((duplicates / total * 100) if total > 0 else 0, 2)
    
    return {
        "form_id": form_id,
        "form_name": form.name,
        "total_submissions": total,
        "unique_submissions": unique,
        "duplicate_submissions": duplicates,
        "duplicate_percentage": duplicate_percentage
    }