# 📁 api/utils/lia_event_emitter.py

from datetime import datetime
from typing import Optional, Dict
from api.utils.rabbitmq import publish_event
from api.config import get_settings

settings = get_settings()

def emit_iba_event(
    project_id: str,
    node: str,
    event_type: str,  # e.g., 'lia.node.started', 'lia.llm.invoked'
    status: str,
    metadata: Optional[Dict] = None,
):
    """
    Unified LIA event emitter.

    Args:
        project_id (str): ID of the project.
        node (str): Name of the current IBA graph node.
        event_type (str): Event string e.g., "iba.node.started", "iba.llm.invoked"
        status (str): Status e.g., "started", "completed", "error"
        metadata (Optional[Dict]): Additional info (e.g., error message, model name).
    """
    event_payload = {
        "event": event_type,
        "project_id": project_id,
        "node": node,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }

    if metadata:
        event_payload["metadata"] = metadata

    publish_event(
        event_payload,
        routing_key=settings.rabbitmq_routing_key_iba_stream
    )
