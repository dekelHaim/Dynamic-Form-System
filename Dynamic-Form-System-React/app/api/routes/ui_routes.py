from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/", tags=["Root"])
async def root():
    """Root endpoint - API info."""
    return {
        "message": "Dynamic Form System API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "submissions": {
                "submit": "POST /api/submissions/submit",
                "list": "GET /api/submissions/",
                "get": "GET /api/submissions/{id}",
                "delete": "DELETE /api/submissions/{id}"
            }
        }
    }


@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "Dynamic Form System API",
        "version": "1.0.0"
    }