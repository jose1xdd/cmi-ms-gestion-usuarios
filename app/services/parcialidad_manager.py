
import io
import logging
import pandas as pd
import numpy as np
from fastapi import UploadFile
from typing import Any, Dict, List
from app.models.inputs.parcialidad.parcialidad_create import ParcialidadCreate
from app.models.inputs.persona.persona_carga_masiva import CargaMasivaResponse, ErrorPersonaOut
from app.models.outputs.response_estado import EstadoResponse
from app.persistence.model.parcialidad import Parcialidad
from app.persistence.repository.parcialidad_repository.interface.interface_parcialidad_repository import IParcialiadRepository
from app.utils.constans import COLUMNS_PARCIALIDAD
from app.utils.exceptions_handlers.models.error_response import AppException


class ParcialidadManager():

    def __init__(self,
                 parcialidad_repository: IParcialiadRepository,
                 logger: logging.Logger):
        self.parcialidad_repository: IParcialiadRepository = parcialidad_repository
        self.logger: logging.Logger = logger

    def create(self, data: ParcialidadCreate):
        self._validar_parcialidad(data)
        self.parcialidad_repository.create(
            Parcialidad(nombre=data.nombre_parcialidad))
        return EstadoResponse(estado="Exitoso",
                              message="Parcialidad creada exitosamente")

    def delete(self, parcialidad_id: int):
        parcialidad = self.parcialidad_repository.get(parcialidad_id)
        if parcialidad is None:
            raise AppException(
                f"No existe una parcialidad con ese id : {parcialidad_id}")
        self.parcialidad_repository.delete(parcialidad.id)
        return EstadoResponse(estado="Exitoso",
                              message="Parcialidad eliminada exitosamente")

    def get_parcialidades(self, page: int, page_size: int, filters: Dict[str, Any]):
        parcialidades = self.parcialidad_repository.find_by_params(
            page, page_size, filters)
        return parcialidades

    def get_parcialidad_by_id(self, id: int):
        parcialidad = self.parcialidad_repository.get(id)
        if parcialidad is None:
            raise AppException("Parcialidad no Encontrada", 404)
        return parcialidad

    def update_parcialidad_by_id(self, id: int, parcialidad_data: ParcialidadCreate):
        parcialidad = self.parcialidad_repository.get(id)
        if parcialidad is None:
            raise AppException("Parcialidad a actualizar no existe")
        parcialidad_name = self.parcialidad_repository.find_by_name(
            parcialidad_data.nombre_parcialidad)
        if parcialidad_name is not None:
            raise AppException("ya existe una parcialidad con ese nombre")
        parcialidad.nombre = parcialidad_data.nombre_parcialidad
        self.parcialidad_repository.update(id, parcialidad)
        return EstadoResponse(estado="Exitoso", message="Parcialidad actualizada exitosamente")

    async def upload_excel(self, file: UploadFile) -> CargaMasivaResponse:
        try:
            content = await file.read()
            df = pd.read_excel(io.BytesIO(content))

            # ✅ Validar columnas requeridas
            missing = [
                col for col in COLUMNS_PARCIALIDAD if col not in df.columns]
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

            df = df.replace({np.nan: None})  # NaN → None

            parcialidades: List[ParcialidadCreate] = []
            errores: List[ErrorPersonaOut] = []

            for i, row in df.iterrows():
                try:
                    data = ParcialidadCreate(**row.to_dict())
                    self._validar_parcialidad(data)
                    parcialidades.append(Parcialidad(
                        nombre=data.nombre_parcialidad))

                except Exception as e:
                    errores.append(
                        ErrorPersonaOut(
                            fila=i + 2,  # Excel fila
                            id=None,
                            mensaje=str(e),
                        )
                    )

            insertados = 0
            if parcialidades:
                insertados = self.parcialidad_repository.bulk_insert(
                    parcialidades)

            return CargaMasivaResponse(
                status="ok",
                insertados=insertados,
                total_procesados=len(parcialidades) + len(errores),
                errores=errores,
            )

        except Exception as e:
            return CargaMasivaResponse(
                status="error",
                errores=[ErrorPersonaOut(fila=0, id=None, mensaje=str(e))],
            )

    def _validar_parcialidad(self, data: ParcialidadCreate) -> None:
        parcialidad = self.parcialidad_repository.find_by_name(
            data.nombre_parcialidad)
        if parcialidad is not None:
            raise AppException(
                f"Ya existe una parcialidad con el nombre '{data.nombre_parcialidad}'")
