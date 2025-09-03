import math
from typing import Generic, TypeVar, Optional, List, Type, Union
from pydantic import BaseModel
from typing import Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta  # tipo de modelos Base

from app.persistence.repository.base_repository.interface.ibase_repository import IBaseRepository

T = TypeVar('T', bound=BaseModel)
M = TypeVar('M')  # Tipo para el modelo SQLAlchemy
ID = TypeVar('ID')


class BaseRepository(IBaseRepository[T, ID], Generic[T, M, ID]):
    def __init__(self, model: Type[M], db: Session):
        self.model = model
        self.db = db

    def _commit_with_handling(self):
        try:
            self.db.flush()
            self.db.commit()
        except:
            self.db.rollback()
            raise

    def _commit_and_refresh(self, db_obj: M):
        try:
            self.db.flush()
            self.db.commit()
            self.db.refresh(db_obj)
        except:
            self.db.rollback()
            raise

    def get(self, id: ID) -> Optional[M]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[M]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: Union[T, M]) -> M:
        if isinstance(obj_in, self.model):
            db_obj = obj_in  # Ya es una instancia SQLAlchemy
        else:
            # Suponemos que es un Pydantic BaseModel
            if hasattr(obj_in, "dict"):
                obj_data = obj_in.dict(exclude_unset=True)
                db_obj = self.model(**obj_data)
            else:
                raise ValueError(
                    "El objeto no es ni instancia del modelo ni un esquema Pydantic.")

        self.db.add(db_obj)
        self._commit_and_refresh(db_obj)
        return db_obj

    def update(self, id: ID, obj_in: Union[BaseModel, M]) -> Optional[M]:
        db_obj = self.get(id)
        if db_obj is None:
            return None

        if isinstance(obj_in, BaseModel):
            obj_data = obj_in.model_dump(exclude_none=True)
        else:
            # Si ya es una instancia de SQLAlchemy, convertimos a dict ignorando atributos internos
            obj_data = {
                key: getattr(obj_in, key)
                for key in vars(obj_in)
                if not key.startswith("_") and hasattr(db_obj, key)
            }

        for key, value in obj_data.items():
            setattr(db_obj, key, value)

        self._commit_and_refresh(db_obj)
        return db_obj

    def delete(self, id: ID) -> bool:
        db_obj = self.get(id)
        if not db_obj:
            return False
        self.db.delete(db_obj)
        self._commit_with_handling()
        return True

    def paginate(self, page: int = 1, page_size: int = 10, query=None) -> dict:

        # Usa la query personalizada o la query base
        query = query or self.db.query(self.model)

        total_items = query.order_by(None).count()
        total_pages = math.ceil(total_items / page_size) if page_size else 1
        skip = (page - 1) * page_size
        items = query.offset(skip).limit(page_size).all()

        return {
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "items": items
        }

    def apply_filters(self,
                      session: Session,
                      model: Type[DeclarativeMeta],
                      filters: Dict[str, Any]
                      ):
        """
        Aplica filtros dinámicos con AND.
        Solo se consideran los filtros enviados en el diccionario.
        """
        query = session.query(model)

        if filters:
            for campo, valor in filters.items():
                if hasattr(model, campo):
                    query = query.filter(getattr(model, campo) == valor)

        return query
