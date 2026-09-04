import secrets
import hashlib
from typing import Dict, Any, List

class DeveloperAPIKeyService:
    """
    Developer Platform API Key Management Service producing secure, hashed API keys
    with granular permission scopes (exam:read, submission:read, analytics:read).
    """

    @staticmethod
    def generate_api_key(organization_slug: str, scopes: List[str]) -> Dict[str, Any]:
        raw_key = f"mae_live_{secrets.token_urlsafe(32)}"
        hashed_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        key_prefix = raw_key[:12]

        return {
            "raw_key": raw_key,  # Only returned once on creation
            "key_prefix": key_prefix,
            "hashed_key": hashed_key,
            "organization_slug": organization_slug,
            "scopes": scopes
        }
