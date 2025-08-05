from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.models.inputs.familia.assing_familia_users import AssingFamilia
from app.models.inputs.persona.persona_create import PersonaCreate
from app.models.inputs.persona.persona_update import PersonaUpdate
from app.models.outputs.familia.familia_asignacion_response import AsignacionFamiliaResponse
from app.models.outputs.persona.persona_output import PersonaOut
from app.models.outputs.response_estado import EstadoResponse
from app.models.outputs.paginated_response import PaginatedPersonas

from app.services.persona_manager import PersonaManager
from app.ioc.container import get_persona_manager
from app.utils.middlewares.validate_persona_admin import validar_persona_admin

persona_router = APIRouter(prefix="/personas", tags=["Persona"])


@persona_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=EstadoResponse)
async def create(
    data: PersonaCreate,
    manager: PersonaManager = Depends(get_persona_manager)
):
    response = manager.create_persona(data)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=201)


@persona_router.put("/{persona_id}", status_code=status.HTTP_202_ACCEPTED, response_model=EstadoResponse)
async def update(
    persona_id: str,
    data: PersonaUpdate,
    _: bool = validar_persona_admin(),
    manager: PersonaManager = Depends(get_persona_manager)
):
    response = manager.update_persona(persona_id, data)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=202)


@persona_router.delete("/{persona_id}", status_code=status.HTTP_200_OK, response_model=EstadoResponse)
async def delete(
    persona_id: str,
    manager: PersonaManager = Depends(get_persona_manager)
):
    response = manager.delete_persona(persona_id)
    return JSONResponse(content=response.model_dump(exclude_none=True), status_code=200)


@persona_router.get("", response_model=PaginatedPersonas)
def get_personas(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    manager: PersonaManager = Depends(get_persona_manager)
):
    return manager.get_personas(page, page_size)


@persona_router.get("/{persona_id}", response_model=PersonaOut)
def get_personas(
    persona_id: str,
    _: bool = validar_persona_admin(),
    manager: PersonaManager = Depends(get_persona_manager)
):
    return manager.get_persona(persona_id)


@persona_router.patch("/assing-family", response_model=AsignacionFamiliaResponse)
def assing_family_users(
    data: AssingFamilia,
    manager: PersonaManager = Depends(get_persona_manager)
):
    return manager.assing_familia_persona(data)
