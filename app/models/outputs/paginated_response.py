from typing import List
from pydantic import BaseModel

from app.models.outputs.familia.familia_output import FamiliaDataLeader, FamiliaOut
from app.models.outputs.parcialidad.parcialidad_output import ParcialidadOut
from app.models.outputs.persona.persona_output import PersonaFamiliaOut, PersonaOut

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

class PaginatedDataLeader(BaseModel):
    total_items: int
    current_page: int
    total_pages: int
    items: List[FamiliaDataLeader]

class PaginatedParcialidad(BaseModel):
    total_items: int
    current_page: int
    total_pages: int
    items: List[ParcialidadOut]

class PaginatedPersonasFamilia(BaseModel):
    total_items: int
    total_pages: int
    current_page: int
    items: List[PersonaFamiliaOut]

    class Config:
        from_attributes = True