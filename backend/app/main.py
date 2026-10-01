import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import get_connection, init_database

# =====================================================
# LIFESPAN: Modern FastAPI pattern (replaces deprecated @app.on_event)
# =====================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    - Startup: Initialize database tables
    - Shutdown: Cleanup if needed
    """
    # Startup
    print("🚀 Starting Loan Application API...")
    init_database()
    print("✅ Database initialized")
    
    yield  # Application runs here
    
    # Shutdown (if needed)
    print("👋 Shutting down Loan Application API...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Loan Application API",
    description="API for managing loan applications with Supabase authentication",
    version="1.0.0",
    lifespan=lifespan
)

# =====================================================
# CORS CONFIGURATION
# Allows React frontend at http://localhost:5173 to call the API
# In production, restrict origins to your actual frontend domain
# =====================================================
allowed_origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative React dev server
]

# Set FRONTEND_URL to the deployed frontend domain in Vercel, for example:
# https://your-frontend.vercel.app
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ROUTERS
# Import and include route modules
# =====================================================
from .auth import router as auth_router
from .loans import router as loans_router

app.include_router(auth_router)
app.include_router(loans_router)


# =====================================================
# ROOT ENDPOINTS
# =====================================================
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Loan Application API",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)