import logging
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.ioc.container import Container
from app.utils.exceptions_handlers.exceptions_handlers import (
    custom_app_exception_handler,
    global_exception_handler,
    validation_exception_handler,
)
from app.utils.exceptions_handlers.models.error_response import AppException
from app.routers.main_router import main_router

def create_app() -> FastAPI:
    app = FastAPI()

    # Crear el container
    container = Container()
    container.init_resources()
    container.wire(
    modules=[
        "app.routers.main_router",
        "app.services.manager",
        "app.ioc.container"
    ]
)
    app.container = container

    # Registrar excepciones
    app.add_exception_handler(AppException, custom_app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # Registrar router
    app.include_router(main_router, prefix="/ms-gestion-usuarios")

    # Logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    return app
