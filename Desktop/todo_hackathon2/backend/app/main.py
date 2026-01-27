"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import create_db_and_tables


# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="FastAPI backend for Todo application with JWT authentication",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers including Authorization
)


@app.on_event("startup")
def on_startup():
    """Create database tables on application startup."""
    try:
        create_db_and_tables()
        print("[STARTUP] Database tables created successfully")
    except Exception as e:
        print(f"[STARTUP] Warning: DB table creation failed (will retry on first request): {e}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Todo API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


# Import and include routers
from app.routers import tasks, auth, mcp, chat, internal, reminders
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(reminders.router)  # Reminder endpoints
app.include_router(mcp.router)  # MCP Tools router
app.include_router(chat.router)  # AI Chatbot router
app.include_router(internal.router)  # Internal service-to-service API
