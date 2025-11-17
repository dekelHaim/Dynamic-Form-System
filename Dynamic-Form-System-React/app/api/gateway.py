
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
import json

# Database
from app.services.database.database import engine
from app.services.database.models import Base
# Routes
from app.api.routes import ui_routes
from app.api.routes.submissions import router as submissions_router
# Cache
from app.services.cache.cache import cache_get, cache_set, cache_delete_pattern


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management - startup and shutdown."""
    print("🔄 Initializing Dynamic Form System...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
    
    print("✅ Application initialized.")
    yield
    print("👋 Shutting down Dynamic Form System API...")


# Create FastAPI app
app = FastAPI(
    title="Dynamic Form System",
    description="Backend API for dynamic form generation with validation, caching, and analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


def _generate_cache_key(request: Request) -> str:

    path = request.url.path
    method = request.method
    query = request.url.query
    
    cache_key = f"{method}:{path}"
    if query:
        cache_key += f"?{query}"
    
    return cache_key


@app.middleware("http")
async def cache_middleware(request: Request, call_next):

    path = request.url.path
    method = request.method
    is_api = path.startswith("/api/")
    
    # ============ HANDLE GET REQUESTS ============
    if method == "GET" and is_api:
        cache_key = _generate_cache_key(request)
        
        # Try to get from cache
        cached_data = cache_get(cache_key)
        if cached_data:
            print(f"✅ CACHE HIT: {path}")
            return JSONResponse(content=cached_data)
        
        print(f"❌ CACHE MISS: {path}")
    
    # ============ EXECUTE REQUEST ============
    response = await call_next(request)
    
    # ============ CACHE SUCCESSFUL GET RESPONSES ============
    if method == "GET" and is_api and response.status_code == 200:
        try:
            # Read response body
            body = b"".join([chunk async for chunk in response.body_iterator])
            data = json.loads(body)
            
            # Generate cache key
            cache_key = _generate_cache_key(request)
            
            # Store in cache (1 hour TTL)
            cache_set(cache_key, data, ttl=3600)
            print(f"💾 CACHED: {path}")
            
            # Return response
            async def stream():
                yield body
            
            return StreamingResponse(
                stream(),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json"
            )
        except Exception as e:
            print(f"⚠️ Cache storage error: {e}")
            return response
    
    # ============ INVALIDATE CACHE FOR MUTATIONS ============
    if method in {"POST", "PUT", "DELETE"} and is_api:
        try:
            if "/submissions" in path:
                # Invalidate ALL submission-related cache
                deleted = cache_delete_pattern("GET:/api/submissions*")
                print(f"🗑️ INVALIDATED {deleted} cache keys for /api/submissions/* (after {method})")
        except Exception as e:
            print(f"⚠️ Cache invalidation error: {e}")
    
    return response


# ============ ADD CORS MIDDLEWARE ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ INCLUDE ROUTERS ============

app.include_router(submissions_router, prefix="/api", tags=["Submissions"])
app.include_router(ui_routes.router, tags=["UI"])


# ============ HEALTH CHECK ============
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "Dynamic Form System API",
        "version": "1.0.0",
        "cache": "enabled"
    }


# ============ ROOT ENDPOINT ============
@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API information."""
    return {
        "message": "Dynamic Form System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "forms": "/docs#/Submissions",
            "submissions": "/api/submissions/"
        }
    }