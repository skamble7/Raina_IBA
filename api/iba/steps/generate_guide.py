
from api.iba.state import IBAState
from api.utils.emitter import emit_iba_event
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from api.config import get_settings
from typing import List, Dict

settings = get_settings()

# Generic prompt for non-entity artifacts
GENERIC_CHUNK_PROMPT = ChatPromptTemplate.from_template(
    """
You are a software architect.

The project follows the paradigm: "{paradigm}".

Below is a list of **{artifact_type}** project artifacts. For this artifact type, describe:

- What this artifact represents
- How it influences architecture and system design
- Design or data flow considerations
- Specific examples if relevant

Respond in **Markdown** using a heading for the artifact type and bullet points for insights.

## {artifact_type} Artifacts
```json
{artifact_chunk}
```
"""
)

FINAL_PROMPT = ChatPromptTemplate.from_template(
    """
You are a senior software architect.

Below is a list of artifact-specific architectural insights with detailed definitions (especially entities). Based on this, write a complete **Architecture Guide** for a "{paradigm}" project.

Include:
1. High-level architectural overview
2. Key components and responsibilities
3. Design patterns and principles based on the selected paradigm
4. Scalability, reliability, maintainability
5. Data or integration flow strategies
6. A dedicated section summarizing key artifacts and referring to their detailed descriptions

Respond in Markdown.

---

## Detailed Artifact Insights
{chunk_insights}
"""
)

def chunk_artifacts(artifacts: dict, max_per_chunk: int = 3) -> List[Dict]:
    chunks = []
    for artifact_type, items in artifacts.items():
        for i in range(0, len(items), max_per_chunk):
            chunk = {
                "artifact_type": artifact_type,
                "artifact_chunk": items[i : i + max_per_chunk]
            }
            chunks.append(chunk)
    return chunks

async def generate_architecture_guide(state: IBAState) -> IBAState:
    emit_iba_event(
        project_id=state.project_id,
        node="generate_guide",
        event_type="iba.node.started",
        status="started",
        metadata={"paradigm": state.paradigm}
    )

    try:
        model = ChatOpenAI(
            temperature=0.3,
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
        )

        generic_chain = GENERIC_CHUNK_PROMPT | model | StrOutputParser()
        final_chain = FINAL_PROMPT | model | StrOutputParser()

        chunks = chunk_artifacts(state.artifacts)
        chunk_guides: List[str] = []

        for i, chunk in enumerate(chunks):
            try:
                artifact_type = chunk["artifact_type"]

                if artifact_type == "entities":
                    entity_md_blocks = []
                    for entity in chunk["artifact_chunk"]:
                        name = entity.get("name", "Unknown")
                        description = entity.get("description", "")
                        attributes = entity.get("attributes", [])

                        table_rows = [
                            f"| {attr.get('name')} | {attr.get('type')} | {attr.get('description')} |"
                            for attr in attributes
                        ]
                        table_md = "\n".join([
                            f"### Entity: {name}",
                            f"_Description_: {description}\n",
                            "| Name | Type | Description |",
                            "|------|------|-------------|",
                            *table_rows,
                            ""
                        ])
                        entity_md_blocks.append(table_md)

                    chunk_text = "\n".join(entity_md_blocks)
                    chunk_guides.append("## Entity Definitions\n" + chunk_text)

                else:
                    chunk_text = await generic_chain.ainvoke({
                        "paradigm": state.paradigm,
                        "artifact_type": artifact_type,
                        "artifact_chunk": chunk["artifact_chunk"]
                    })
                    chunk_guides.append(chunk_text)

            except Exception as ce:
                emit_iba_event(
                    project_id=state.project_id,
                    node="generate_guide",
                    event_type="iba.chunk.failed",
                    status="warning",
                    metadata={"chunk_index": i, "error": str(ce)}
                )

        full_chunk_insights = "\n\n".join(chunk_guides)

        final_guide = await final_chain.ainvoke({
            "paradigm": state.paradigm,
            "chunk_insights": full_chunk_insights
        })

        # Hybrid approach: include final guide + full chunk insights as appendix
        state.architecture_guide = (
            final_guide.strip()
            + "\n\n---\n\n"
            + "## Detailed Detailed Artifact Definitions\n\n"
            + full_chunk_insights
        )

        emit_iba_event(
            project_id=state.project_id,
            node="generate_guide",
            event_type="iba.node.completed",
            status="completed",
            metadata={"output_preview": state.architecture_guide[:500]}
        )

    except Exception as e:
        emit_iba_event(
            project_id=state.project_id,
            node="generate_guide",
            event_type="iba.node.error",
            status="failed",
            metadata={"error": str(e)}
        )
        state.architecture_guide = "# Architecture Guide\n\n_An error occurred during generation._"

    return state
