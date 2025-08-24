from typing import Optional
from pydantic import BaseModel


class ParcialidadFilter(BaseModel):
    nombre: Optional[str] = None