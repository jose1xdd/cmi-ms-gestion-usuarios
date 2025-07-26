import logging
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
from app.persistence.repository.parcialidad_repository.interface.interface_parcialidad_repository import IParcialiadRepository
from app.persistence.repository.persona_repository.interface.interface_persona_repository import IPersonaRepository
from app.persistence.repository.repository_factory import RepositoryFactory
from app.persistence.repository.user_repository.interface.interface_user_repository import IUsuarioRepository
from app.services.manager import Manager


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.routers.main_router",
                 "app.ioc.container"])

    logger = providers.Singleton(logging.getLogger, __name__)


@inject
def get_manager(
    db: Session = Depends(get_db),
    logger: logging.Logger = Depends(Provide[Container.logger]),
) -> Manager:
    factory = RepositoryFactory(db=db)

    return Manager(
        logger=logger,
        usuario_repository=factory.get_repository(IUsuarioRepository),
        persona_repository=factory.get_repository(IPersonaRepository),
        familia_repository=factory.get_repository(IFamiliaRepository),
        parcialidad_repository=factory.get_repository(IParcialiadRepository),
    )
