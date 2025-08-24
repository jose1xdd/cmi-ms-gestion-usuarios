
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.ioc.container import get_parcialidad_manager
from app.models.inputs.parcialidad.parcialidad_create import ParcialidadCreate
from app.models.inputs.parcialidad.parcialidad_filter import ParcialidadFilter
from app.models.outputs.paginated_response import PaginatedParcialidad
from app.models.outputs.parcialidad.parcialidad_output import ParcialidadOut
from app.models.outputs.response_estado import EstadoResponse
from app.services.parcialidad_manager import ParcialidadManager


parcialialidad_router = APIRouter(prefix="/parcialidad", tags=["Parcialidad"])


@parcialialidad_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=EstadoResponse)
def create(data: ParcialidadCreate,
           manager: ParcialidadManager = Depends(get_parcialidad_manager)):
    response = manager.create(data)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=201)


@parcialialidad_router.delete("/{id_parcialidad}", status_code=status.HTTP_200_OK, response_model=EstadoResponse)
def delete(
        id_parcialidad: int,
        manager: ParcialidadManager = Depends(get_parcialidad_manager)):
    response = manager.delete(id_parcialidad)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=200)


@parcialialidad_router.get("", response_model=PaginatedParcialidad)
def get_all(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, le=100),
        filters: ParcialidadFilter = Depends(),
        manager: ParcialidadManager = Depends(get_parcialidad_manager)):
    return manager.get_parcialidades(page, page_size, filters.model_dump(exclude_none=True))


@parcialialidad_router.get("/{id_parcialidad}", response_model=ParcialidadOut)
def get(
        id_parcialidad: int,
        manager: ParcialidadManager = Depends(get_parcialidad_manager)):
    return manager.get_parcialidad_by_id(id_parcialidad)


@parcialialidad_router.put("/{id_parcialidad}", response_model=EstadoResponse, status_code=status.HTTP_202_ACCEPTED)
def update(
        id_parcialidad: int,
        data: ParcialidadCreate,
        manager: ParcialidadManager = Depends(get_parcialidad_manager)):
    response = manager.update_parcialidad_by_id(id_parcialidad, data)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=200)
