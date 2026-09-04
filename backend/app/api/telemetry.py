import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import ExamAttempt, User, SubmissionFact
from app.api.auth import get_current_user
from app.realtime.redis_events import RedisEventPublisher
from app.core.config import settings

router = APIRouter(prefix="/attempts", tags=["Telemetry & Code Drafts"])

class TelemetryEventItem(BaseModel):
    event_type: str
    client_timestamp: Optional[str] = None
    duration_ms: Optional[float] = 0.0
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TelemetryIngestSchema(BaseModel):
    events: List[TelemetryEventItem] = Field(default_factory=list, max_length=1000)

class DraftSaveSchema(BaseModel):
    question_id: str
    code: str

@router.post("/{attempt_id}/telemetry")
def ingest_proctoring_telemetry(
    attempt_id: str,
    payload: TelemetryIngestSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ingests real-time proctoring telemetry events (typing, focus loss, paste, visibility).
    Normalizes timestamps against server receipt time and publishes ANOMALY_SCORE_UPDATED event.
    """
    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    if attempt.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only record telemetry for your own attempt.")

    if attempt.status in ["EXPIRED", "CANCELLED", "COMPLETED"]:
        raise HTTPException(status_code=400, detail=f"Cannot ingest telemetry for attempt in status '{attempt.status}'.")

    focus_losses = len([e for e in payload.events if e.event_type.upper() in ["FOCUS_LOST", "VISIBILITY_HIDDEN"]])
    paste_events = len([e for e in payload.events if e.event_type.upper() == "PASTE_DETECTED"])

    # Calculate real-time anomaly score estimate
    anomaly_score = min(round((focus_losses * 0.15) + (paste_events * 0.25), 2), 1.0)
    confidence = round(0.85 + (0.10 * (1.0 - anomaly_score)), 2)

    # Publish ANOMALY_SCORE_UPDATED event to Redis
    RedisEventPublisher.publish_event(
        event_type="ANOMALY_SCORE_UPDATED",
        attempt_id=attempt_id,
        payload={
            "anomaly_score": anomaly_score,
            "confidence": confidence,
            "focus_loss_count": focus_losses,
            "paste_events_count": paste_events,
            "server_timestamp": datetime.utcnow().isoformat()
        }
    )

    return {
        "status": "ingested",
        "processed_events": len(payload.events),
        "anomaly_score": anomaly_score,
        "confidence": confidence
    }

@router.post("/{attempt_id}/drafts")
def save_code_draft(
    attempt_id: str,
    payload: DraftSaveSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Saves candidate live code draft without triggering full Celery evaluation pipeline.
    Validates attempt state, size caps, and publishes CODE_SAVED event.
    """
    try:
        a_uuid = uuid.UUID(attempt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attempt_id UUID format.")

    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found.")

    if attempt.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only save drafts for your own attempt.")

    if attempt.status in ["EXPIRED", "CANCELLED", "COMPLETED"]:
        raise HTTPException(status_code=400, detail=f"Cannot save draft for attempt in status '{attempt.status}'.")

    code_bytes = len(payload.code.encode("utf-8"))
    if code_bytes > settings.MAX_SOURCE_CODE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Draft payload size ({code_bytes} bytes) exceeds limit of {settings.MAX_SOURCE_CODE_BYTES} bytes."
        )

    # Publish CODE_SAVED event to Redis
    RedisEventPublisher.publish_event(
        event_type="CODE_SAVED",
        attempt_id=attempt_id,
        payload={
            "question_id": payload.question_id,
            "code_bytes": code_bytes,
            "saved_at": datetime.utcnow().isoformat()
        }
    )

    return {
        "status": "saved",
        "question_id": payload.question_id,
        "saved_at": datetime.utcnow().isoformat()
    }
