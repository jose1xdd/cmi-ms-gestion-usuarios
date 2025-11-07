from typing import Optional
from fastapi import APIRouter, File, UploadFile, Depends, Query, status
from fastapi.responses import JSONResponse

from app.ioc.container import get_familia_manager
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.models.inputs.persona.persona_carga_masiva import CargaMasivaResponse
from app.models.outputs.familia.familia_output import FamiliaDataLeader, FamiliaOut, FamiliaResumenOut
from app.models.outputs.paginated_response import PaginatedDataLeader, PaginatedFamilias, PaginatedPersonasFamilia
from app.models.outputs.persona.persona_output import EstadisticaGeneralOut
from app.models.outputs.response_estado import EstadoResponse
from app.services.familia_manager import FamiliaManager

familia_router = APIRouter(prefix="/familias", tags=["Familia"])


@familia_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=EstadoResponse
)
async def create(
    data: FamiliaCreate,
    manager: FamiliaManager = Depends(get_familia_manager)
):
    """
    Crea una familia nueva con estado y representante opcional.
    """
    response = manager.create(data)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=201)


@familia_router.post(
    "/upload-excel",
    status_code=status.HTTP_201_CREATED,
    response_model=CargaMasivaResponse
)
async def upload_excel(
    file: UploadFile = File(...),
    manager: FamiliaManager = Depends(get_familia_manager)
):
    """
    Carga masiva de familias desde archivo Excel.
    """
    response = await manager.upload_excel(file)
    return response


@familia_router.delete(
    "/{id_familia}",
    status_code=status.HTTP_200_OK,
    response_model=EstadoResponse
)
async def delete(
    id_familia: int,
    manager: FamiliaManager = Depends(get_familia_manager)
):
    response = manager.delete(id_familia)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=200)


@familia_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedFamilias
)
def get_familias(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    manager: FamiliaManager = Depends(get_familia_manager)
):
    return manager.get_familias(page, page_size)


@familia_router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedFamilias
)
def search_familia(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    query: Optional[str] = Query(None),
    manager: FamiliaManager = Depends(get_familia_manager)
):
    """
    Busca familias por coincidencia parcial en los datos del representante (líder).
    """
    result = manager.search_familia_by_lider(query, page, page_size)
    return result


@familia_router.get(
    "/get/leader-data",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedDataLeader,
    summary="Lista familias con datos del líder y parcialidad"
)
def get_familias_dashboard(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    manager: FamiliaManager = Depends(get_familia_manager),
):
    """
    Obtiene un resumen de las familias con su líder, cédula, parcialidad y estado.
    """
    return manager.get_familias_leaderdata(page, page_size)


@familia_router.get(
    "/{id_familia}/miembros",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedPersonasFamilia,
    summary="Obtiene los miembros de una familia por su ID"
)
def get_miembros_familia(
    id_familia: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    query: Optional[str] = Query(
        None, description="Buscar por nombre, apellido o cédula"),
    manager: FamiliaManager = Depends(get_familia_manager)
):
    """
    Retorna los miembros de la familia especificada, con búsqueda parcial.
    """
    return manager.get_miembros_familia(id_familia, query, page, page_size)


@familia_router.get(
    "/{id_familia}/resumen",
    response_model=FamiliaResumenOut,
    summary="Obtiene resumen de una familia"
)
def get_familia_resumen(
    id_familia: int,
    manager: FamiliaManager = Depends(get_familia_manager)
):
    """
    Retorna información resumida de una familia:
    ID, líder, parcialidad, total de miembros, miembros activos y defunciones.
    """
    return manager.get_familia_resumen(id_familia)


@familia_router.get(
    "/estadisticas-generales",
    response_model=EstadisticaGeneralOut,
    summary="Obtiene el total de familias y total de personas"
)
def get_estadisticas_generales(
    manager: FamiliaManager = Depends(get_familia_manager)
):
    """
    Retorna estadísticas generales del sistema:
    - Total de familias registradas
    - Total de personas registradas
    """
    return manager.get_estadisticas_generales()


@familia_router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=FamiliaOut
)
def get_familia(
    id: int,
    manager: FamiliaManager = Depends(get_familia_manager)
):
    return manager.get_familia(id)
