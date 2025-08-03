
from typing import List
from pydantic import BaseModel


class AssingFamilia(BaseModel):
    familia_id: int
    personas_id: List[str]

    class Config:
        from_attributes = True  # Para convertir entre SQLAlchemy y Pydantic fácilmente
