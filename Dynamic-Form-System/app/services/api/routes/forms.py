from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.database.database import get_db
from app.services.database.models import FormSchema
from app.services.api.schemas import FormCreate, FormResponse
from app.services.api.validators import validate_form_data

router = APIRouter(prefix="/forms", tags=["Forms"])

# ═══════════════════════════════════════════════════════════
# POST /api/forms/ - CREATE FORM WITH VALIDATION
# ═══════════════════════════════════════════════════════════

@router.post("/", response_model=FormResponse)
def create_form(form: FormCreate, db: Session = Depends(get_db)):
    """Create a new form with full validation"""
    
    # ✅ 1. Validate schema is not empty
    if not form.schema_definition or len(form.schema_definition) == 0:
        raise HTTPException(status_code=400, detail="Schema cannot be empty")
    
    # ✅ 2. Check form name is unique
    if db.query(FormSchema).filter(FormSchema.name == form.name).first():
        raise HTTPException(status_code=400, detail=f"Form '{form.name}' already exists")
    
    # ✅ 3. VALIDATE user_details against schema if provided
    if form.user_details:
        is_valid, errors = validate_form_data(form.user_details, form.schema_definition)
        if not is_valid:
            raise HTTPException(
                status_code=422,
                detail={"message": "Validation failed", "errors": errors}
            )
    
    # ✅ 4. Check for duplicate email if provided
    if form.user_details and form.user_details.get('email'):
        email = form.user_details.get('email')
        existing_forms = db.query(FormSchema).all()
        for existing_form in existing_forms:
            if (existing_form.user_details and 
                existing_form.user_details.get('email', '').lower() == email.lower()):
                raise HTTPException(
                    status_code=400,
                    detail=f"Email '{email}' already exists in system"
                )
    
    # ✅ 5. Create and save form
    db_form = FormSchema(
        name=form.name,
        description=form.description or "",
        schema_definition=form.schema_definition,
        data=form.data or {},
        user_details=form.user_details or {}
    )
    
    db.add(db_form)
    db.commit()
    db.refresh(db_form)
    
    return db_form


# ═══════════════════════════════════════════════════════════
# GET /api/forms/ - LIST ALL FORMS with FILTERING
# ═══════════════════════════════════════════════════════════

@router.get("/")
def list_forms(
    search: str = Query("", description="Search by name (starts with)"),
    sort: str = Query("created_at", description="Sort by: created_at, name, id"),
    order: str = Query("desc", description="Order: asc, desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List forms with smart filtering and sorting"""
    
    query = db.query(FormSchema)
    
    # 🔍 SMART SEARCH: Use ILIKE with prefix
    if search:
        search_pattern = f"{search}%"
        query = query.filter(FormSchema.name.ilike(search_pattern))
    
    # Get total BEFORE sort
    total = query.count()
    
    # 📊 SORT: Only allowed fields
    sort_field_map = {
        "created_at": FormSchema.created_at,
        "name": FormSchema.name,
        "id": FormSchema.id
    }
    
    sort_field = sort_field_map.get(sort, FormSchema.created_at)
    
    if order.lower() == "asc":
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())
    
    # 📄 PAGINATION
    forms = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "forms": forms,
        "search_mode": "prefix" if search else "all",
        "sort": sort,
        "order": order
    }


# ═══════════════════════════════════════════════════════════
# GET /api/forms/{form_id} - GET SINGLE FORM
# ═══════════════════════════════════════════════════════════

@router.get("/{form_id}", response_model=FormResponse)
def get_form(form_id: int, db: Session = Depends(get_db)):
    """Get specific form by ID with all data including user_details"""
    
    form = db.query(FormSchema).filter(FormSchema.id == form_id).first()
    
    if not form:
        raise HTTPException(status_code=404, detail=f"Form {form_id} not found")
    
    # ✅ ENSURE user_details is returned
    if not hasattr(form, 'user_details'):
        form.user_details = {}
    
    return form


# ═══════════════════════════════════════════════════════════
# PUT /api/forms/{form_id} - UPDATE FORM WITH VALIDATION
# ═══════════════════════════════════════════════════════════

@router.put("/{form_id}", response_model=FormResponse)
def update_form(form_id: int, form_data: FormCreate, db: Session = Depends(get_db)):
    """Update form with full validation"""
    
    # ✅ 1. Find existing form
    form = db.query(FormSchema).filter(FormSchema.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail=f"Form {form_id} not found")
    
    # ✅ 2. Check name uniqueness - ONLY if name changed
    if form_data.name != form.name:
        existing = db.query(FormSchema).filter(
            FormSchema.name == form_data.name,
            FormSchema.id != form_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Form name '{form_data.name}' already exists"
            )
    
    # ✅ 3. VALIDATE user_details against schema if provided
    if form_data.user_details:
        is_valid, errors = validate_form_data(form_data.user_details, form_data.schema_definition)
        if not is_valid:
            raise HTTPException(
                status_code=422,
                detail={"message": "Validation failed", "errors": errors}
            )
    
    # ✅ 4. Check for duplicate email - DATABASE-AGNOSTIC
    if form_data.user_details and form_data.user_details.get('email'):
        email = form_data.user_details.get('email')
        
        # Works with PostgreSQL, SQLite, MySQL, any database
        existing_forms = db.query(FormSchema).all()
        for existing_form in existing_forms:
            if (existing_form.id != form_id and
                existing_form.user_details and
                existing_form.user_details.get('email', '').lower() == email.lower()):
                raise HTTPException(
                    status_code=400,
                    detail=f"Email '{email}' already in use"
                )
    
    # ✅ 5. UPDATE all fields
    form.name = form_data.name
    form.description = form_data.description or ""
    form.schema_definition = form_data.schema_definition
    form.data = form_data.data or {}
    form.user_details = form_data.user_details or {}
    
    # ✅ 6. Save to database
    db.commit()
    db.refresh(form)
    
    return form


# ═══════════════════════════════════════════════════════════
# DELETE /api/forms/{form_id} - DELETE FORM
# ═══════════════════════════════════════════════════════════

@router.delete("/{form_id}")
def delete_form(form_id: int, db: Session = Depends(get_db)):
    """Delete form"""
    
    form = db.query(FormSchema).filter(FormSchema.id == form_id).first()
    
    if not form:
        raise HTTPException(status_code=404, detail=f"Form {form_id} not found")
    
    db.delete(form)
    db.commit()
    
    return {"message": f"Form {form_id} deleted"}


# ═══════════════════════════════════════════════════════════
# GET /api/forms/stats/summary - STATS
# ═══════════════════════════════════════════════════════════

@router.get("/stats/summary")
def get_forms_stats(db: Session = Depends(get_db)):
    """Get forms statistics (cached by gateway)"""
    
    total = db.query(func.count(FormSchema.id)).scalar()
    
    return {"total_forms": total, "cached": True}