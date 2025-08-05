from typing import List
from pydantic import BaseModel

from app.models.outputs.familia.familia_output import FamiliaOut
from app.models.outputs.persona.persona_output import PersonaOut

class PaginatedPersonas(BaseModel):
    total_items: int
    current_page: int
    total_pages: int
    items: List[PersonaOut]

class PaginatedFamilias(BaseModel):
    total_items: int
    current_page: int
    total_pages: int
    items: List[FamiliaOut]