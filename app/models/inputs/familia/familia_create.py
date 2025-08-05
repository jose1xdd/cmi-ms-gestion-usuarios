from typing import Optional
from pydantic import BaseModel


class FamiliaCreate(BaseModel):
    idFamilia: Optional[int] = None