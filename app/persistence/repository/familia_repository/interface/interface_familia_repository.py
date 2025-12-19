from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.models.outputs.familia.familia_output import FamiliaOut, FamiliaResumenOut
from app.models.outputs.paginated_response import PaginatedFamilias
from app.persistence.model.enum import EnumEstadoFamilia
from app.persistence.model.familia import Familia
from app.persistence.repository.base_repository.interface.ibase_repository import IBaseRepository


class IFamiliaRepository(IBaseRepository[Familia, int], ABC):

    @abstractmethod
    def get_familias_con_lider(
        self,
        page: int,
        page_size: int
    ):
        pass

    @abstractmethod
    def bulk_insert(self, familias: List[FamiliaCreate]) -> int:
        pass

    @abstractmethod
    def search_by_representante(self, page: int, page_size: int, query: str) -> PaginatedFamilias:
        pass

    @abstractmethod
    def get_familias_dashboard(self, page: int, page_size: int):
        pass

    @abstractmethod
    def get_miembros_familia(self, id_familia: int, query: Optional[str], page: int, page_size: int):
        pass

    @abstractmethod
    def get_familia_resumen(self, id_familia: int) -> FamiliaResumenOut:
        pass

    @abstractmethod
    def get_estadisticas_generales(self) -> dict:
        pass

    @abstractmethod
    def search_by_representante(
            self,
            page: int,
            page_size: int,
            query: str,
            parcialidad_id: int | None = None,
            rango_miembros: str | None = None,
            estado: EnumEstadoFamilia | None = None):
        pass
    @abstractmethod
    def get_familia_by_id(self, id_familia: int) -> FamiliaOut:
        pass
