import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from backend.app.core.logging import logger

class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware for injecting Request IDs, logging latency, and tracking execution metrics."""
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-Ms"] = str(process_time_ms)
            
            # Log HTTP request
            if request.url.path not in ["/api/v1/health/live", "/health"]:
                logger.info(
                    f"{request.method} {request.url.path} completed with status {response.status_code} in {process_time_ms}ms",
                    extra={
                        "request_id": request_id,
                        "duration_ms": process_time_ms,
                        "status_code": response.status_code,
                        "path": request.url.path,
                        "method": request.method
                    }
                )
            return response
        except Exception as e:
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"Unhandled error processing {request.method} {request.url.path}: {e}",
                exc_info=True,
                extra={"request_id": request_id, "duration_ms": process_time_ms}
            )
            raise
