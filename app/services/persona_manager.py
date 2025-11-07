import io
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional
from fastapi import UploadFile

from app.models.inputs.familia.assing_familia_users import AssingFamilia
from app.models.inputs.persona.persona_carga_masiva import CargaMasivaResponse, ErrorPersonaOut
from app.models.inputs.persona.persona_create import PersonaCreate
from app.models.inputs.persona.persona_create_excel import PersonaCreateExcel
from app.models.inputs.persona.persona_update import PersonaDefuncion, PersonaUpdate
from app.models.outputs.familia.familia_asignacion_response import AsignacionFamiliaResponse
from app.models.outputs.familia.familia_output import FamiliaResumenOut
from app.models.outputs.paginated_response import PaginatedPersonas
from app.models.outputs.response_estado import EstadoResponse
from app.persistence.model.familia import Familia
from app.persistence.model.persona import Persona
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
from app.persistence.repository.parcialidad_repository.interface.interface_parcialidad_repository import IParcialiadRepository
from app.persistence.repository.persona_repository.interface.interface_persona_repository import IPersonaRepository
from app.persistence.repository.user_repository.interface.interface_user_repository import IUsuarioRepository
from app.utils.constans import COLUMNS_PERSONA
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
        self.usuario_repository:IUsuarioRepository = usuario_repository
        self.persona_repository:IPersonaRepository = persona_repository
        self.familia_repository:IFamiliaRepository = familia_repository
        self.parcialidad_repository:IParcialiadRepository = parcialidad_repository
        self.logger = logger

    def create_persona(self, data: PersonaCreate) -> EstadoResponse:
        self.logger.info(f"Iniciando creación de persona con ID: {data.id}")

        self._validar_persona(data)

        # --- Crear Persona ---
        self.logger.info(f"Creando nueva persona con ID: {data.id}")
        self.persona_repository.create(data)

        self.logger.info(f"Persona creada correctamente: {data.id}")
        return EstadoResponse(estado="Exitoso", message="Persona creada exitosamente")

    def update_persona(self, id_persona: str, data: PersonaUpdate) -> EstadoResponse:
        self.logger.info(
            f"Iniciando actualización de persona con ID: {id_persona}")
        persona: Persona = self.persona_repository.get(id_persona)
        if not persona:
            self.logger.error(f"Persona no encontrada con ID: {id_persona}")
            raise AppException("Esa persona no está registrada")

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

        self.logger.info(
            f"Actualizando familia {familia.id} al eliminar persona")
        self.familia_repository.update(familia.id, familia)
        self.persona_repository.update(id_persona, persona)
        self.logger.info(f"Persona eliminada lógicamente: {id_persona}")
        return EstadoResponse(estado="Exitoso", message="Persona eliminada exitosamente")

    def get_personas(self, page: int, page_size: int, filters: Dict[str, Any]) -> PaginatedPersonas:
        self.logger.info(
            f"Obteniendo personas: página {page}, tamaño {page_size}")
        paginated = self.persona_repository.find_all_personas(
            page, page_size, filters)
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
        familia = self.familia_repository.get(data.familia_id)
        if not familia:
            self.logger.error(f"Familia no encontrada: {data.familia_id}")
            raise AppException("La Familia asignada no existe")

        for persona_id in data.personas_id:
            self.logger.info(f"Procesando persona: {persona_id}")
            persona = self.persona_repository.get(persona_id)
            if not persona:
                self.logger.warning(f"Persona no encontrada: {persona_id}")
                personas_no_encontradas.append(persona_id)
                continue

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

    def unassign_familia_persona(self, persona_id: str) -> EstadoResponse:
        """
        Desasigna a una persona de cualquier familia (pone idFamilia = NULL).
        Retorna un EstadoResponse.
        """
        self.logger.info(
            f"[PersonaManager] Eliminando asociación familiar para persona {persona_id}")

        persona = self.persona_repository.get(persona_id)
        if not persona:
            self.logger.warning(
                f"[PersonaManager] Persona no encontrada: {persona_id}")
            raise AppException("La persona indicada no existe")

        if persona.idFamilia is None:
            self.logger.info(
                f"[PersonaManager] Persona {persona_id} ya no pertenece a ninguna familia")
            return EstadoResponse(
                estado="Exitoso",
                message=f"La persona {persona_id} no pertenece a ninguna familia"
            )

        persona.idFamilia = None
        self.persona_repository.update(persona_id, persona)

        self.logger.info(
            f"[PersonaManager] Persona {persona_id} desasignada correctamente de su familia")

        return EstadoResponse(
            estado="Exitoso",
            message=f"Persona {persona_id} desasignada exitosamente de su familia"
        )

    async def upload_excel(self, file: UploadFile) -> CargaMasivaResponse:
        try:
            content = await file.read()
            df = pd.read_excel(io.BytesIO(content))

            # ✅ Validar columnas
            missing = [col for col in COLUMNS_PERSONA if col not in df.columns]
            if missing:
                return CargaMasivaResponse(
                    status="error",
                    errores=[
                        ErrorPersonaOut(
                            fila=0,
                            id=None,
                            mensaje=f"Faltan columnas en el Excel: {missing}"
                        )
                    ],
                )

            # ✅ Normalizar datos antes de validación
            df["id"] = df["id"].astype(str)              # siempre string
            df["telefono"] = df["telefono"].astype(str)  # siempre string
            df["familia"] = df["familia"].astype(int)  # siempre string
            df = df.replace({np.nan: None})              # NaN → None

            personas: List[PersonaCreate] = []
            errores: List[ErrorPersonaOut] = []

            for i, row in df.iterrows():
                try:
                    persona = PersonaCreateExcel(**row.to_dict())
                    parcialidad = self.parcialidad_repository.find_by_name(
                        persona.parcialidad)
                    persona_create = PersonaCreate(**persona.model_dump())
                    if parcialidad is not None:
                        persona_create.idParcialidad = parcialidad.id
                    persona_create.idFamilia = persona.familia
                    self._validar_persona(persona_create)
                    personas.append(persona_create)
                except Exception as e:
                    errores.append(
                        ErrorPersonaOut(
                            fila=i + 2,  # +2 porque Excel empieza en 1 y fila 1 es header
                            id=str(row.get("id")) if row.get("id") else None,
                            mensaje=str(e),
                        )
                    )

            insertados = 0
            if personas:
                insertados = self.persona_repository.bulk_insert(personas)

            return CargaMasivaResponse(
                status="ok",
                insertados=insertados,
                total_procesados=len(personas) + len(errores),
                errores=errores,
            )

        except Exception as e:
            return CargaMasivaResponse(
                status="error",
                errores=[ErrorPersonaOut(fila=0, id=None, mensaje=str(e))],
            )

    def registrar_defuncion(self, data: PersonaDefuncion) -> EstadoResponse:
        """
        Registra la fecha de defunción de una persona.
        """
        self.logger.info(
            f"[PersonaManager] Registrando defunción para persona {data.id}")

        persona = self.persona_repository.get(data.id)
        if not persona:
            self.logger.warning(
                f"[PersonaManager] Persona no encontrada: {data.id}")
            raise AppException("La persona indicada no existe")

        # Validar que no se haya registrado ya
        if persona.fechaDefuncion:
            self.logger.warning(
                f"[PersonaManager] La persona {data.id} ya tiene registrada una fecha de defunción")
            raise AppException(
                "La persona ya tiene registrada una fecha de defunción")

        persona.fechaDefuncion = data.fechaDefuncion
        self.persona_repository.update(data.id, persona)

        self.logger.info(
            f"[PersonaManager] Fecha de defunción registrada para persona {data.id}")

        return EstadoResponse(
            estado="Exitoso",
            message=f"Fecha de defunción registrada para la persona {data.id}"
        )
    def get_familia_resumen(self, id_familia: int) -> FamiliaResumenOut:
        """
        Retorna la información resumen de una familia.
        """
        self.logger.info(f"[FamiliaManager] Consultando resumen de familia {id_familia}")
        return self.familia_repository.get_familia_resumen(id_familia)
    def _validar_persona(self, data: PersonaCreate) -> Familia | None:
        """
        Valida reglas de negocio antes de crear una Persona.
        Retorna la familia actualizada (si aplica), o None.
        """
        familia = None

        # --- Validación de Familia ---
        if data.idFamilia is not None:
            self.logger.info(f"Validando familia con ID: {data.idFamilia}")
            familia = self.familia_repository.get(data.idFamilia)
            if not familia:
                self.logger.error(f"Familia no encontrada: {data.idFamilia}")
                raise AppException("La Familia asignada no existe")
        else:
            self.logger.info("No se asignó familia a la persona")

        # --- Validación de Parcialidad ---
        if data.idParcialidad is not None:
            self.logger.info(
                f"Validando parcialidad con ID: {data.idParcialidad}")
            if not self.parcialidad_repository.get(data.idParcialidad):
                self.logger.error(
                    f"Parcialidad no encontrada: {data.idParcialidad}")
                raise AppException("Parcialidad no existente")
        else:
            self.logger.info("No se asignó parcialidad a la persona")

        # --- Verificar duplicado ---
        self.logger.info(
            f"Verificando existencia previa de la persona ID: {data.id}")
        if self.persona_repository.get(data.id):
            self.logger.error(f"Persona ya registrada con ID: {data.id}")
            raise AppException("Ese documento ya se encuentra registrado")

        return familia
