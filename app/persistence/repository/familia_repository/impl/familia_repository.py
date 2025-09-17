from typing import List
from sqlalchemy.orm import Session
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.persistence.model.familia import Familia
from app.persistence.repository.base_repository.impl.base_repository import BaseRepository
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository


class FamiliaRepository(BaseRepository, IFamiliaRepository):
    def __init__(self, db: Session):
        # Llamar al constructor de la clase base
        super().__init__(Familia, db)

    def bulk_insert(self, familias: List[FamiliaCreate]) -> int:
        for familia in familias:
            self.create(
                Familia(integrantes=0, id=familia.idFamilia)
            )
        return len(familias)
