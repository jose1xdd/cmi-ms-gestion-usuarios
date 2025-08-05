import logging
from typing import List

from app.models.inputs.familia.assing_familia_users import AssingFamilia
from app.models.inputs.persona.persona_create import PersonaCreate
from app.models.inputs.persona.persona_update import PersonaUpdate
from app.models.outputs.familia.familia_asignacion_response import AsignacionFamiliaResponse
from app.models.outputs.persona.persona_output import PersonaOut
from app.models.outputs.paginated_response import PaginatedPersonas
from app.models.outputs.response_estado import EstadoResponse
from app.persistence.model.familia import Familia
from app.persistence.model.persona import Persona
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
from app.persistence.repository.parcialidad_repository.interface.interface_parcialidad_repository import IParcialiadRepository
from app.persistence.repository.persona_repository.interface.interface_persona_repository import IPersonaRepository
from app.persistence.repository.user_repository.interface.interface_user_repository import IUsuarioRepository
from app.utils.exceptions_handlers.models.error_response import AppException


class PersonaManager:
    def __init__(
        self,
        usuario_repository: IUsuarioRepository,
        persona_repository: IPersonaRepository,
        familia_repository: IFamiliaRepository,
        parcialidad_repository: IParcialiadRepository,
        logger: logging.Logger,
    ):
        self.usuario_repository = usuario_repository
        self.persona_repository = persona_repository
        self.familia_repository = familia_repository
        self.parcialidad_repository = parcialidad_repository
        self.logger = logger

    def create_persona(self, data: PersonaCreate) -> EstadoResponse:
        self.logger.info(f"Iniciando creación de persona con ID: {data.id}")

        self.logger.info(f"Validando familia con ID: {data.idFamilia}")
        familia: Familia = self.familia_repository.get(data.idFamilia)
        if not familia:
            self.logger.error(f"Familia no encontrada: {data.idFamilia}")
            raise AppException("La Familia asignada no existe")
        familia.integrantes += 1

        self.logger.info(f"Validando parcialidad con ID: {data.idParcialidad}")
        if not self.parcialidad_repository.get(data.idParcialidad):
            self.logger.error(
                f"Parcialidad no encontrada: {data.idParcialidad}")
            raise AppException("Parcialidad no existente")

        self.logger.info(
            f"Verificando existencia previa de la persona ID: {data.id}")
        if self.persona_repository.get(data.id):
            self.logger.error(f"Persona ya registrada con ID: {data.id}")
            raise AppException("Ese documento ya se encuentra registrado")

        self.logger.info(f"Creando nueva persona con ID: {data.id}")
        self.persona_repository.create(data)
        self.familia_repository.update(familia.id, familia)
        self.logger.info(
            f"Persona creada y familia actualizada correctamente: {data.id}")

        return EstadoResponse(estado="Exitoso", message="Persona creada exitosamente")

    def update_persona(self, id_persona: str, data: PersonaUpdate) -> EstadoResponse:
        self.logger.info(
            f"Iniciando actualización de persona con ID: {id_persona}")
        persona: Persona = self.persona_repository.get(id_persona)
        if not persona:
            self.logger.error(f"Persona no encontrada con ID: {id_persona}")
            raise AppException("Esa persona no está registrada")

        self._update_familia_members(persona.idFamilia, data.idFamilia)

        self.logger.info(f"Actualizando datos de persona con ID: {id_persona}")
        self.persona_repository.update(id_persona, data)
        self.logger.info(f"Persona actualizada correctamente: {id_persona}")
        return EstadoResponse(estado="Exitoso", message="Persona actualizada exitosamente")

    def delete_persona(self, id_persona: str) -> EstadoResponse:
        self.logger.info(
            f"Iniciando eliminación lógica de persona con ID: {id_persona}")
        persona: Persona = self.persona_repository.get(id_persona)
        if not persona:
            self.logger.error(f"Persona no encontrada con ID: {id_persona}")
            raise AppException("Esa persona no está registrada")

        persona.activo = False
        familia: Familia = self.familia_repository.get(persona.idFamilia)
        familia.integrantes -= 1

        self.logger.info(
            f"Actualizando familia {familia.id} al eliminar persona")
        self.familia_repository.update(familia.id, familia)
        self.persona_repository.update(id_persona, persona)
        self.logger.info(f"Persona eliminada lógicamente: {id_persona}")
        return EstadoResponse(estado="Exitoso", message="Persona eliminada exitosamente")

    def get_personas(self, page: int, page_size: int) -> PaginatedPersonas:
        self.logger.info(
            f"Obteniendo personas: página {page}, tamaño {page_size}")
        paginated = self.persona_repository.paginate(page, page_size)
        return paginated

    def get_persona(self, id: str):
        persona = self.persona_repository.get(id)
        if persona is None:
            raise AppException("Persona no encontrada", 404)
        return persona

    def assing_familia_persona(self, data: AssingFamilia) -> AsignacionFamiliaResponse:
        self.logger.info(
            f"Asignando personas a familia con ID: {data.familia_id}")

        personas_no_encontradas = []
        personas_asignadas = []

        for persona_id in data.personas_id:
            self.logger.info(f"Procesando persona: {persona_id}")
            persona = self.persona_repository.get(persona_id)
            if not persona:
                self.logger.warning(f"Persona no encontrada: {persona_id}")
                personas_no_encontradas.append(persona_id)
                continue

            if persona.idFamilia is not None:
                self._update_familia_members(
                    persona.idFamilia, data.familia_id)

            persona.idFamilia = data.familia_id
            self.persona_repository.update(persona_id, persona)
            personas_asignadas.append(persona_id)
            self.logger.info(
                f"Persona asignada a familia {data.familia_id}: {persona_id}")

        self.logger.info(f"Personas asignadas: {personas_asignadas}")
        self.logger.info(f"Personas no encontradas: {personas_no_encontradas}")

        return AsignacionFamiliaResponse(
            familia_id=data.familia_id,
            personas_asignadas=personas_asignadas,
            personas_no_encontradas=personas_no_encontradas,
            total_asignadas=len(personas_asignadas),
            total_no_encontradas=len(personas_no_encontradas)
        )

    def _update_familia_members(self, id_familia_old: int, id_familia_new: int):
        if id_familia_new is not None and id_familia_old != id_familia_new:
            self.logger.info(
                f"Actualizando miembros entre familias: {id_familia_old} -> {id_familia_new}")
            familia_new = self.familia_repository.get(id_familia_new)

            if familia_new is None:
                self.logger.error(f"Familia no encontrada: {id_familia_new}")
                raise AppException("La Familia asignada no existe")

            if id_familia_old is None:
                familia_new.integrantes += 1
                self.logger.info(
                    f"Agregando miembro a nueva familia ID: {id_familia_new}")
                self.familia_repository.update(id_familia_new, familia_new)
                return

            familia_old = self.familia_repository.get(id_familia_old)
            familia_old.integrantes -= 1
            familia_new.integrantes += 1

            self.logger.info(
                f"Actualizando familia original ID: {id_familia_old}")
            self.familia_repository.update(id_familia_old, familia_old)

            self.logger.info(
                f"Actualizando nueva familia ID: {id_familia_new}")
            self.familia_repository.update(id_familia_new, familia_new)

            self.logger.info(
                f"Actualización de familias completada: {id_familia_old} -> {id_familia_new}")
