
from api.iba.state import IBAState, DiagramObject
from api.utils.emitter import emit_iba_event
from api.utils.embed_system_diagrams import encode_plantuml
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

SYSTEM_DIAGRAM_PROMPT = ChatPromptTemplate.from_template("""
You are a software architect.

Use the following tech stack to generate a PlantUML Component Diagram with:
- Packages for logical groupings (Frontend, Backend, DB, etc.)
- Correct PlantUML syntax only
- Return a valid diagram using [Component] notation inside package {{}}

Tech Stack:
Frontend: {{frontend}}
Backend: {{backend}}
Database: {{database}}
Messaging: {{messaging}}
Orchestration: {{orchestration}}
Data Processing: {{data_processing}}
Storage Layer: {{storage_layer}}
Observability: {{observability}}
Other Tools: {{other_tools}}

Output only valid PlantUML:
```plantuml
@startuml
title {{paradigm}} System Architecture

actor User

package "Frontend" {{
  [{{frontend}}]
}}

package "Backend" {{
  [{{backend}}]
}}

package "Database" {{
  [{{database}}]
}}

package "Messaging" {{
  [{{messaging}}]
}}

package "Orchestration" {{
  [{{orchestration}}]
}}

package "Data Processing" {{
  [{{data_processing}}]
}}

package "Storage Layer" {{
  [{{storage_layer}}]
}}

package "Observability" {{
  [Prometheus]
  [Grafana]
}}

package "Other Tools" {{
  [Docker]
  [Kubernetes]
}}

User --> [{{frontend}}]
[{{frontend}}] --> [{{backend}}] : Sends requests
[{{backend}}] --> [{{database}}] : Reads/Writes
[{{backend}}] --> [{{messaging}}] : Publishes
[{{messaging}}] --> [{{orchestration}}] : Sends jobs
[{{orchestration}}] --> [{{data_processing}}] : Orchestrates
[{{data_processing}}] --> [{{storage_layer}}] : Stores results
[Prometheus] --> [Grafana] : Visualizes
@enduml
```

No explanation.
""")

def plantuml_image_url(code: str) -> str:
    from api.config import get_settings
    return f"{get_settings().PLANTUML_SERVER_URL}/svg/{encode_plantuml(code)}"

def generate_system_diagram(state: IBAState) -> IBAState:
    emit_iba_event(
        project_id=state.project_id,
        node="generate_system_diagram",
        event_type="iba.node.started",
        status="started",
        metadata={},
    )

    try:
        if not state.selected_tech_stack:
            raise ValueError("Missing tech stack selection.")

        stack = state.selected_tech_stack
        paradigm = (state.paradigm or "application").replace('"', '').strip()

        prompt = SYSTEM_DIAGRAM_PROMPT.format_messages(
            paradigm=paradigm,
            frontend=stack.frontend,
            backend=stack.backend,
            database=stack.database,
            messaging=stack.messaging,
            orchestration=stack.orchestration,
            data_processing=stack.data_processing,
            storage_layer=stack.storage_layer,
            observability=", ".join(stack.observability_stack or []),
            other_tools=", ".join(stack.other_tools or []),
        )

        llm = ChatOpenAI(model="gpt-4", temperature=0)
        result = llm.invoke(prompt).content.strip()

        if "```plantuml" in result:
            result = result.split("```plantuml")[1].split("```")[0].strip()

        lines = result.splitlines()
        if "@startuml" in lines[0]:
            lines.insert(1, f"title {paradigm} System Architecture")
        result = "\n".join(lines)

        if not result.startswith("@startuml") or not result.endswith("@enduml"):
            raise ValueError("Generated diagram is not valid PlantUML")

        state.system_diagram = DiagramObject(
            code=result, image_url=plantuml_image_url(result)
        )

        emit_iba_event(
            project_id=state.project_id,
            node="generate_system_diagram",
            event_type="iba.node.completed",
            status="completed",
            metadata={"length": len(result)},
        )

    except Exception as e:
        logger.exception("Error generating system diagram")
        emit_iba_event(
            project_id=state.project_id,
            node="generate_system_diagram",
            event_type="iba.node.error",
            status="failed",
            metadata={"error": str(e)},
        )

    return state
