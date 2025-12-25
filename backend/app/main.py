"""
RAG Chatboard FastAPI Backend.

Main application entry point with CORS, rate limiting, and all routers.
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings, validate_settings
from .middleware.rate_limiter import RateLimitMiddleware
from .routers import chat, ingest, meta, gamified, profile, personalize, chat_history, translate
from .models import HealthResponse
from .db_neon import get_neon_db


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting RAG Chatboard API...")
    
    # Validate configuration
    errors = validate_settings()
    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        # Don't fail startup, but log warnings
    
    # Initialize Neon tables if enabled
    neon = get_neon_db()
    if neon.enabled:
        try:
            await neon.ensure_tables()
            logger.info("Neon database tables initialized")
            
            # Seed default skills
            await neon.register_skill("Math Guru", "Expert in mathematical formulas and derivations.", 50)
            await neon.register_skill("Code Mentor", "Specialized in Python, C++, and Real-time robotics programming.", 50)
            await neon.register_skill("Hardware Hacker", "Guides you through electronic circuits and sensor wiring.", 50)
            await neon.register_skill("Concept Artist", "Explains abstract concepts through analogies and visual descriptions.", 30)
            logger.info("Default AI skills seeded")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Neon tables: {e}")
    
    logger.info("RAG Chatboard API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Chatboard API...")
    
    # Close Neon connection
    neon = get_neon_db()
    if neon.enabled:
        await neon.close()
    
    logger.info("RAG Chatboard API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="RAG Chatboard API",
    description="Retrieval-Augmented Generation Chat API for Physical AI & Humanoid Robotics Textbook",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get settings
settings = get_settings()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(meta.router, prefix="/api", tags=["Metadata"])
app.include_router(gamified.router, prefix="/api", tags=["Gamification"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(personalize.router, prefix="/api", tags=["Personalization"])
app.include_router(chat_history.router, prefix="/api/chat", tags=["Chat History"])
app.include_router(translate.router, prefix="/api", tags=["Translation"])


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns API status and version.
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "RAG Chatboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
