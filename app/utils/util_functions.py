import secrets
import string
def generate_recovery_code(length: int = 6) -> str:
    characters = string.ascii_uppercase + string.digits  # A-Z and 0-9
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_temporary_password(length: int = 10) -> str:
    """Genera una contraseña provisional segura."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

from typing import Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta  # tipo de modelos Base

def apply_filters(
    session: Session,
    model: Type[DeclarativeMeta],
    filters: Dict[str, Any]
):
    """
    Aplica filtros dinámicos con AND.
    Solo se consideran los filtros enviados en el diccionario.
    """
    query = session.query(model)

    if filters:
        for campo, valor in filters.items():
            if hasattr(model, campo):
                query = query.filter(getattr(model, campo) == valor)

    return query
