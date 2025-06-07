from pymongo import MongoClient
from api.iba.state import IBAState, DiagramObject
from api.config import get_settings
from api.utils.emitter import emit_iba_event
from api.utils.embed_system_diagrams import encode_plantuml
from collections import defaultdict

settings = get_settings()

client = MongoClient(settings.mongodb_uri)
db = client["Raina"]

DIAGRAM_SUGGESTIONS = {
    "application": ["context", "sequence", "erd", "use_case"],
    "data_pipeline": ["dag", "class", "target_data_model"],
}

def plantuml_image_url(code: str) -> str:
    return f"{settings.PLANTUML_SERVER_URL}/svg/{encode_plantuml(code)}"

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

    try:
        raw_diagrams = list(db["diagrams"].find({"project_id": project_id}))
        if not raw_diagrams:
            raise ValueError("No diagrams found for this project.")

        allowed_types = DIAGRAM_SUGGESTIONS.get(paradigm, [])
        filtered = [d for d in raw_diagrams if d.get("diagram_type") in allowed_types]

        diagram_map = defaultdict(list)
        for d in filtered:
            diagram_map[d["diagram_type"]].append(
                DiagramObject(
                    code=d["code"],
                    image_url=plantuml_image_url(d["code"])
                )
            )

        state.diagrams = dict(diagram_map)

        emit_iba_event(
            project_id=project_id,
            node="embed_diagrams",
            event_type="iba.node.completed",
            status="completed",
            metadata={"count": sum(len(v) for v in state.diagrams.values())}
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
