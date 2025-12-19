import logging
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import io

from fastapi import UploadFile
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.models.inputs.familia.familia_update import FamiliaUpdate
from app.models.inputs.persona.persona_carga_masiva import CargaMasivaResponse, ErrorPersonaOut
from app.models.inputs.persona.persona_update import PersonaUpdate
from app.models.outputs.familia.familia_output import FamiliaOut, FamiliaResumenOut
from app.models.outputs.paginated_response import PaginatedFamilias
from app.models.outputs.persona.persona_output import EstadisticaGeneralOut
from app.models.outputs.response_estado import EstadoResponse
from app.persistence.model import miembro_familia
from app.persistence.model.familia import Familia
from app.persistence.model.enum import EnumEstadoFamilia
from app.persistence.model.miembro_familia import MiembroFamilia
from app.persistence.model.persona import Persona
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
from app.persistence.repository.miembro_familia_repository.interface.inteface_miembro_familia import IMiembroRepository
from app.persistence.repository.persona_repository.interface.interface_persona_repository import IPersonaRepository
from app.utils.constans import COLUMNS_FAMILIA
from app.utils.exceptions_handlers.models.error_response import AppException


class FamiliaManager:
    def __init__(self, familia_repository: IFamiliaRepository,
                 persona_repository: IPersonaRepository,
                 miembro_repository: IMiembroRepository,
                 logger: logging.Logger):
        self.familia_repository: IFamiliaRepository = familia_repository
        self.persona_repository: IPersonaRepository = persona_repository
        self.miembro_repository = miembro_repository
        self.logger = logger

    def create(self, data: FamiliaCreate) -> EstadoResponse:
        """
        Crea una familia con estado y representante opcional.
        """
        self.logger.info(
            f"[FamiliaManager] Iniciando creación de familia con datos: {data.model_dump(exclude_none=True)}")

        self._validar_familia(data)

        try:
            familia = Familia(
                id=data.idFamilia,
                estado=data.estado or EnumEstadoFamilia.ACTIVA
            )

            created = self.familia_repository.create(familia)

            if data.representanteId:
                self.logger.info(
                    f"[FamiliaManager] Asignando representante {data.representanteId} a la familia {created.id}")
                self.miembro_repository.create(MiembroFamilia(
                    personaId=data.representanteId, familiaId=familia.id, esRepresentante=True))
                self.logger.info(
                    f"[FamiliaManager] ✅ Representante {data.representanteId} asignado correctamente a la familia {created.id}"
                )
            self.logger.info(
                f"[FamiliaManager] ✅ Familia creada exitosamente | ID: {created.id}, "
                f"Estado: {created.estado}, Representante: {data.representanteId}"
            )
            familia_data = created.to_dict()
            familia_data["representanteId"] = data.representanteId
            return EstadoResponse(
                estado="success",
                message="Familia creada exitosamente",
                data=familia_data
            )
        except Exception as e:
            self.logger.exception(
                f"[FamiliaManager] ❌ Error al crear familia: {e}")
            raise AppException("Error interno al crear la familia")

    def delete(self, familia_id: int) -> EstadoResponse:
        self.logger.info(
            f"[FamiliaManager] Solicitando eliminación de familia ID: {familia_id}")

        result = self.familia_repository.delete(familia_id)

        if not result:
            self.logger.warning(
                f"[FamiliaManager] ⚠️ No se encontró familia con ID {familia_id} para eliminar")
            raise AppException("No se encontró la familia para eliminar")

        self.logger.info(
            f"[FamiliaManager] 🗑️ Familia eliminada correctamente: ID {familia_id}")
        return EstadoResponse(
            estado="success",
            message="Familia eliminada exitosamente"
        )

    def get_familias(self, page: int, page_size: int) -> PaginatedFamilias:
        self.logger.info(
            f"[FamiliaManager] Consultando familias | Página: {page}, Tamaño: {page_size}")
        result = self.familia_repository.get_familias_con_lider(page, page_size)
        
        self.logger.info(
            f"[FamiliaManager] ✅ Consulta completada | Total familias en página: {result['items'].__len__()}")
        return result

    def update_familias(self, request: FamiliaUpdate):
        self.logger.info(
            "[FamiliaManager] 🔄 Iniciando actualización de familia")

        familia = self.familia_repository.get(request.familiaId)
        if familia is None:
            self.logger.warning(
                f"[FamiliaManager] ⚠️ Familia con ID {request.familiaId} no encontrada"
            )
            raise AppException("Familia no encontrada", 404)

        # Manejo del líder (asignar o remover)
        self._set_lider(
            familia_id=request.familiaId,
            representante_id=request.representanteId
        )

        self.logger.info(
            f"[FamiliaManager] 🎉 Familia {familia.id} actualizada exitosamente"
        )

        return EstadoResponse(
            estado="success",
            message="Familia actualizada exitosamente"
        )

    def _set_lider(self, familia_id: int, representante_id: Optional[str]):
        """
        Asigna o remueve el líder de una familia.
        """
        # Obtener líder actual
        lider_actual = self.miembro_repository.get_lider_familia(familia_id)

        # Si no se envía representante, se remueve el líder actual
        if representante_id is None:
            if lider_actual:
                lider_actual.esRepresentante = False
                self.miembro_repository.update(lider_actual.id, lider_actual)
            return

        # Validar persona
        persona = self.persona_repository.get(representante_id)
        if persona is None:
            self.logger.warning(
                f"[FamiliaManager] ⚠️ Persona con ID {representante_id} no encontrada"
            )
            raise AppException("Persona no encontrada", 404)

        # Validar que pertenezca a la familia
        miembro = self.miembro_repository.get_familia_actual(representante_id)
        if miembro is None or miembro.familiaId != familia_id:
            self.logger.warning(
                f"[FamiliaManager] ⚠️ Persona con ID {representante_id} no pertenece a la familia"
            )
            raise AppException("Persona no pertenece a la familia", 404)

        # Desactivar líder anterior si existe y es distinto
        if lider_actual and lider_actual.id != miembro.id:
            lider_actual.esRepresentante = False
            self.miembro_repository.update(lider_actual.id, lider_actual)

        # Asignar nuevo líder
        miembro.esRepresentante = True
        self.miembro_repository.update(miembro.id, miembro)

    def get_familia(self, familia_id: int) -> FamiliaOut:
        self.logger.info(
            f"[FamiliaManager] Buscando familia con ID: {familia_id}")
        familia = self.familia_repository.get_familia_by_id(familia_id)

        if familia is None:
            self.logger.warning(
                f"[FamiliaManager] ⚠️ Familia con ID {familia_id} no encontrada")
            raise AppException("Familia no encontrada", 404)

        self.logger.info(
            f"[FamiliaManager] ✅ Familia encontrada | ID: {familia.id}, "
            f"Estado: {familia.estado}, Representante: {familia.representanteId}"
        )
        return familia

    async def upload_excel(self, file: UploadFile) -> CargaMasivaResponse:
        self.logger.info(
            f"[FamiliaManager] Iniciando carga masiva de familias desde archivo: {file.filename}"
        )

        try:
            content = await file.read()
            df = pd.read_excel(io.BytesIO(content))
            self.logger.info(
                f"[FamiliaManager] Archivo leído correctamente | Filas detectadas: {len(df)}"
            )

            missing = [col for col in COLUMNS_FAMILIA if col not in df.columns]
            if missing:
                self.logger.error(
                    f"[FamiliaManager] ❌ Faltan columnas requeridas en Excel: {missing}"
                )
                return CargaMasivaResponse(
                    status="error",
                    errores=[
                        ErrorPersonaOut(
                            fila=0,
                            id=None,
                            mensaje=f"Faltan columnas: {missing}"
                        )
                    ]
                )

            df = df.replace({np.nan: None})

            familias: List[FamiliaCreate] = []
            errores: List[ErrorPersonaOut] = []
            representantes: Dict[int, str] = {}

            for i, row in df.iterrows():
                try:
                    familia_dict = row.to_dict()
                    representante_id = familia_dict.pop(
                        "cedulaRepresentante", None)

                    if representante_id:
                        persona = self.persona_repository.get(representante_id)
                        if not persona:
                            raise AppException(
                                f"El representante '{representante_id}' no existe"
                            )
                        representantes[familia_dict["idFamilia"]] = str(
                            representante_id)

                    familia = FamiliaCreate(**familia_dict)
                    self._validar_familia(familia)
                    familias.append(familia)

                except Exception as e:
                    self.logger.warning(
                        f"[FamiliaManager] Error en fila {i + 2}: {e}"
                    )
                    errores.append(
                        ErrorPersonaOut(
                            fila=i + 2,
                            id=str(row.get("idFamilia")) if row.get(
                                "idFamilia") else None,
                            mensaje=str(e),
                        )
                    )

            insertados = 0
            if familias:
                self.logger.info(
                    f"[FamiliaManager] Insertando {len(familias)} familias válidas..."
                )
                insertados = self.familia_repository.bulk_insert(familias)

                for familia_id, representante_id in representantes.items():
                    miembro = self.miembro_repository.get_familia_actual(
                        representante_id
                    )

                    if not miembro:
                        self.miembro_repository.create(
                            MiembroFamilia(
                                personaId=representante_id,
                                familiaId=familia_id,
                                activo=True,
                                esRepresentante=False
                            )
                        )

                    self._set_lider(
                        familia_id=familia_id,
                        representante_id=representante_id
                    )

            total = len(familias) + len(errores)
            self.logger.info(
                f"[FamiliaManager] Carga masiva finalizada | Total: {total}, Errores: {len(errores)}"
            )

            return CargaMasivaResponse(
                status="ok",
                insertados=insertados,
                total_procesados=total,
                errores=errores,
            )

        except Exception as e:
            self.logger.exception(
                f"[FamiliaManager] ❌ Error procesando archivo Excel: {e}"
            )
            return CargaMasivaResponse(
                status="error",
                errores=[ErrorPersonaOut(fila=0, id=None, mensaje=str(e))],
            )

    def search_familia_by_lider(
        self,
        query: str,
        page: int,
        page_size: int,
        parcialidad_id: int | None = None,
        rango_miembros: str | None = None,
        estado: EnumEstadoFamilia | None = None
    ):

        self.logger.info(
            f"[FamiliaManager] 🔍 Buscando familias con query='{query}', "
            f"parcialidad_id={parcialidad_id}, rango_miembros={rango_miembros}, estado={estado}"
        )

        familias = self.familia_repository.search_by_representante(
            page=page,
            page_size=page_size,
            query=query,
            parcialidad_id=parcialidad_id,
            rango_miembros=rango_miembros,
            estado=estado
        )

        if not familias:
            self.logger.warning(
                "[FamiliaManager] ⚠️ No se encontraron familias con los filtros aplicados"
            )
        else:
            self.logger.info(
                f"[FamiliaManager] ✅ {len(familias)} familia(s) encontradas"
            )

        return familias

    def get_familias_leaderdata(self, page: int, page_size: int) -> list:
        """
        Obtiene la lista de familias con su líder, parcialidad y número de miembros.
        """
        self.logger.info("[FamiliaManager] Consultando dashboard de familias")

        result = self.familia_repository.get_familias_dashboard(
            page, page_size)

        self.logger.info(
            f"[FamiliaManager] Se obtuvieron {len(result)} familias para el dashboard")
        return result

    def get_miembros_familia(self, id_familia: int, query: Optional[str], page: int, page_size: int):
        self.logger.info(
            f"[FamiliaManager] Consultando miembros de la familia {id_familia} (query='{query}')")
        result = self.familia_repository.get_miembros_familia(
            id_familia, query, page, page_size)
        self.logger.info(
            f"[FamiliaManager] Miembros encontrados: {result['total_items']}")
        return result

    def get_familia_resumen(self, id_familia: int) -> FamiliaResumenOut:
        """
        Retorna la información resumen de una familia.
        """
        self.logger.info(
            f"[FamiliaManager] Consultando resumen de familia {id_familia}")
        return self.familia_repository.get_familia_resumen(id_familia)

    def _validar_familia(self, data: FamiliaCreate) -> None:
        """
        Valida datos antes de crear una familia.
        """
        self.logger.debug(
            f"[FamiliaManager] Validando datos de familia: {data.model_dump(exclude_none=True)}")

        if data.idFamilia:
            familia_exist = self.familia_repository.get(data.idFamilia)
            if familia_exist:
                self.logger.error(
                    f"[FamiliaManager] La familia con ID {data.idFamilia} ya existe en base de datos")
                raise AppException("La familia ya existe")

        if data.estado and data.estado not in EnumEstadoFamilia:
            self.logger.error(
                f"[FamiliaManager] Estado inválido recibido: {data.estado}")
            raise AppException(f"Estado de familia inválido: {data.estado}")

        if data.representanteId is not None:
            self.logger.debug(
                f"[FamiliaManager] Verificando existencia del representante con ID {data.representanteId}")

            representante_exist = self.persona_repository.get(
                data.representanteId)
            if not representante_exist:
                self.logger.error(
                    f"[FamiliaManager] ❌ No existe la persona con ID {data.representanteId} para asignar como líder")
                raise AppException(
                    f"No existe la persona con ID {data.representanteId} para asignar como líder")
            miembro_familia = self.miembro_repository.get_familia_actual(
                data.representanteId)
            if miembro_familia is not None:
                raise AppException(
                    f"La persona con ID {data.representanteId} ya forma parte de una familia no se puede asignar como líder")
            self.logger.info(
                f"[FamiliaManager] ✅ Representante válido encontrado: {data.representanteId}")

        self.logger.debug(
            "[FamiliaManager] Validación de familia completada correctamente")

    def get_estadisticas_generales(self) -> EstadisticaGeneralOut:
        """
        Obtiene las estadísticas generales del sistema.
        """
        self.logger.info(
            "[FamiliaManager] Consultando estadísticas generales del sistema")
        data = self.familia_repository.get_estadisticas_generales()
        return EstadisticaGeneralOut(**data)
