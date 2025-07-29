from fastapi import APIRouter
from fastapi import APIRouter, Depends, Query, Request, status

from app.ioc.container import get_familia_manager
from app.services.familia_manager import FamiliaManager


familia_router = APIRouter(prefix="/familias")


@familia_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create(
        manager: FamiliaManager = Depends(get_familia_manager)):
    return manager.create()