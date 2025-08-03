from pydantic import BaseModel
from typing import Optional, Any


class EstadoResponse(BaseModel):
    estado: str
    message: Optional[str]
    data: Optional[Any] = None

    class Config:
        # Esto hace que `data` no aparezca si es None
        exclude_none = True
