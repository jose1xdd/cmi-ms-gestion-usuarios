from pydantic import BaseModel
from typing import List, Optional, Literal


class ErrorPersonaOut(BaseModel):
    fila: int
    id: Optional[str] = None
    mensaje: str


class CargaMasivaResponse(BaseModel):
    status: Literal["ok", "error"]
    insertados: int = 0
    total_procesados: int = 0
    errores: List[ErrorPersonaOut] = []
