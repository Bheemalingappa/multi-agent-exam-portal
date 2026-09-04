import uuid
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.database.models import ExamAttempt, SubmissionFact, User
from app.core.security import decode_access_token
from app.realtime.connection_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Real-Time WebSockets"])

def authenticate_ws_token(token: Optional[str], db: Session) -> Optional[User]:
    """Validates JWT token query param for WebSocket handshake."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        return None
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    return user if (user and user.is_active) else None

@router.websocket("/ws/exams/{attempt_id}")
async def websocket_exam_attempt(
    websocket: WebSocket,
    attempt_id: str,
    token: Optional[str] = Query(None)
):
    """
    Real-time WebSocket connection for live exam attempts.
    Receives live timer warnings, exam start events, autosave confirmations, and anomaly updates.
    """
    db = SessionLocal()
    try:
        user = authenticate_ws_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            a_uuid = uuid.UUID(attempt_id)
        except ValueError:
            await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
            return

        attempt = db.query(ExamAttempt).filter(ExamAttempt.id == a_uuid).first()
        if not attempt:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # IDOR Ownership Check
        if user.role == "candidate" and attempt.candidate_id != user.id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await manager.connect(websocket, user_id=str(user.id), attempt_id=attempt_id)

        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type", "").upper()

                # Client message validation: Reject client attempts to forge server-only events
                if msg_type in ["FINAL_SCORE", "EXAM_EXPIRED", "ANOMALY_SCORE", "EVALUATION_COMPLETED"]:
                    await websocket.send_json({"type": "ERROR", "detail": "Forbidden: Client cannot publish server-only event types."})
                elif msg_type == "PING":
                    await websocket.send_json({"type": "PONG"})
                else:
                    await websocket.send_json({"type": "ACK", "message": "Client message received."})

        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id=str(user.id), attempt_id=attempt_id)

    finally:
        db.close()

@router.websocket("/ws/submissions/{submission_id}")
async def websocket_submission_evaluation(
    websocket: WebSocket,
    submission_id: str,
    token: Optional[str] = Query(None)
):
    """
    Real-time WebSocket connection for live submission evaluation pipeline progress.
    Receives stage changes (0% -> 100%), AST pre-screen status, A2A consensus logs, and final scores.
    """
    db = SessionLocal()
    try:
        user = authenticate_ws_token(token, db)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            s_uuid = uuid.UUID(submission_id)
        except ValueError:
            await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
            return

        submission = db.query(SubmissionFact).filter(SubmissionFact.submission_id == s_uuid).first()
        if not submission:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        if user.role == "candidate" and submission.candidate_id != user.id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await manager.connect(websocket, user_id=str(user.id), submission_id=submission_id)

        try:
            while True:
                data = await websocket.receive_json()
                msg_type = data.get("type", "").upper()

                if msg_type == "PING":
                    await websocket.send_json({"type": "PONG"})
                else:
                    await websocket.send_json({"type": "ACK", "message": "Client message received."})

        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id=str(user.id), submission_id=submission_id)

    finally:
        db.close()
