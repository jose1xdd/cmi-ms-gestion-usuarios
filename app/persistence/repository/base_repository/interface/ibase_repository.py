from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Optional, List, Union
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)
ID = TypeVar('ID')
M = TypeVar('M')
class IBaseRepository(ABC, Generic[T, ID]):
    @abstractmethod
    def get(self, id: ID) -> Optional[T]:
        pass
    
    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        pass
    
    @abstractmethod
    def create(self, obj_in: T) -> T:
        pass
    
    @abstractmethod
    def update(self, id: ID, obj_in: T) -> Optional[T]:
        pass
    
    @abstractmethod
    def delete(self, id: ID) -> bool:
        pass
    
    @abstractmethod
    def paginate(self, page: int = 1, page_size: int = 10, query=None) -> Dict[str, Union[int, List[M]]]:
        """Devuelve un diccionario con los campos: total_items, total_pages, current_page, items"""
