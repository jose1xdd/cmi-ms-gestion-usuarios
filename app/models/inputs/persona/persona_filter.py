from typing import Optional
from pydantic import BaseModel

class PersonaFilter(BaseModel):
    id: Optional[str] = None
    tipoDocumento: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    sexo: Optional[str] = None
    idFamilia: Optional[int] = None
    idParcialidad: Optional[int] = None
