from pydantic import BaseModel

class FamiliaOut(BaseModel):
    id: int
    integrantes: int

    class Config:
        from_attributes = True  # Compatible con SQLAlchemy
