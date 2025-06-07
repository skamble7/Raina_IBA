from api.iba.state import IBAState
from api.utils.emitter import emit_iba_event
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from api.config import get_settings
from typing import List, Dict


settings = get_settings()

CHUNK_PROMPT = ChatPromptTemplate.from_template(
    """
You are a software architect.

Given the following project artifacts and paradigm: "{paradigm}", provide a concise architectural summary of how these should influence system design.

Respond in **Markdown** with headings and bullet points.

## Artifacts
```json
{artifact_chunk}
```
"""
)

FINAL_PROMPT = ChatPromptTemplate.from_template(
    """
You are a senior software architect.

Based on the following architectural insights, write a complete **Architecture Guide** for a "{paradigm}" project.

Include:
1. High-level architectural overview
2. Key components and responsibilities
3. Design patterns and principles
4. Scalability, reliability, maintainability
5. Data or integration flow strategies

Respond in Markdown format.

---

## Architectural Insights
{chunk_insights}
"""
)

def chunk_artifacts(artifacts: dict, max_per_chunk: int = 3) -> List[dict]:
    chunks = []
    for artifact_type, items in artifacts.items():
        for i in range(0, len(items), max_per_chunk):
            chunk = {
                artifact_type: items[i : i + max_per_chunk]
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

        chunk_chain = CHUNK_PROMPT | model | StrOutputParser()
        final_chain = FINAL_PROMPT | model | StrOutputParser()

        chunks = chunk_artifacts(state.artifacts)
        chunk_guides: List[str] = []

        for i, chunk in enumerate(chunks):
            try:
                chunk_text = await chunk_chain.ainvoke({
                    "paradigm": state.paradigm,
                    "artifact_chunk": chunk
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

        final_guide = await final_chain.ainvoke({
            "paradigm": state.paradigm,
            "chunk_insights": "\n\n".join(chunk_guides)
        })

        state.architecture_guide = final_guide

        emit_iba_event(
            project_id=state.project_id,
            node="generate_guide",
            event_type="iba.node.completed",
            status="completed",
            metadata={"output_preview": final_guide[:500]}
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