from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, status

from app.models.inputs.persona_create import PersonaCreate
from app.models.inputs.persona_update import PersonaUpdate
from app.services.manager import Manager
from app.ioc.container import Container, get_manager

persona_router = APIRouter()


@persona_router.post("/personas/create", status_code=status.HTTP_201_CREATED)
async def login(
        data: PersonaCreate,
        manager: Manager = Depends(get_manager)):
    manager.create_person(data)
    return {}


@persona_router.put("/personas/{persona_id}", status_code=status.HTTP_202_ACCEPTED)
async def login(
        persona_id: str,
        data: PersonaUpdate,
        manager: Manager = Depends(get_manager)):
    persona = manager.update_persona(persona_id, data)
    return {"estado": "Exitoso", "data": persona}


@persona_router.delete("/personas/{persona_id}", status_code=status.HTTP_200_OK)
async def login(
        persona_id: str,
        manager: Manager = Depends(get_manager)):
    manager.delete_persona(persona_id)
    return {"estado": "Exitoso"}

@persona_router.get("/personas")
def get_personas(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    manager: Manager = Depends(get_manager)
):
    return manager.get_personas(page, page_size)