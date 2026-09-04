from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import AuditEventFact, User
from app.api.auth import get_current_user

router = APIRouter(prefix="/audit", tags=["Compliance Audit Trail"])

class AuditEventResponseSchema(BaseModel):
    id: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str
    created_at: str

@router.get("/events", response_model=List[AuditEventResponseSchema])
def get_audit_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Only platform admins can view compliance audit trails.")

    events = db.query(AuditEventFact).order_by(AuditEventFact.created_at.desc()).limit(100).all()
    return [
        AuditEventResponseSchema(
            id=str(e.id),
            actor_id=str(e.actor_id or ""),
            action=e.action,
            resource_type=e.resource_type,
            resource_id=e.resource_id,
            created_at=e.created_at.isoformat()
        )
        for e in events
    ]
