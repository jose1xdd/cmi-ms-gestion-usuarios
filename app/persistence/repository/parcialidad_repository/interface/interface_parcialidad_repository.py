from abc import ABC, abstractmethod
from typing import Any, Dict
from app.models.outputs.paginated_response import PaginatedParcialidad
from app.persistence.model.parcialidad import Parcialidad
from app.persistence.repository.base_repository.interface.ibase_repository import IBaseRepository


class IParcialiadRepository(IBaseRepository[Parcialidad, int], ABC):

    @abstractmethod
    def find_by_name(self, name: str) -> Parcialidad:
        pass

    @abstractmethod
    def find_by_params(self, page: int, page_size: int, filters: Dict[str, Any]) -> PaginatedParcialidad:
        pass

    @abstractmethod
    def bulk_insert(self, parcialidades) -> int:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Parcialidad:
        pass
