from abc import ABC
from typing import List
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.persistence.model.familia import Familia
from app.persistence.repository.base_repository.interface.ibase_repository import IBaseRepository


class IFamiliaRepository(IBaseRepository[Familia, int], ABC):
    def bulk_insert(self, familias: List[FamiliaCreate]) -> int:
        pass
