import logging

from app.persistence.model.familia import Familia
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository


class FamiliaManager():
    def __init__(self,
                 familia_repository: IFamiliaRepository,
                 logger: logging.Logger):
        self.familia_repository = familia_repository
        self.logger = logger

    def create(self):
        return self.familia_repository.create(Familia(integrantes=0))
