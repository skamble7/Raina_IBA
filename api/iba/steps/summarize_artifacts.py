from api.iba.state import IBAState
from api.utils.emitter import emit_iba_event

def summarize_entities(entities: list[dict]) -> str:
    if not entities:
        return "No entities defined."
    summary_lines = []
    for ent in entities:
        name = ent.get("name", "Unnamed")
        attrs = ent.get("attributes", [])
        attr_strs = [f"{a.get('name')}: {a.get('description')}" for a in attrs]
        summary_lines.append(f"**{name}**: " + "; ".join(attr_strs))
    return "\n".join(summary_lines)

def summarize_flows(flows: list[dict]) -> str:
    return "\n".join(f"- {f.get('flow_name', 'Unnamed')} — {f.get('description', '')}" for f in flows) or "No flows defined."

def summarize_stories(stories: list[dict]) -> str:
    return "\n".join(f"- {s.get('summary', 'Unnamed')} — {s.get('description', '')}" for s in stories) or "No stories defined."


def summarize_artifacts(state: IBAState) -> IBAState:
    emit_iba_event(
        project_id=state.project_id,
        node="summarize_artifacts",
        event_type="iba.node.started",
        status="started"
    )

    artifacts = state.artifacts or {}

    state.entity_summary = summarize_entities(artifacts.get("entities", []))
    state.flow_summary = summarize_flows(artifacts.get("flows", []))
    state.story_summary = summarize_stories(artifacts.get("stories", []))

    emit_iba_event(
        project_id=state.project_id,
        node="summarize_artifacts",
        event_type="iba.node.completed",
        status="success",
        metadata={
            "entity_len": len(artifacts.get("entities", [])),
            "flow_len": len(artifacts.get("flows", [])),
            "story_len": len(artifacts.get("stories", [])),
        }
    )
    return state
