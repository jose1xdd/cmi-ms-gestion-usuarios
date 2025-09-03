from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.models.inputs.persona.persona_create import PersonaCreate
from app.models.outputs.paginated_response import PaginatedPersonas
from app.models.outputs.persona.persona_output import PersonaOut
from app.persistence.model.persona import Persona
from app.persistence.repository.base_repository.interface.ibase_repository import IBaseRepository


class IPersonaRepository(IBaseRepository[Persona, str], ABC):
    @abstractmethod
    def find_familia_members(self, id: int) -> int:
        pass

    @abstractmethod
    def find_all_personas(self, page: int, page_size: int, filters: Dict[str, Any]) -> PaginatedPersonas:
        pass

    @abstractmethod
    def bulk_insert(self, personas: List[PersonaCreate]) -> int:
        pass
