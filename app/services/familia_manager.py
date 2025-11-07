import logging
from typing import List, Optional
import numpy as np
import pandas as pd
import io

from fastapi import UploadFile
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.models.inputs.persona.persona_carga_masiva import CargaMasivaResponse, ErrorPersonaOut
from app.models.inputs.persona.persona_update import PersonaUpdate
from app.models.outputs.familia.familia_output import FamiliaOut, FamiliaResumenOut
from app.models.outputs.paginated_response import PaginatedFamilias
from app.models.outputs.persona.persona_output import EstadisticaGeneralOut
from app.models.outputs.response_estado import EstadoResponse
from app.persistence.model.familia import Familia
from app.persistence.model.enum import EnumEstadoFamilia
from app.persistence.model.persona import Persona
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
from app.persistence.repository.persona_repository.interface.interface_persona_repository import IPersonaRepository
from app.utils.constans import COLUMNS_FAMILIA
from app.utils.exceptions_handlers.models.error_response import AppException


class FamiliaManager:
    def __init__(self, familia_repository: IFamiliaRepository,
                 persona_repository: IPersonaRepository,
                 logger: logging.Logger):
        self.familia_repository: IFamiliaRepository = familia_repository
        self.persona_repository: IPersonaRepository = persona_repository
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
                representante_id=data.representante_id,
                estado=data.estado or EnumEstadoFamilia.ACTIVA
            )

            created = self.familia_repository.create(familia)

            if data.representante_id:
                self.logger.info(
                    f"[FamiliaManager] Asignando representante {data.representante_id} a la familia {created.id}")
                persona = PersonaUpdate(idFamilia=created.id)
                persona = self.persona_repository.update(
                    data.representante_id, persona)
                self.logger.info(
                    f"[FamiliaManager] ✅ Representante {persona.id} asignado correctamente a la familia {created.id}"
                )
            self.logger.info(
                f"[FamiliaManager] ✅ Familia creada exitosamente | ID: {created.id}, "
                f"Estado: {created.estado}, Representante: {created.representante_id}"
            )

            return EstadoResponse(
                estado="success",
                message="Familia creada exitosamente",
                data=created.to_dict()
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
        result = self.familia_repository.paginate(page, page_size)
        self.logger.info(
            f"[FamiliaManager] ✅ Consulta completada | Total familias en página: {result.__len__()}")
        return result

    def get_familia(self, familia_id: int) -> FamiliaOut:
        self.logger.info(
            f"[FamiliaManager] Buscando familia con ID: {familia_id}")
        familia = self.familia_repository.get(familia_id)

        if familia is None:
            self.logger.warning(
                f"[FamiliaManager] ⚠️ Familia con ID {familia_id} no encontrada")
            raise AppException("Familia no encontrada", 404)

        self.logger.info(
            f"[FamiliaManager] ✅ Familia encontrada | ID: {familia.id}, "
            f"Estado: {familia.estado}, Representante: {familia.representante_id}"
        )
        return familia

    async def upload_excel(self, file: UploadFile) -> CargaMasivaResponse:
        self.logger.info(
            f"[FamiliaManager] Iniciando carga masiva de familias desde archivo: {file.filename}")

        try:
            content = await file.read()
            df = pd.read_excel(io.BytesIO(content))
            self.logger.info(
                f"[FamiliaManager] Archivo leído correctamente | Filas detectadas: {len(df)}")

            # Validar columnas requeridas
            missing = [col for col in COLUMNS_FAMILIA if col not in df.columns]
            if missing:
                self.logger.error(
                    f"[FamiliaManager] ❌ Faltan columnas requeridas en Excel: {missing}")
                return CargaMasivaResponse(
                    status="error",
                    errores=[ErrorPersonaOut(
                        fila=0, id=None, mensaje=f"Faltan columnas: {missing}")]
                )

            df = df.replace({np.nan: None})
            familias: List[FamiliaCreate] = []
            errores: List[ErrorPersonaOut] = []

            for i, row in df.iterrows():
                try:
                    familia = FamiliaCreate(**row.to_dict())
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
                    f"[FamiliaManager] Insertando {len(familias)} familias válidas en base de datos...")
                insertados = self.familia_repository.bulk_insert(familias)
                self.logger.info(
                    f"[FamiliaManager] ✅ Inserción masiva completada. Familias insertadas: {insertados}")

            total = len(familias) + len(errores)
            self.logger.info(
                f"[FamiliaManager] Carga masiva finalizada | Total procesados: {total}, Errores: {len(errores)}")

            return CargaMasivaResponse(
                status="ok",
                insertados=insertados,
                total_procesados=total,
                errores=errores,
            )

        except Exception as e:
            self.logger.exception(
                f"[FamiliaManager] ❌ Error procesando archivo Excel: {e}")
            return CargaMasivaResponse(
                status="error",
                errores=[ErrorPersonaOut(fila=0, id=None, mensaje=str(e))],
            )

    def search_familia_by_lider(self, query: str, page: int, page_size: int) -> list[FamiliaOut]:
        """
        Busca familias por coincidencia parcial en los datos del representante (documento, nombre o apellido).
        """
        self.logger.info(
            f"[FamiliaManager] 🔍 Buscando familia por datos del representante con query='{query}'")

        familias = self.familia_repository.search_by_representante(
            page, page_size, query)

        if not familias:
            self.logger.warning(
                f"[FamiliaManager] ⚠️ No se encontraron familias para query='{query}'")
        else:
            self.logger.info(
                f"[FamiliaManager] ✅ {len(familias)} familia(s) encontradas para query='{query}'")

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

        if data.representante_id:
            self.logger.debug(
                f"[FamiliaManager] Verificando existencia del representante con ID {data.representante_id}")

            representante_exist = self.persona_repository.get(
                data.representante_id)
            if not representante_exist:
                self.logger.error(
                    f"[FamiliaManager] ❌ No existe la persona con ID {data.representante_id} para asignar como líder")
                raise AppException(
                    f"No existe la persona con ID {data.representante_id} para asignar como líder")
            if representante_exist.idFamilia != None:
                raise AppException(
                    f"La persona con ID {data.representante_id} ya forma parte de una familia no se puede asignar como líder")
            self.logger.info(
                f"[FamiliaManager] ✅ Representante válido encontrado: {data.representante_id}")

        self.logger.debug(
            "[FamiliaManager] Validación de familia completada correctamente")
    
    def get_estadisticas_generales(self) -> EstadisticaGeneralOut:
        """
        Obtiene las estadísticas generales del sistema.
        """
        self.logger.info("[FamiliaManager] Consultando estadísticas generales del sistema")
        data = self.familia_repository.get_estadisticas_generales()
        return EstadisticaGeneralOut(**data)