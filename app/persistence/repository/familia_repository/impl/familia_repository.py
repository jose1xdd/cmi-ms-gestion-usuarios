from typing import List, Optional
from sqlalchemy import or_, func, text, case
from sqlalchemy.orm import Session, aliased, joinedload
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.models.outputs.familia.familia_output import FamiliaDataLeader, FamiliaResumenOut
from app.models.outputs.persona.persona_output import PersonaFamiliaOut
from app.persistence.model.familia import Familia
from app.persistence.model.parcialidad import Parcialidad
from app.persistence.model.persona import Persona
from app.persistence.repository.base_repository.impl.base_repository import BaseRepository
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
from app.utils.exceptions_handlers.models.error_response import AppException


class FamiliaRepository(BaseRepository, IFamiliaRepository):
    def __init__(self, db: Session):
        # Llamar al constructor de la clase base
        super().__init__(Familia, db)

    def bulk_insert(self, familias: List[FamiliaCreate]) -> int:
        for familia in familias:
            self.create(
                Familia(integrantes=0, id=familia.idFamilia)
            )
        return len(familias)

    def search_by_representante(self, page: int, page_size: int, query: str):
        """
        Busca familias cuyo representante coincida parcialmente por documento, nombre o apellido.
        Si el query está vacío, retorna todas las familias.
        """
        query = query.strip() if query else ""

        base_query = (
            self.db.query(Familia)
            .join(Persona, Familia.representante_id == Persona.id)
            .options(joinedload(Familia.representante), joinedload(Familia.personas))
            .order_by(Persona.apellido, Persona.nombre)
        )

        # Si no hay query, no aplicar filtros
        if not query:
            return self.paginate(page, page_size, base_query)

        like_query = f"%{query}%"
        filtered_query = base_query.filter(
            or_(
                Persona.id.like(like_query),
                func.lower(Persona.nombre).like(func.lower(like_query)),
                func.lower(Persona.apellido).like(func.lower(like_query)),
            )
        )

        return self.paginate(page, page_size, filtered_query)

    def get_familias_dashboard(self, page: int, page_size: int):
        """
        Consulta familias con su líder y parcialidad, usando paginate()
        y luego convierte los resultados a FamiliaDataLeader.
        """
        persona_lider = aliased(Persona)
        persona_miembro = aliased(Persona)

        # Construimos la query
        query = (
            self.db.query(
                Familia.id.label("id"),
                persona_lider.nombre.label("lider_nombre"),
                persona_lider.apellido.label("lider_apellido"),
                persona_lider.id.label("cedula"),
                Parcialidad.nombre.label("parcialidad"),
                func.count(persona_miembro.id).label("miembros"),
                Familia.estado.label("estado"),
            )
            .join(persona_lider, persona_lider.id == Familia.representante_id)
            .outerjoin(persona_miembro, persona_miembro.idFamilia == Familia.id)
            .outerjoin(Parcialidad, Parcialidad.id == persona_lider.idParcialidad)
            .group_by(
                Familia.id,
                persona_lider.nombre,
                persona_lider.apellido,
                persona_lider.id,
                Parcialidad.nombre,
                Familia.estado,
            )
        )

        result = self.paginate(page, page_size, query)

        result["items"] = [
            FamiliaDataLeader(
                id=row.id,
                lider_nombre=row.lider_nombre,
                lider_apellido=row.lider_apellido,
                cedula=row.cedula,
                parcialidad=row.parcialidad,
                miembros=row.miembros,
                estado=row.estado.value if hasattr(
                    row.estado, "value") else row.estado,
            )
            for row in result["items"]
        ]

        return result

    def get_miembros_familia(self, id_familia: int, query: Optional[str], page: int, page_size: int):
        """
        Devuelve los miembros de una familia con información detallada:
        nombre, parentesco, parcialidad, cédula, edad y estado (ACTIVO/FALLECIDO).
        """
        # 🔹 Calculamos edad (MySQL)
        edad_expr = func.timestampdiff(
            text("YEAR"), Persona.fechaNacimiento, func.current_date())

        # 🔹 Calculamos estado (CASE SQL)
        estado_expr = case(
            (Persona.fechaDefuncion.isnot(None), "FALLECIDO"),
            else_="ACTIVO"
        ).label("estado")

        # 🔹 Query principal
        q = (
            self.db.query(
                Persona.id.label("id"),
                Persona.nombre.label("nombre"),
                Persona.apellido.label("apellido"),
                Persona.parentesco.label("parentesco"),
                Parcialidad.nombre.label("parcialidad"),
                Persona.id.label("cedula"),
                edad_expr.label("edad"),
                estado_expr,
            )
            .outerjoin(Parcialidad, Parcialidad.id == Persona.idParcialidad)
            .filter(Persona.idFamilia == id_familia)
        )

        # 🔍 Búsqueda flexible
        if query:
            q = q.filter(
                or_(
                    Persona.nombre.ilike(f"%{query}%"),
                    Persona.apellido.ilike(f"%{query}%"),
                    Persona.id.like(f"%{query}%"),
                )
            )

        # 🔹 Paginación estándar
        result = self.paginate(page, page_size, q)

        # 🔹 Mapeo a modelo Pydantic
        result["items"] = [
            PersonaFamiliaOut(
                id=row.id,
                nombre=row.nombre,
                apellido=row.apellido,
                parentesco=row.parentesco,
                parcialidad=row.parcialidad,
                cedula=row.cedula,
                edad=row.edad,
                estado=row.estado,
            )
            for row in result["items"]
        ]

        return result

    def get_familia_resumen(self, id_familia: int) -> FamiliaResumenOut:
        """
        Devuelve un resumen con los datos principales de una familia.
        Incluye líder, parcialidad, total de miembros, miembros activos y defunciones.
        """
        persona_lider = aliased(Persona)
        persona_miembro = aliased(Persona)

        query = (
            self.db.query(
                Familia.id.label("id"),
                func.concat(persona_lider.nombre, " ",
                            persona_lider.apellido).label("lider_familia"),
                Parcialidad.nombre.label("parcialidad"),
                func.count(persona_miembro.id).label("total_miembros"),
                func.sum(func.if_(persona_miembro.fechaDefuncion.is_(
                    None), 1, 0)).label("miembros_activos"),
                func.sum(func.if_(persona_miembro.fechaDefuncion.isnot(
                    None), 1, 0)).label("defunciones"),
            )
            .join(persona_lider, persona_lider.id == Familia.representante_id)
            .outerjoin(persona_miembro, persona_miembro.idFamilia == Familia.id)
            .outerjoin(Parcialidad, Parcialidad.id == persona_lider.idParcialidad)
            .filter(Familia.id == id_familia)
            .group_by(Familia.id, persona_lider.nombre, persona_lider.apellido, Parcialidad.nombre)
        )

        result = query.first()
        if not result:
            raise AppException("Familia no encontrada")

        return FamiliaResumenOut(
            id=result.id,
            lider_familia=result.lider_familia,
            parcialidad=result.parcialidad,
            total_miembros=result.total_miembros or 0,
            miembros_activos=result.miembros_activos or 0,
            defunciones=result.defunciones or 0,
        )

    def get_estadisticas_generales(self) -> dict:
        """
        Devuelve el total de familias y el total de personas registradas.
        """
        total_familias = self.db.query(func.count(Familia.id)).scalar() or 0
        total_personas = self.db.query(func.count(Persona.id)).scalar() or 0

        return {
            "total_familias": total_familias,
            "total_personas": total_personas
        }
