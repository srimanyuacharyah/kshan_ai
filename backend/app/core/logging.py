import logging
import sys
import json
from datetime import datetime, timezone

class StructuredJsonFormatter(logging.Formatter):
    """Structured JSON log formatter for production observability."""
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging() -> logging.Logger:
    logger = logging.getLogger("kshan")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        
    return logger

def get_logger(name: str = "kshan") -> logging.Logger:
    return logging.getLogger(name)

logger = setup_logging()
