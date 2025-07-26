from sqlalchemy import Boolean, Enum, Column, ForeignKey, String, Integer, Date
from app.config.database import Base
from app.persistence.model.enum import EnumDocumento, EnumEscolaridad, EnumParentesco, EnumSexo
from sqlalchemy.orm import relationship



class Persona(Base):
    __tablename__ = 'Persona'
    
    id = Column(String(36), primary_key=True)
    tipoDocumento = Column(Enum(EnumDocumento))
    nombre = Column(String(50))
    apellido = Column(String(50))
    fechaNacimiento = Column(Date)
    parentesco = Column(Enum(EnumParentesco))
    sexo = Column(Enum(EnumSexo))
    profesion = Column(String(100), nullable=True)
    escolaridad = Column(Enum(EnumEscolaridad))
    direccion = Column(String(200))
    telefono = Column(String(20))
    activo = Column(Boolean, default=True, nullable=False)
    idFamilia = Column(Integer, ForeignKey('Familia.id'))
    idParcialidad = Column(Integer, ForeignKey('Parcialidad.id'))

    familia = relationship("Familia", back_populates="personas")
    parcialidad = relationship("Parcialidad", back_populates="personas")

    # Relación uno a uno con Usuario (definido en otro archivo)
    usuario = relationship("Usuario", back_populates="persona", uselist=False)