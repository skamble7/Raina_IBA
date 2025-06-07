from typing import Optional, Dict, List
from pydantic import BaseModel

class IBAState(BaseModel):
    project_id: str
    paradigm: Optional[str] = None  # ✅ Optional
    artifacts: Optional[Dict[str, List[Dict]]] = None  # ✅ Optional

    # Intermediates and outputs
    architecture_guide: Optional[str] = None
    diagrams: Optional[Dict[str, str]] = None
    adrs: Optional[List[Dict]] = None
    blueprint_markdown: Optional[str] = None
    exported_files: Optional[Dict[str, str]] = None
