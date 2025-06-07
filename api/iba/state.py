from pydantic import BaseModel, Field
from typing import Dict, Optional, List

class DiagramObject(BaseModel):
    code: str
    image_url: Optional[str] = None

class IBAState(BaseModel):
    project_id: str
    architecture_guide: Optional[str] = None
    adrs: Optional[List[dict]] = None
    exported_files: Optional[Dict[str, str]] = None
    blueprint_markdown: Optional[str] = None
    paradigm: Optional[str] = None
    artifacts: Optional[dict] = None

    diagrams: Optional[Dict[str, List[DiagramObject]]] = None
