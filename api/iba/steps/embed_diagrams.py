import requests
from api.iba.state import IBAState
from api.config import get_settings
from api.utils.emitter import emit_iba_event

settings = get_settings()

DIAGRAM_SUGGESTIONS = {
    "application": ["context", "sequence", "erd", "use_case"],
    "data_pipeline": ["dag", "lineage", "partitioning_scheme", "checkpoint_flow"],
}

def embed_system_diagrams(state: IBAState) -> IBAState:
    project_id = state.project_id
    paradigm = state.paradigm

    emit_iba_event(
        project_id=project_id,
        node="embed_diagrams",
        event_type="iba.node.started",
        status="started",
        metadata={"paradigm": paradigm}
    )

    diagram_types = DIAGRAM_SUGGESTIONS.get(paradigm, [])
    request_body = {
        "project_id": project_id,
        "diagram_types": diagram_types
    }

    try:
        response = requests.post(
            f"{settings.VBA_API_URL}/vba/generate",
            json=request_body,
            timeout=60
        )
        response.raise_for_status()
        diagrams = response.json().get("diagrams", [])

        state.diagrams = {d["diagram_type"]: d["code"] for d in diagrams}

        emit_iba_event(
            project_id=project_id,
            node="embed_diagrams",
            event_type="iba.node.completed",
            status="completed",
            metadata={"diagram_types": list(state.diagrams.keys())}
        )
    except Exception as e:
        emit_iba_event(
            project_id=project_id,
            node="embed_diagrams",
            event_type="iba.node.error",
            status="failed",
            metadata={"error": str(e)}
        )
        state.diagrams = {}

    return state
