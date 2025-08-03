from typing import List, Optional
from pydantic import BaseModel

from app.models.outputs.familia_output import FamiliaOut
from app.models.outputs.persona_output import PersonaOut

class PaginatedPersonas(BaseModel):
    total_items: int
    current_page: int
    page_size: int
    items: List[PersonaOut]

class PaginatedFamilias(BaseModel):
    total_items: int
    current_page: int
    page_size: int
    items: List[FamiliaOut]