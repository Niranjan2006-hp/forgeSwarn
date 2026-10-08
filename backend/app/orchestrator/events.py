import asyncio
import json
import logging
from typing import Dict, List, Any, AsyncGenerator
from datetime import datetime, timezone

logger = logging.getLogger("forgeswarm.events")

class EventBroadcaster:
    def __init__(self):
        # project_id -> list of asyncio.Queue
        self._listeners: Dict[str, List[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, project_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        queue = asyncio.Queue()
        async with self._lock:
            if project_id not in self._listeners:
                self._listeners[project_id] = []
            self._listeners[project_id].append(queue)
            
        try:
            while True:
                data = await queue.get()
                yield data
        except asyncio.CancelledError:
            pass
        finally:
            async with self._lock:
                if project_id in self._listeners and queue in self._listeners[project_id]:
                    self._listeners[project_id].remove(queue)
                    if not self._listeners[project_id]:
                        del self._listeners[project_id]

    async def publish(self, project_id: str, event_type: str, source: str, message: str, details: Dict[str, Any] = None, level: str = "INFO"):
        event_payload = {
            "project_id": project_id,
            "event_type": event_type,
            "source": source,
            "message": message,
            "details": details or {},
            "level": level,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        async with self._lock:
            queues = list(self._listeners.get(project_id, []))
            
        for q in queues:
            try:
                q.put_nowait(event_payload)
            except Exception as e:
                logger.debug(f"Failed to deliver event to queue: {e}")

event_broadcaster = EventBroadcaster()
