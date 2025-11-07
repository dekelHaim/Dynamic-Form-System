from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
import json

from app.services.database.database import engine, Base
from app.services.api.routes.forms import router as forms_router
from app.services.api.routes.submission import router as submissions_router
from app.services.api.routes import ui_routes
# Cache
from app.services.cache.cache import cache_get, cache_set, cache_delete_pattern

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events"""
    print("🔄 Initializing Dynamic Form System...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
    print("✅ Cache middleware initialized.")
    yield
    print("👋 Shutting down Dynamic Form System API...")


app = FastAPI(
    title="Dynamic Form System",
    description="Backend API for dynamic form generation, validation, and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


@app.middleware("http")
async def cache_middleware(request: Request, call_next):

    path = request.url.path
    method = request.method
    is_api = path.startswith("/api/")

    # ======== GET Requests: Try to read from cache ========
    if method == "GET" and is_api:
        cache_key = f"{method}:{path}"
        if request.url.query:
            cache_key += f"?{request.url.query}"

        cached_data = cache_get(cache_key)
        if cached_data:
            print(f"✅ CACHE HIT: {path}")
            return JSONResponse(content=cached_data)
        print(f"❌ CACHE MISS: {path}")

    # ======== Continue to actual request ========
    response = await call_next(request)

    # ======== Cache successful GET responses ========
    if method == "GET" and is_api and response.status_code == 200:
        try:
            body = b"".join([chunk async for chunk in response.body_iterator])
            data = json.loads(body)
            cache_key = f"{method}:{path}"
            if request.url.query:
                cache_key += f"?{request.url.query}"

            cache_set(cache_key, data, ttl=3600)
            print(f"💾 CACHED: {path}")

            async def stream():
                yield body
            return StreamingResponse(
                stream(),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json",
            )
        except Exception as e:
            print(f"⚠️ Cache error: {e}")
            return response

    # ======== Invalidate cache after data changes ========
    if method in {"POST", "PUT", "DELETE"} and is_api:
        try:
            # Invalidate all forms-related cache (includes /create_form)
            if any(p in path for p in ["/forms", "/create_form"]):
                deleted = cache_delete_pattern("GET:/api/forms*")
                print(f"🗑️ INVALIDATED ({deleted} keys): /api/forms/* (after {method})")

            # Invalidate all submissions-related cache
            elif "/submissions" in path:
                deleted = cache_delete_pattern("GET:/api/submissions*")
                print(f"🗑️ INVALIDATED ({deleted} keys): /api/submissions/* (after {method})")

        except Exception as e:
            print(f"⚠️ Invalidation error: {e}")

    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ui_routes.router, tags=["UI"])
app.include_router(forms_router, prefix="/api", tags=["Forms"])
app.include_router(submissions_router, prefix="/api", tags=["Submissions"])


@app.get("/health", tags=["Health"])
def health_check():
    """Simple health check for monitoring and uptime verification."""
    return {
        "status": "ok",
        "service": "Dynamic Form System API",
        "version": "1.0.0",
        "cache": "enabled",
    }

@app.get("/", tags=["Root"])
def root():
    """Root endpoint."""
    return {
        "message": "Dynamic Form System API",
        "docs": "/docs",
        "health": "/health",
    }