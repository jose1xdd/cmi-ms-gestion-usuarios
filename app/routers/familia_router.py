from fastapi import APIRouter
from fastapi import APIRouter, Depends, Query, status

from app.ioc.container import get_familia_manager
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.models.outputs.familia.familia_output import FamiliaOut
from app.models.outputs.paginated_response import PaginatedFamilias
from app.models.outputs.response_estado import EstadoResponse
from app.services.familia_manager import FamiliaManager


familia_router = APIRouter(prefix="/familias", tags=["Familia"])


@familia_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=EstadoResponse)
async def create(
        data: FamiliaCreate,
        manager: FamiliaManager = Depends(get_familia_manager)):
    return manager.create(data)


@familia_router.delete("/{id_familia}", status_code=status.HTTP_200_OK, response_model=EstadoResponse)
async def delete(
        id_familia: int,
        manager: FamiliaManager = Depends(get_familia_manager)):
    return manager.delete(id_familia)


@familia_router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedFamilias)
def get_familias(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, le=100),
        manager: FamiliaManager = Depends(get_familia_manager)):
    return manager.get_familias(page, page_size)


@familia_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=FamiliaOut)
def get_familia(
        id: int,
        manager: FamiliaManager = Depends(get_familia_manager)):
    return manager.get_familia(id)
