from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from app.config.database import Base
from sqlalchemy.orm import relationship
from app.persistence.model.enum import EnumEstadoFamilia


class Familia(Base):
    __tablename__ = 'Familia'

    id = Column(Integer, primary_key=True, autoincrement=True)
    representante_id = Column(
        String(36), ForeignKey('Persona.id'), nullable=True)
    estado = Column(Enum(EnumEstadoFamilia),
                    default=EnumEstadoFamilia.ACTIVA, nullable=False)
    # Relaciones
    personas = relationship(
        "Persona",
        back_populates="familia",
        foreign_keys="Persona.idFamilia"
    )

    representante = relationship(
        "Persona",
        foreign_keys=[representante_id],
        uselist=False
    )

    def __repr__(self):
        return f"<Familia(id={self.id}, estado={self.estado}, representante_id={self.representante_id})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "representante_id": self.representante_id,
            "estado": self.estado.value if self.estado else None
        }
