from abc import ABC
from typing import List, Optional
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.models.outputs.familia.familia_output import FamiliaResumenOut
from app.models.outputs.paginated_response import PaginatedFamilias
from app.persistence.model.familia import Familia
from app.persistence.repository.base_repository.interface.ibase_repository import IBaseRepository


class IFamiliaRepository(IBaseRepository[Familia, int], ABC):
    def bulk_insert(self, familias: List[FamiliaCreate]) -> int:
        pass

    def search_by_representante(self, page: int, page_size: int, query: str) -> PaginatedFamilias:
        pass

    def get_familias_dashboard(self, page: int, page_size: int):
        pass

    def get_miembros_familia(self, id_familia: int, query: Optional[str], page: int, page_size: int):
        pass
    def get_familia_resumen(self, id_familia: int) -> FamiliaResumenOut:
        pass
    def get_estadisticas_generales(self) -> dict:
        pass