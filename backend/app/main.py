import os
import sys

# Ensure both project root and backend directory are in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.abspath(os.path.join(_current_dir, ".."))
_root_dir = os.path.abspath(os.path.join(_backend_dir, ".."))
for p in [_root_dir, _backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.middleware import RequestObservabilityMiddleware
from backend.app.api.v1.router import api_v1_router, root_router

from backend.app.core.database import engine
from backend.app.models.base import Base
import backend.app.models  # Ensure all model tables are registered in Base.metadata

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    logger.info(f"Initializing {settings.PROJECT_NAME} AI Multiverse Engine in {settings.ENVIRONMENT} mode...")
    logger.info(f"Tagline: {settings.TAGLINE}")
    logger.info(f"Configured Vector Embedding Dimension: {settings.EMBEDDING_DIMENSION}")
    
    # Initialize database tables automatically (for SQLite or uninitialized instances)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Database schema auto-creation skipped or failed: {e}")

    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME} Multiverse Engine...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="One Moment. Infinite Lives. Your choices create worlds that never existed.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

from fastapi.exceptions import RequestValidationError
import json

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "req-unknown")
    try:
        body = await request.body()
        body_json = json.loads(body.decode("utf-8"))
        if isinstance(body_json, dict) and "password" in body_json:
            body_json = {**body_json, "password": "[REDACTED]"}
    except Exception:
        body_json = "<unparseable>"
    logger.error(f"[DEBUG 422 VALIDATION ERROR] URL={request.url.path}, Errors={exc.errors()}, Received Body={body_json}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "error": {
                "code": "HTTP_422_UNPROCESSABLE_ENTITY",
                "message": "Request validation failed.",
                "details": exc.errors(),
                "request_id": request_id
            }
        },
        headers={"X-Request-ID": request_id}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "req-unknown")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "request_id": request_id
            }
        },
        headers={"X-Request-ID": request_id}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "req-unknown")
    logger.error(f"Unhandled server anomaly on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server anomaly occurred in multiverse execution.",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "A multiverse anomaly occurred while processing your request.",
                "request_id": request_id
            }
        },
        headers={"X-Request-ID": request_id}
    )

# Observability middleware
app.add_middleware(RequestObservabilityMiddleware)

# Production-safe CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time-Ms"]
)

# Mount API Routers
app.include_router(api_v1_router)
app.include_router(root_router)

@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "tagline": settings.TAGLINE,
        "status": "online",
        "docs": "/api/docs",
        "health": "/api/v1/health/ready"
    }
