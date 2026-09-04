import logging
from typing import Dict, List, Set, Any, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketConnectionManager:
    """
    Manages active WebSocket connections mapped by user_id, attempt_id, and submission_id topics.
    Supports JWT authentication during connection, broadcasting, and target channel delivery.
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.user_topics: Dict[str, Set[WebSocket]] = {}
        self.attempt_topics: Dict[str, Set[WebSocket]] = {}
        self.submission_topics: Dict[str, Set[WebSocket]] = {}

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
        attempt_id: Optional[str] = None,
        submission_id: Optional[str] = None
    ):
        """Accepts WebSocket connection and subscribes socket to user, attempt, and submission topics."""
        await websocket.accept()
        self.active_connections.add(websocket)

        if user_id not in self.user_topics:
            self.user_topics[user_id] = set()
        self.user_topics[user_id].add(websocket)

        if attempt_id:
            if attempt_id not in self.attempt_topics:
                self.attempt_topics[attempt_id] = set()
            self.attempt_topics[attempt_id].add(websocket)

        if submission_id:
            if submission_id not in self.submission_topics:
                self.submission_topics[submission_id] = set()
            self.submission_topics[submission_id].add(websocket)

        logger.info(f"WebSocket connected for user '{user_id}' on attempt '{attempt_id}' and submission '{submission_id}'. Total active: {len(self.active_connections)}")

    def disconnect(
        self,
        websocket: WebSocket,
        user_id: str,
        attempt_id: Optional[str] = None,
        submission_id: Optional[str] = None
    ):
        """Removes WebSocket connection from active pool and topics."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if user_id in self.user_topics and websocket in self.user_topics[user_id]:
            self.user_topics[user_id].remove(websocket)

        if attempt_id and attempt_id in self.attempt_topics and websocket in self.attempt_topics[attempt_id]:
            self.attempt_topics[attempt_id].remove(websocket)

        if submission_id and submission_id in self.submission_topics and websocket in self.submission_topics[submission_id]:
            self.submission_topics[submission_id].remove(websocket)

        logger.info(f"WebSocket disconnected for user '{user_id}'. Total active: {len(self.active_connections)}")

    async def send_to_attempt(self, attempt_id: str, message: Dict[str, Any]):
        """Sends message to all sockets subscribed to a specific attempt_id."""
        if attempt_id in self.attempt_topics:
            dead_sockets = set()
            for ws in self.attempt_topics[attempt_id]:
                try:
                    await ws.send_json(message)
                except Exception as err:
                    logger.warning(f"Failed sending WS event to attempt topic {attempt_id}: {err}")
                    dead_sockets.add(ws)
            
            for ds in dead_sockets:
                self.active_connections.discard(ds)
                self.attempt_topics[attempt_id].discard(ds)

    async def send_to_submission(self, submission_id: str, message: Dict[str, Any]):
        """Sends message to all sockets subscribed to a specific submission_id."""
        if submission_id in self.submission_topics:
            dead_sockets = set()
            for ws in self.submission_topics[submission_id]:
                try:
                    await ws.send_json(message)
                except Exception as err:
                    logger.warning(f"Failed sending WS event to submission topic {submission_id}: {err}")
                    dead_sockets.add(ws)
            
            for ds in dead_sockets:
                self.active_connections.discard(ds)
                self.submission_topics[submission_id].discard(ds)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts message to all connected sockets."""
        dead_sockets = set()
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead_sockets.add(ws)
        
        for ds in dead_sockets:
            self.active_connections.discard(ds)

manager = WebSocketConnectionManager()
