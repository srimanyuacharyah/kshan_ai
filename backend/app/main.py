from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.core.middleware import RequestObservabilityMiddleware
from backend.app.api.v1.router import api_v1_router, root_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown hooks."""
    logger.info(f"Initializing {settings.PROJECT_NAME} AI Multiverse Engine in {settings.ENVIRONMENT} mode...")
    logger.info(f"Tagline: {settings.TAGLINE}")
    logger.info(f"Configured Vector Embedding Dimension: {settings.EMBEDDING_DIMENSION}")
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

# Custom Structured Exception Handlers
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
