from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.iba.graph import build_iba_graph
from api.iba.state import IBAState
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class RunIBARequest(BaseModel):
    project_id: str

@router.post("/iba/run")
async def run_iba(request: RunIBARequest):
    try:
        # Build the IBA graph
        graph = build_iba_graph()

        # Initial LangGraph state
        initial_state = IBAState(project_id=request.project_id)

        logger.info(f"[IBA] Running implementation blueprint agent for project {request.project_id}")

        # Run the graph and rehydrate final state into IBAState
        result = await graph.ainvoke(initial_state)
        final_state = IBAState(**result)

        return {
            "project_id": final_state.project_id,
            "paradigm": final_state.paradigm,
            "blueprint_markdown": final_state.blueprint_markdown,
            "diagrams": final_state.diagrams,
            "adrs": final_state.adrs,
            "file_info": final_state.exported_files,
        }

    except Exception as e:
        logger.exception(f"[IBA] Agent failed for project {request.project_id}")
        raise HTTPException(status_code=500, detail=f"IBA agent execution failed: {str(e)}")
