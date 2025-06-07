from api.dal.project_map_loader import load_project_artifacts
from api.iba.state import IBAState
from api.utils.emitter import emit_iba_event

def load_artifacts(state: IBAState) -> IBAState:
    emit_iba_event(
        project_id=state.project_id,
        node="load_artifacts",
        event_type="iba.node.started",
        status="started",
        metadata={"project_id": state.project_id}
    )

    try:
        paradigm, artifacts = load_project_artifacts(state.project_id)
        state.paradigm = paradigm
        state.artifacts = artifacts

        emit_iba_event(
            project_id=state.project_id,
            node="load_artifacts",
            event_type="iba.node.completed",
            status="success",
            metadata={"paradigm": paradigm, "artifact_keys": list(artifacts.keys())}
        )
    except Exception as e:
        emit_iba_event(
            project_id=state.project_id,
            node="load_artifacts",
            event_type="iba.node.error",
            status="failed",
            metadata={"error": str(e)}
        )
        state.artifacts = {}
        state.paradigm = "application"

    return state
