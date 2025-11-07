from typing import Optional
from pydantic import BaseModel


class PersonaFilter(BaseModel):
    """
    Filtros opcionales para consultar personas.
    """
    id: Optional[str] = None
    tipoDocumento: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    sexo: Optional[str] = None
    idFamilia: Optional[int] = None
    idParcialidad: Optional[int] = None
    activo: Optional[bool] = None
    fechaDefuncion: Optional[str] = None  # formato 'YYYY-MM-DD' si se usa como filtro

    class Config:
        from_attributes = True
        exclude_none = True
