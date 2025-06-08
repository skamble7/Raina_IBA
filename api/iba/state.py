from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Union

class DiagramObject(BaseModel):
    code: str
    image_url: Optional[str] = None

class SelectedTechStack(BaseModel):
    frontend: str
    backend: str
    database: str
    messaging: str
    orchestration: str
    data_processing: str
    storage_layer: str
    observability_stack: List[str]
    other_tools: List[str]
    reasoning: Optional[str] = None

class IBAState(BaseModel):
    project_id: str
    architecture_guide: Optional[str] = None
    adrs: Optional[List[dict]] = None
    exported_files: Optional[Dict[str, str]] = None
    blueprint_markdown: Optional[str] = None
    paradigm: Optional[str] = None
    artifacts: Optional[dict] = None
    diagrams: Optional[Dict[str, List[DiagramObject]]] = None

    # 🆕 Added fields
    selected_tech_stack: Optional[SelectedTechStack] = None
    tech_stack_guidance: Optional[str] = None
