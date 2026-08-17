from fastapi import APIRouter
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.rag import router as rag_router
from backend.app.api.v1.ai import router as ai_router
from backend.app.api.v1.multiverse import router as multiverse_router
from backend.app.api.v1.scenarios import router as scenarios_router

api_v1_router = APIRouter(prefix="/api/v1")

# Include Modular Routers
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(rag_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(multiverse_router, prefix="/multiverse", tags=["multiverse"])
api_v1_router.include_router(scenarios_router, prefix="/scenarios", tags=["scenarios"])

# Root convenience endpoints
root_router = APIRouter()
root_router.include_router(health_router, prefix="/api")
