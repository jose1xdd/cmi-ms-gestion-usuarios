import logging
from typing import List
import numpy as np
import pandas as pd
import io

from fastapi import UploadFile
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.models.inputs.persona.persona_carga_masiva import CargaMasivaResponse, ErrorPersonaOut
from app.models.outputs.familia.familia_output import FamiliaOut
from app.models.outputs.paginated_response import PaginatedFamilias
from app.models.outputs.response_estado import EstadoResponse
from app.persistence.model.familia import Familia
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
from app.utils.constans import COLUMNS_FAMILIA
from app.utils.exceptions_handlers.models.error_response import AppException


class FamiliaManager:
    def __init__(
        self,
        familia_repository: IFamiliaRepository,
        logger: logging.Logger
    ):
        self.familia_repository = familia_repository
        self.logger = logger

    def create(self, data: FamiliaCreate) -> EstadoResponse:
        """
        Crea una familia después de validar.
        """
        # Paso 1: Validar
        self._validar_familia(data)

        # Paso 2: Crear familia
        if not data.idFamilia:
            familia = self.familia_repository.create(Familia(integrantes=0))
            self.logger.info(
                f"Familia creada con ID auto-generado: {familia.id}"
            )
            return EstadoResponse(
                estado="success",
                message="Familia creada exitosamente",
                data=familia
            )

        # Si se proporciona idFamilia y pasó validación
        familia = self.familia_repository.create(
            Familia(integrantes=0, id=data.idFamilia)
        )
        self.logger.info(f"Familia creada con ID específico: {data.idFamilia}")
        return EstadoResponse(
            estado="success",
            message="Familia creada exitosamente",
            data=familia
        )

    def delete(self, familia_id: int) -> EstadoResponse:
        self.logger.info(f"Intentando eliminar familia con ID: {familia_id}")
        result = self.familia_repository.delete(familia_id)
        if not result:
            self.logger.warning(f"No se encontró familia con ID: {familia_id}")
            raise AppException("No se encontró la familia para eliminar")

        self.logger.info(f"Familia eliminada con éxito: {familia_id}")
        return EstadoResponse(
            estado="success",
            message="Familia eliminada exitosamente"
        )

    def get_familias(self, page: int, page_size: int) -> PaginatedFamilias:
        self.logger.info(
            f"Obteniendo familias - Página: {page}, Tamaño: {page_size}")
        return self.familia_repository.paginate(page, page_size)

    def get_familia(self, familia_id: int) -> FamiliaOut:
        familia = self.familia_repository.get(familia_id)
        if familia is None:
            raise AppException("Familia no Encontrada", 404)
        return familia

    async def upload_excel(self, file: UploadFile) -> CargaMasivaResponse:
        try:

            content = await file.read()
            df = pd.read_excel(io.BytesIO(content))
            missing = [col for col in COLUMNS_FAMILIA if col not in df.columns]
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
            df["idFamilia"] = df["idFamilia"].astype(str)
            df = df.replace({np.nan: None})
            familias: List[FamiliaCreate] = []
            errores: List[ErrorPersonaOut] = []
            for i, row in df.iterrows():
                try:
                    familia = FamiliaCreate(**row.to_dict())
                    self._validar_familia(familia)
                    familias.append(familia)
                except Exception as e:
                    errores.append(
                        ErrorPersonaOut(
                            fila=i + 2,  # +2 porque Excel empieza en 1 y fila 1 es header
                            id=str(row.get("idFamilia")) if row.get(
                                "idFamilia") else None,
                            mensaje=str(e),
                        )
                    )
            insertados = 0
            if familias:
                insertados = self.familia_repository.bulk_insert(familias)
            return CargaMasivaResponse(
                status="ok",
                insertados=insertados,
                total_procesados=len(familias) + len(errores),
                errores=errores,
            )

        except Exception as e:
            return CargaMasivaResponse(
                status="error",
                errores=[ErrorPersonaOut(fila=0, id=None, mensaje=str(e))],
            )

    def _validar_familia(self, data: FamiliaCreate) -> None:
        """
        Valida la creación de una familia antes de persistirla.
        Lanza AppException si encuentra algún error.
        """
        if data.idFamilia:
            familia_exist = self.familia_repository.get(data.idFamilia)
            if familia_exist:
                self.logger.error(
                    f"El número de familia ya existe: {data.idFamilia}"
                )
                raise AppException("La Familia a crear ya existe")
