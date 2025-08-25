from typing import Any, Dict
from sqlalchemy.orm import Session, joinedload
from app.models.outputs.persona.persona_output import PersonaOut
from app.persistence.model.parcialidad import Parcialidad
from app.persistence.model.persona import Persona
from app.persistence.repository.base_repository.impl.base_repository import BaseRepository
from app.persistence.repository.persona_repository.interface.interface_persona_repository import IPersonaRepository



class PersonaRepository(BaseRepository, IPersonaRepository):
    def __init__(self, db: Session):
        super().__init__(Persona, db)

    def find_familia_members(self, id_familia: int) -> int:
        return (
            self.db.query(Persona)
            .filter(Persona.idFamilia == id_familia)
            .count()
        )

    def find_all_personas(self, page: int, page_size: int, filters: Dict[str, Any]):
        query = (
            self.apply_filters(self.db, Persona, filters)
            .outerjoin(Persona.parcialidad)
            .options(joinedload(Persona.parcialidad))
        )
        return self.paginate(page, page_size, query)