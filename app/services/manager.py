import logging

from app.models.inputs.persona_input import PersonaInput
from app.persistence.model.familia import Familia
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
from app.persistence.repository.parcialidad_repository.interface.interface_parcialidad_repository import IParcialiadRepository
from app.persistence.repository.persona_repository.interface.interface_persona_repository import IPersonaRepository
from app.persistence.repository.user_repository.interface.interface_user_repository import IUsuarioRepository
from app.utils.exceptions_handlers.models.error_response import AppException
from fastapi import status


class Manager():
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

    def create_person(self, data: PersonaInput):
        self.logger.info(f"Iniciando proceso de creación de persona con ID: {data.id}")

        # Validar existencia de la familia
        self.logger.info(f"Validando existencia de la familia con ID: {data.idFamilia}")
        familia: Familia = self.familia_repository.get(data.idFamilia)
        if not familia:
            self.logger.error(f"Familia no encontrada: {data.idFamilia}")
            raise AppException("La Familia asignada no existe")

        # Validar límite de miembros
        miembros_actuales = self.persona_repository.find_familia_members(data.idFamilia)
        self.logger.info(f"Miembros actuales en familia {data.idFamilia}: {miembros_actuales}/{familia.integrantes}")
        if miembros_actuales >= familia.integrantes:
            self.logger.error(
                f"Se alcanzó el límite de integrantes para la familia {data.idFamilia}. "
                f"Miembros actuales: {miembros_actuales}, Límite: {familia.integrantes}"
            )
            raise AppException(
                f"Cantidad máxima de miembros alcanzada. "
                f"Miembros actuales: {miembros_actuales}, Límite permitido: {familia.integrantes}"
            )

        # Validar existencia de la parcialidad
        self.logger.info(f"Validando existencia de la parcialidad con ID: {data.idParcialidad}")
        if not self.parcialidad_repository.get(data.idParcialidad):
            self.logger.error(f"Parcialidad no encontrada: {data.idParcialidad}")
            raise AppException("Parcialidad no existente")

        # Validar si la persona ya existe
        self.logger.info(f"Verificando si el documento ya está registrado: {data.id}")
        if self.persona_repository.get(data.id):
            self.logger.error(f"Persona ya registrada con ID: {data.id}")
            raise AppException("Ese documento ya se encuentra registrado")

        # Crear la persona
        self.logger.info(f"Creando persona con ID: {data.id}")
        self.persona_repository.create(data)
        self.logger.info(f"Persona creada exitosamente: {data.id}")
