from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

@router.get("/")
def home():
    """Render home page (forms list)"""
    template_path = TEMPLATES_DIR / "forms_list.html"
    return FileResponse(template_path)

@router.get("/create")
def create_form_page():
    """Render create form page"""
    template_path = TEMPLATES_DIR / "create_form.html"
    return FileResponse(template_path)

@router.get("/form/{form_id}")
def form_detail_page(form_id: int):
    """Render form detail page with form_id passed to HTML"""
    template_path = TEMPLATES_DIR / "form_detail.html"
    
    # ✅ Read HTML file
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # ✅ INJECT form_id into HTML as data attribute
    # This way JavaScript can find it
    html = html.replace(
        '<form id="formDetail"',
        f'<form id="formDetail" data-form-id="{form_id}"'
    )
    
    return HTMLResponse(html)

@router.get("/submissions")
def submissions_page(form_id: int = None):
    """Render submissions page"""
    template_path = TEMPLATES_DIR / "submissions_list.html"
    
    # If form_id provided, pass it to HTML
    if form_id:
        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
        html = html.replace(
            '<div id="loading"',
            f'<div id="loading" data-form-id="{form_id}"'
        )
        return HTMLResponse(html)
    
    return FileResponse(template_path)