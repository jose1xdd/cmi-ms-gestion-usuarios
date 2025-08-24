from typing import Any, Dict
from sqlalchemy.orm import Session
from app.persistence.model.parcialidad import Parcialidad
from app.persistence.repository.base_repository.impl.base_repository import BaseRepository
from app.persistence.repository.parcialidad_repository.interface.interface_parcialidad_repository import IParcialiadRepository
from app.utils.util_functions import apply_filters


class ParcialidadRepository(BaseRepository, IParcialiadRepository):
    def __init__(self, db: Session):
        # Llamar al constructor de la clase base
        super().__init__(Parcialidad, db)

    def find_by_name(self, name: str) -> Parcialidad:
        return (
            self.db.query(Parcialidad)
            .filter(Parcialidad.nombre == name)
            .first()
        )

    def find_by_params(self, page: int, page_size: int, filters: Dict[str, Any]):
        query = (
            apply_filters(self.db, Parcialidad, filters)
        )
        return self.paginate(page, page_size, query)
