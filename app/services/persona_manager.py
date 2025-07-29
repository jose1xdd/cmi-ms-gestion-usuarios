import logging

from app.models.inputs.persona_create import PersonaCreate
from app.models.inputs.persona_update import PersonaUpdate
from app.persistence.model.familia import Familia
from app.persistence.model.persona import Persona
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
from app.persistence.repository.parcialidad_repository.interface.interface_parcialidad_repository import IParcialiadRepository
from app.persistence.repository.persona_repository.interface.interface_persona_repository import IPersonaRepository
from app.persistence.repository.user_repository.interface.interface_user_repository import IUsuarioRepository
from app.utils.exceptions_handlers.models.error_response import AppException


class PersonaManager():
    def __init__(self,
                 usuario_repository: IUsuarioRepository,
                 persona_repository: IPersonaRepository,
                 familia_repository: IFamiliaRepository,
                 parcialidad_repository: IParcialiadRepository,
                 logger: logging.Logger):
        self.usuario_repository = usuario_repository
        self.logger = logger
        self.persona_repository = persona_repository
        self.familia_repository = familia_repository
        self.parcialidad_repository = parcialidad_repository

    def create_persona(self, data: PersonaCreate):
        self.logger.info(
            f"Iniciando proceso de creación de persona con ID: {data.id}")

        # Validar existencia de la familia
        self.logger.info(
            f"Validando existencia de la familia con ID: {data.idFamilia}")
        familia: Familia = self.familia_repository.get(data.idFamilia)
        if not familia:
            self.logger.error(f"Familia no encontrada: {data.idFamilia}")
            raise AppException("La Familia asignada no existe")
        familia.integrantes = familia.integrantes+1
        # Validar existencia de la parcialidad
        self.logger.info(
            f"Validando existencia de la parcialidad con ID: {data.idParcialidad}")
        if not self.parcialidad_repository.get(data.idParcialidad):
            self.logger.error(
                f"Parcialidad no encontrada: {data.idParcialidad}")
            raise AppException("Parcialidad no existente")

        # Validar si la persona ya existe
        self.logger.info(
            f"Verificando si el documento ya está registrado: {data.id}")
        if self.persona_repository.get(data.id):
            self.logger.error(f"Persona ya registrada con ID: {data.id}")
            raise AppException("Ese documento ya se encuentra registrado")

        # Crear la persona
        self.logger.info(f"Creando persona con ID: {data.id}")
        self.persona_repository.create(data)
        self.logger.info(f"Persona creada exitosamente: {data.id}")
        self.logger.info(f"Cantidad de miembros de familia: {familia.id} actualizada")

        self.familia_repository.update(familia.id, familia)

    def update_persona(self, id_persona: str, data: PersonaUpdate):
        # Validar si la persona ya existe
        self.logger.info(
            f"Verificando existencia de la persona con id: {id_persona}")
        persona: Persona = self.persona_repository.get(id_persona)
        if not persona:
            self.logger.error(f"no existe una persona con ID: {id_persona}")
            raise AppException("Esa persona no está registrada")
        return self.persona_repository.update(id_persona, data)

    def delete_persona(self, id_persona: str):
        # Validar si la persona ya existe
        self.logger.info(
            f"Verificando existencia de la persona con id: {id_persona}")
        persona: Persona = self.persona_repository.get(id_persona)
        persona.activo = False
        if not persona:
            self.logger.error(f"no existe una persona con ID: {id_persona}")
            raise AppException("Esa persona no está registrada")
        return self.persona_repository.update(id_persona, persona)

    def get_personas(self, page: int, page_size: int):
        return self.persona_repository.paginate(page, page_size)
