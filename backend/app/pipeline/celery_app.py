import logging
from celery import Celery
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery app instance bound to Redis broker & backend
redis_backend = settings.REDIS_URL.replace("/0", "/1") if "/0" in settings.REDIS_URL else settings.REDIS_URL

celery_app = Celery(
    "multi_agent_exam_portal",
    broker=settings.REDIS_URL,
    backend=redis_backend,
    include=["app.pipeline.tasks"]
)

# Enforce production engineering configurations
celery_app.conf.update(
    # Specialized JSON task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Late task acknowledgment ensuring task re-queue on worker failure
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,

    # Explicit result expiration (1 hour = 3600s) to prevent Redis memory bloat
    result_expires=3600,

    # Task execution hard & soft time limits
    task_time_limit=60,
    task_soft_time_limit=45,

    # Worker connection retries on startup
    broker_connection_retry_on_startup=True
)

logger.info(f"Celery application initialized with Broker: {settings.REDIS_URL}")

if __name__ == "__main__":
    celery_app.start()
