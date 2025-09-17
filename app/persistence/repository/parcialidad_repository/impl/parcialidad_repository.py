from typing import Any, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.persistence.model.parcialidad import Parcialidad
from app.persistence.repository.base_repository.impl.base_repository import BaseRepository
from app.persistence.repository.parcialidad_repository.interface.interface_parcialidad_repository import IParcialiadRepository


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
            self.apply_filters(self.db, Parcialidad, filters)
        )
        return self.paginate(page, page_size, query)

    def bulk_insert(self, parcialidades) -> int:
        for parcialidad in parcialidades:
            self.create(parcialidad)
        return len(parcialidades)

    def find_by_name(self, name: str) -> Parcialidad:
        # Buscar coincidencias parciales
        return (
            self.db.query(Parcialidad)
            .filter(Parcialidad.nombre.ilike(f"%{name}%"))
            # Ordenamos por la posición donde aparece el texto y la longitud del nombre
            .order_by(func.locate(name, Parcialidad.nombre), func.length(Parcialidad.nombre))
            .first()
        )
