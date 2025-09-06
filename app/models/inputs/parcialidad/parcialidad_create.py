from pydantic import BaseModel


class ParcialidadCreate(BaseModel):
    nombre_parcialidad: str
