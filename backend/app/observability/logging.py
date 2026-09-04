import logging
import json
from datetime import datetime
from app.observability.tracing import get_correlation_id

class StructuredJSONFormatter(logging.Formatter):
    """
    Structured JSON log formatter injecting request_id correlation context,
    timestamp, log level, and logger module name.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": get_correlation_id(),
            "message": record.getMessage()
        }

        if hasattr(record, "submission_id"):
            log_data["submission_id"] = record.submission_id
        if hasattr(record, "attempt_id"):
            log_data["attempt_id"] = record.attempt_id

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)
