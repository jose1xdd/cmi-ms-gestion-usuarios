import logging
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.models.outputs.familia.familia_output import FamiliaOut
from app.models.outputs.paginated_response import PaginatedFamilias
from app.models.outputs.response_estado import EstadoResponse
from app.persistence.model.familia import Familia
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
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
        if not data.idFamilia:
            familia = self.familia_repository.create(Familia(integrantes=0))
            self.logger.info(
                f"Familia creada con ID auto-generado: {familia.id}")
            return EstadoResponse(
                estado="success",
                message="Familia creada exitosamente",
                data=familia
            )

        familia_exist = self.familia_repository.get(data.idFamilia)
        if familia_exist:
            self.logger.error(
                f"El número de familia ya existe: {data.idFamilia}")
            raise AppException("La Familia a crear ya existe")

        familia = self.familia_repository.create(
            Familia(integrantes=0, id=data.idFamilia))
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
