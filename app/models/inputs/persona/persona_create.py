from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from app.persistence.model.enum import EnumDocumento, EnumEscolaridad, EnumParentesco, EnumSexo


class PersonaCreate(BaseModel):
    """
    Modelo de entrada para crear una Persona.
    """
    id: str = Field(max_length=36, description="Documento o identificador único")
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
    idFamilia: int = Field(default=None, description="ID de la familia a la que pertenece")
    idParcialidad: int = Field(default=None, description="ID de la parcialidad")
    fechaDefuncion: Optional[date] = Field(default=None, description="Fecha de defunción si la persona ha fallecido")

    class Config:
        from_attributes = True
        exclude_none = True
