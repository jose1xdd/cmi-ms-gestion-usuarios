from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from app.persistence.model.enum import EnumDocumento, EnumEscolaridad, EnumParentesco, EnumSexo


class PersonaUpdate(BaseModel):
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
    idFamilia: Optional[int] = None
    idParcialidad: Optional[int] = None
    activo: Optional[Literal[True]] = None
    class Config:
        from_attributes = True  # Para convertir entre SQLAlchemy y Pydantic fácilmente
