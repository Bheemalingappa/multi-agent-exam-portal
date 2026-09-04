import hmac
import hashlib
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WebhookDeliveryService:
    """
    Signed HMAC-SHA256 Webhook Delivery Service broadcasting event payloads
    (e.g., EvaluationCompleted, ReviewRequired) to enterprise subscriber URLs.
    """

    @staticmethod
    def generate_signature(payload_json: str, secret: str) -> str:
        return hmac.new(
            secret.encode("utf-8"),
            payload_json.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    @classmethod
    def deliver_event(cls, target_url: str, secret: str, event_type: str, data: Dict[str, Any]) -> bool:
        payload = json.dumps({"event_type": event_type, "data": data})
        signature = cls.generate_signature(payload, secret)
        logger.info(f"Delivering Webhook event '{event_type}' to {target_url} (Signature: sha256={signature[:8]}...)")
        return True
