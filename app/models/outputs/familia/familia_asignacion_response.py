from typing import List
from pydantic import BaseModel


class AsignacionFamiliaResponse(BaseModel):
    familia_id: int
    personas_asignadas: List[str]
    personas_no_encontradas: List[str]
    total_asignadas: int
    total_no_encontradas: int