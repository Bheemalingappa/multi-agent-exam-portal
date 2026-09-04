import json
import logging
from typing import Dict, Any, Optional
import redis
from app.core.config import settings
from app.schemas.events import RealtimeEventSchema

logger = logging.getLogger(__name__)

CHANNEL_NAME = "exam_portal_events"

class RedisEventPublisher:
    """
    Publishes real-time pipeline and proctoring events to Redis Pub/Sub channel.
    Allows decoupled Celery workers to broadcast live events to FastAPI WebSockets.
    """

    @staticmethod
    def publish_event(
        event_type: str,
        payload: Dict[str, Any],
        attempt_id: Optional[str] = None,
        submission_id: Optional[str] = None,
        progress: Optional[int] = None
    ) -> bool:
        """Publishes structured RealtimeEventSchema payload to Redis Pub/Sub channel."""
        try:
            r = redis.Redis.from_url(settings.REDIS_BROKER_URL, socket_timeout=2)
            event_obj = RealtimeEventSchema(
                event_type=event_type,
                attempt_id=attempt_id,
                submission_id=submission_id,
                progress=progress,
                payload=payload
            )
            raw_data = json.dumps(event_obj.dict())
            r.publish(CHANNEL_NAME, raw_data)
            logger.info(f"Published Redis Event '{event_type}' for submission '{submission_id}' (Progress: {progress}%)")
            return True
        except Exception as err:
            logger.warning(f"Failed publishing Redis Pub/Sub event '{event_type}': {err}")
            return False
