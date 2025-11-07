from typing import Optional
from pydantic import BaseModel, Field
from datetime import date
from app.persistence.model.enum import EnumDocumento, EnumEscolaridad, EnumParentesco, EnumSexo


class PersonaUpdate(BaseModel):
    """
    Modelo de actualización parcial de Persona.
    Solo los campos no nulos se actualizarán.
    """
    tipoDocumento: Optional[EnumDocumento] = None
    nombre: Optional[str] = Field(default=None, max_length=50)
    apellido: Optional[str] = Field(default=None, max_length=50)
    fechaNacimiento: Optional[date] = None
    parentesco: Optional[EnumParentesco] = None
    sexo: Optional[EnumSexo] = None
    profesion: Optional[str] = Field(default=None, max_length=100)
    escolaridad: Optional[EnumEscolaridad] = None
    direccion: Optional[str] = Field(default=None, max_length=200)
    telefono: Optional[str] = Field(default=None, max_length=20)
    idParcialidad: Optional[int] = None

    class Config:
        from_attributes = True
        exclude_none = True

class PersonaDefuncion(BaseModel):
    id: str
    fechaDefuncion: date

    class Config:
        from_attributes = True