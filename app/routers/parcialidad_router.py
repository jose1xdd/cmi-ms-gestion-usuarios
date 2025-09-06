
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import JSONResponse

from app.ioc.container import get_parcialidad_manager
from app.models.inputs.parcialidad.parcialidad_create import ParcialidadCreate
from app.models.inputs.parcialidad.parcialidad_filter import ParcialidadFilter
from app.models.inputs.persona.persona_carga_masiva import CargaMasivaResponse
from app.models.outputs.paginated_response import PaginatedParcialidad
from app.models.outputs.parcialidad.parcialidad_output import ParcialidadOut
from app.models.outputs.response_estado import EstadoResponse
from app.services.parcialidad_manager import ParcialidadManager


parcialidad_router = APIRouter(prefix="/parcialidad", tags=["Parcialidad"])


@parcialidad_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=EstadoResponse)
def create(data: ParcialidadCreate,
           manager: ParcialidadManager = Depends(get_parcialidad_manager)):
    response = manager.create(data)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=201)


@parcialidad_router.delete("/{id_parcialidad}", status_code=status.HTTP_200_OK, response_model=EstadoResponse)
def delete(
        id_parcialidad: int,
        manager: ParcialidadManager = Depends(get_parcialidad_manager)):
    response = manager.delete(id_parcialidad)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=200)


@parcialidad_router.get("", response_model=PaginatedParcialidad)
def get_all(
        page: int = Query(1, ge=1),
        page_size: int = Query(10, le=100),
        filters: ParcialidadFilter = Depends(),
        manager: ParcialidadManager = Depends(get_parcialidad_manager)):
    return manager.get_parcialidades(page, page_size, filters.model_dump(exclude_none=True))


@parcialidad_router.get("/{id_parcialidad}", response_model=ParcialidadOut)
def get(
        id_parcialidad: int,
        manager: ParcialidadManager = Depends(get_parcialidad_manager)):
    return manager.get_parcialidad_by_id(id_parcialidad)


@parcialidad_router.put("/{id_parcialidad}", response_model=EstadoResponse, status_code=status.HTTP_202_ACCEPTED)
def update(
        id_parcialidad: int,
        data: ParcialidadCreate,
        manager: ParcialidadManager = Depends(get_parcialidad_manager)):
    response = manager.update_parcialidad_by_id(id_parcialidad, data)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=200)

@parcialidad_router.post("/upload-excel", status_code=status.HTTP_201_CREATED, response_model=CargaMasivaResponse)
async def upload_excel(
    file: UploadFile = File(...),
    manager: ParcialidadManager = Depends(get_parcialidad_manager)
):
    response = manager.upload_excel(file)
    return await response