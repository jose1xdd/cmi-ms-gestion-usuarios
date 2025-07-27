from fastapi import APIRouter, Depends, Query, status

from app.models.inputs.persona_create import PersonaCreate
from app.models.inputs.persona_update import PersonaUpdate
from app.services.persona_manager import PersonaManager
from app.ioc.container import get_persona_manager

persona_router = APIRouter(prefix="/personas")


@persona_router.post("/create", status_code=status.HTTP_201_CREATED)
async def login(
        data: PersonaCreate,
        manager: PersonaManager = Depends(get_persona_manager)):
    manager.create_person(data)
    return {}


@persona_router.put("/{persona_id}", status_code=status.HTTP_202_ACCEPTED)
async def login(
        persona_id: str,
        data: PersonaUpdate,
        manager: PersonaManager = Depends(get_persona_manager)):
    persona = manager.update_persona(persona_id, data)
    return {"estado": "Exitoso", "data": persona}


@persona_router.delete("/{persona_id}", status_code=status.HTTP_200_OK)
async def login(
        persona_id: str,
        manager: PersonaManager = Depends(get_persona_manager)):
    manager.delete_persona(persona_id)
    return {"estado": "Exitoso"}

@persona_router.get("")
def get_personas(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    manager: PersonaManager = Depends(get_persona_manager)
):
    return manager.get_personas(page, page_size)