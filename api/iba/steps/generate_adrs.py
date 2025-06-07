from api.iba.state import IBAState
from api.utils.emitter import emit_iba_event
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List, Dict
from api.config import get_settings

settings = get_settings()

class ADR(BaseModel):
    title: str
    context: str
    decision: str
    alternatives: str
    rationale: str

class ADRList(BaseModel):
    adrs: List[ADR]

parser = PydanticOutputParser(pydantic_object=ADRList)

CHUNK_PROMPT = ChatPromptTemplate.from_template("""
You are an experienced software architect.

Based on the following **architecture guide** and **a subset of project artifacts**, generate 1–3 Architectural Decision Records (ADRs).

Each ADR must include:
- title
- context
- decision
- alternatives considered
- rationale

Respond strictly in this format:
{format_instructions}

---

# Architecture Guide:
{architecture_guide}

# Artifacts:
{subset_artifacts}
""")

def chunk_artifacts_globally(artifacts: Dict[str, List[Dict]], max_items: int = 8) -> List[Dict[str, List[Dict]]]:
    flat_items = []
    for artifact_type, items in artifacts.items():
        for item in items:
            flat_items.append((artifact_type, item))

    chunks = []
    current_chunk: Dict[str, List[Dict]] = {}

    for artifact_type, item in flat_items:
        if artifact_type not in current_chunk:
            current_chunk[artifact_type] = []
        current_chunk[artifact_type].append(item)

        total_items = sum(len(v) for v in current_chunk.values())
        if total_items >= max_items:
            chunks.append(current_chunk)
            current_chunk = {}

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

async def generate_adrs(state: IBAState) -> IBAState:
    emit_iba_event(
        project_id=state.project_id,
        node="generate_adrs",
        event_type="iba.node.started",
        status="started",
        metadata={"input_preview": state.architecture_guide[:300]}
    )

    llm = ChatOpenAI(
        temperature=0.3,
        model="gpt-3.5-turbo",  # ✅ Use cost-effective model
        openai_api_key=settings.openai_api_key,
    )

    chunks = chunk_artifacts_globally(state.artifacts, max_items=8)
    all_adrs = []

    for i, chunk in enumerate(chunks):
        try:
            messages = CHUNK_PROMPT.format_messages(
                format_instructions=parser.get_format_instructions(),
                architecture_guide=state.architecture_guide or "N/A",
                subset_artifacts=chunk
            )
            result = await llm.ainvoke(messages)
            parsed = parser.parse(result.content)
            all_adrs.extend([adr.model_dump() for adr in parsed.adrs])
        except Exception as e:
            emit_iba_event(
                project_id=state.project_id,
                node="generate_adrs",
                event_type="iba.chunk.failed",
                status="warning",
                metadata={"chunk_index": i, "error": str(e)}
            )

    state.adrs = all_adrs

    emit_iba_event(
        project_id=state.project_id,
        node="generate_adrs",
        event_type="iba.node.completed",
        status="completed",
        metadata={"count": len(all_adrs)}
    )

    return state
