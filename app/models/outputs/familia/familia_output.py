from pydantic import BaseModel
from typing import Optional
from app.persistence.model.enum import EnumEstadoFamilia, EnumParentesco
from app.models.outputs.persona.persona_output import PersonaOut  # si quieres incluir el representante completo

class FamiliaOut(BaseModel):
    id: int
    representante_id: Optional[str]
    estado: EnumEstadoFamilia
    representante: Optional[PersonaOut] = None

    class Config:
        from_attributes = True
        exclude_none = True

class FamiliaDataLeader(BaseModel):
    id: int
    lider_nombre: str
    lider_apellido: str
    cedula: str
    parcialidad: Optional[str]
    miembros: int
    estado: EnumEstadoFamilia

    class Config:
        from_attributes = True
        exclude_none = True
        
class FamiliaResumenOut(BaseModel):
    id: int
    lider_familia: Optional[str]
    parcialidad: Optional[str]
    total_miembros: int
    miembros_activos: int
    defunciones: int

    class Config:
        from_attributes = True