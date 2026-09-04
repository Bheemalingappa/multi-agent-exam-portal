import uuid
from contextvars import ContextVar

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

def get_correlation_id() -> str:
    """Returns the current context correlation ID or generates a new one."""
    cid = correlation_id_ctx.get()
    if not cid:
        cid = str(uuid.uuid4())
        correlation_id_ctx.set(cid)
    return cid

def set_correlation_id(cid: str) -> str:
    """Sets explicit context correlation ID."""
    correlation_id_ctx.set(cid)
    return cid
