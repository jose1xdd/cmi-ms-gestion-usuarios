from fastapi import Request, Depends

from app.utils.exceptions_handlers.models.error_response import AppException


def validar_persona_admin(path_param_key: str = "persona_id"):
    def dependency(request: Request):
        headers = request.headers
        role = headers.get("role")
        header_persona_id = headers.get("persona_id")
        path_persona_id = request.path_params.get(path_param_key)

        if header_persona_id != path_persona_id and role != "admin":
            raise AppException(
                codigo_http=403, mensaje="No autorizado: rol inválido")

        return True  # Devuelve algo si se necesita

    return Depends(dependency)
