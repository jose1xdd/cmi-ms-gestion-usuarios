from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from app.persistence.model.enum import EnumDocumento, EnumEscolaridad, EnumParentesco, EnumSexo


class PersonaCreate(BaseModel):
    id: str = Field(max_length=20)
    tipoDocumento: EnumDocumento
    nombre: str = Field(max_length=50)
    apellido: str = Field(max_length=50)
    fechaNacimiento: date
    parentesco: EnumParentesco
    sexo: EnumSexo
    profesion: Optional[str] = Field(default=None, max_length=100)
    escolaridad: EnumEscolaridad
    direccion: str = Field(max_length=200)
    telefono: str = Field(max_length=20)
    idFamilia: int
    idParcialidad: int

    class Config:
        from_attributes = True  # Para convertir entre SQLAlchemy y Pydantic fácilmente
