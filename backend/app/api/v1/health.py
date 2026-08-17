from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.services.mcp.client import mcp_client

router = APIRouter(prefix="/health", tags=["Health & Observability"])

@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness():
    """Liveness probe returning 200 if FastAPI process is operational."""
    return {
        "status": "live",
        "service": "KSHAN Multiverse Engine",
        "version": "1.0.0"
    }

@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness(db: AsyncSession = Depends(get_db)):
    """Readiness probe validating PostgreSQL database, pgvector extension, and MCP server status."""
    db_status = "healthy"
    vector_extension = "inactive"
    
    try:
        result = await db.execute(text("SELECT 1"))
        _ = result.scalar()
        
        try:
            ext_result = await db.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            )
            if ext_result.scalar():
                vector_extension = "active"
        except Exception:
            vector_extension = "fallback_mock"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check MCP status
    mcp_health = await mcp_client.check_connection()

    return {
        "status": "ready" if "healthy" in db_status else "degraded",
        "database": db_status,
        "pgvector_extension": vector_extension,
        "mcp_server": {
            "connected": mcp_health.connected,
            "server_name": mcp_health.server_name,
            "tools_count": mcp_health.tools_count
        },
        "embedding_dimension": settings.EMBEDDING_DIMENSION,
        "embedding_model": settings.EMBEDDING_MODEL,
        "demo_mode": settings.DEMO_MODE,
        "environment": settings.ENVIRONMENT
    }
