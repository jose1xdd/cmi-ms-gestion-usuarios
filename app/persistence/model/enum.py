from enum import Enum


class EnumDocumento(Enum):
    CC = "CC"
    TI = "TI"
    CE = "CE"


class EnumRol(Enum):
    admin = "admin"
    usuario = "usuario"


class EnumSexo(Enum):
    M = "M"
    F = "F"


class EnumParentesco(Enum):
    PA = "PA"  # Padre
    MA = "MA"  # Madre
    HI = "HI"  # Hijo(a)
    AB = "AB"  # Abuelo(a)
    SO = "SO"  # Sobrino(a)
    CU = "CU"  # Cuñado(a)
    YR = "YR"  # Yerno / Nuera
    CF = "CF"  # Cónyuge / Familiar
    HE = "HE"  # Hermano(a)


class EnumEscolaridad(Enum):
    NI = "NI"   # Ninguna
    PR = "PR"   # Primaria
    SE = "SE"   # Secundaria
    UN = "UN"   # Universitaria

class EnumEstadoFamilia(str, Enum):
    ACTIVA = "ACTIVA"
    INACTIVA = "INACTIVA"
