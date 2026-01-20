import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.infrastructure.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    logger.info("Starting TV Series API...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down TV Series API...")


# Create FastAPI application
app = FastAPI(
    title="TV Series Tracker API",
    description="API for tracking TV series, episodes, and generating AI insights",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:7777",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:7777",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "TV Series Tracker API",
        "docs": "/docs",
        "health": "/api/health",
    }

