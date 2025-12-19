from typing import List, Optional
from sqlalchemy import and_, or_, func, text, case
from sqlalchemy.orm import Session, aliased, joinedload
from app.models.inputs.familia.familia_create import FamiliaCreate
from app.models.outputs.familia.familia_output import FamiliaDataLeader, FamiliaOut, FamiliaResumenOut
from app.models.outputs.persona.persona_output import PersonaFamiliaOut, PersonaOut
from app.persistence.model.enum import EnumEstadoFamilia
from app.persistence.model.familia import Familia
from app.persistence.model.miembro_familia import MiembroFamilia
from app.persistence.model.parcialidad import Parcialidad
from app.persistence.model.persona import Persona
from app.persistence.repository.base_repository.impl.base_repository import BaseRepository
from app.persistence.repository.familia_repository.interface.interface_familia_repository import IFamiliaRepository
from app.utils.exceptions_handlers.models.error_response import AppException


class FamiliaRepository(BaseRepository, IFamiliaRepository):
    def __init__(self, db: Session):
        # Llamar al constructor de la clase base
        super().__init__(Familia, db)

    def get_familia_by_id(self, id_familia: int) -> FamiliaOut:
        representante = aliased(Persona)

        # Query principal
        familia = (
            self.db.query(Familia)
            .outerjoin(
                MiembroFamilia,
                and_(
                    MiembroFamilia.familiaId == Familia.id,
                    MiembroFamilia.esRepresentante == True,
                    MiembroFamilia.activo == True,
                )
            )
            .outerjoin(
                representante,
                representante.id == MiembroFamilia.personaId
            )
            .filter(Familia.id == id_familia)
            .first()
        )

        if not familia:
            return None

        # Obtener el miembro líder activo
        miembro_lider = next(
            (m for m in familia.miembros if m.esRepresentante and m.activo), None
        )

        representante_id = miembro_lider.personaId if miembro_lider else None
        persona_obj = PersonaOut.from_orm(
            miembro_lider.persona) if miembro_lider else None

        return FamiliaOut(
            id=familia.id,
            estado=familia.estado,
            fechaCreacion=familia.fechaCreacion,
            representanteId=representante_id,
            representante=persona_obj,
        )

    def get_familias_con_lider(self, page: int, page_size: int):
        representante = aliased(Persona)

        # Query: solo trae familias y representante activo
        query = (
            self.db.query(Familia, MiembroFamilia, representante)
            .outerjoin(
                MiembroFamilia,
                (MiembroFamilia.familiaId == Familia.id) &
                (MiembroFamilia.esRepresentante == 1) &
                (MiembroFamilia.activo == 1)
            )
            .outerjoin(
                representante,
                representante.id == MiembroFamilia.personaId
            )
            .order_by(Familia.id)
        )

        # Paginar resultados
        result = self.paginate(query=query, page=page, page_size=page_size)

        items = []
        for familia, miembro, persona in result['items']:
            familia_out = FamiliaOut(
                id=familia.id,
                estado=familia.estado,
                fechaCreacion=familia.fechaCreacion,
                representanteId=persona.id if persona else None,
                representante=PersonaOut.from_orm(persona) if persona else None
            )
            items.append(familia_out)

        return {
            "total_items": result['total_items'],
            "current_page": result['current_page'],
            "total_pages": result['total_pages'],
            "items": items
        }

    def bulk_insert(self, familias: List[FamiliaCreate]) -> int:
        for familia in familias:
            self.create(
                Familia(id=familia.idFamilia)
            )
        return len(familias)

    def search_by_representante(
        self,
        page: int,
        page_size: int,
        query: str,
        parcialidad_id: int | None = None,
        rango_miembros: str | None = None,
        estado: EnumEstadoFamilia | None = None
    ):
        query_str = query.strip() if query else ""

        # Aliases
        representante = aliased(Persona)
        miembro_rep = aliased(MiembroFamilia)

        # Base query: familias + representante activo
        base_query = (
            self.db.query(Familia, miembro_rep, representante)
            .outerjoin(
                miembro_rep,
                (miembro_rep.familiaId == Familia.id) &
                (miembro_rep.esRepresentante == 1) &
                (miembro_rep.activo == 1)
            )
            .outerjoin(
                representante,
                representante.id == miembro_rep.personaId
            )
        )

        # --- FILTRO POR QUERY ---
        if query_str:
            like_query = f"%{query_str}%"
            base_query = base_query.filter(
                or_(
                    representante.id.like(like_query),
                    func.lower(representante.nombre).like(
                        func.lower(like_query)),
                    func.lower(representante.apellido).like(
                        func.lower(like_query))
                )
            )

        # --- FILTRO POR PARCIALIDAD ---
        if parcialidad_id is not None:
            base_query = base_query.filter(
                representante.idParcialidad == parcialidad_id)

        # --- FILTRO POR ESTADO ---
        if estado is not None:
            base_query = base_query.filter(Familia.estado == estado)

        # --- FILTRO POR CANTIDAD DE MIEMBROS ---
        if rango_miembros:
            subq = (
                self.db.query(
                    MiembroFamilia.familiaId.label("fam_id"),
                    func.count(MiembroFamilia.id).label("num_miembros")
                )
                .group_by(MiembroFamilia.familiaId)
                .subquery()
            )
            base_query = base_query.outerjoin(
                subq, subq.c.fam_id == Familia.id)

            if rango_miembros == "1-3":
                base_query = base_query.filter(
                    subq.c.num_miembros.between(1, 3))
            elif rango_miembros == "4-6":
                base_query = base_query.filter(
                    subq.c.num_miembros.between(4, 6))
            elif rango_miembros == "7+":
                base_query = base_query.filter(subq.c.num_miembros >= 7)

        # Orden
        base_query = base_query.order_by(Familia.id)

        # Ejecutar paginación
        result = self.paginate(
            query=base_query, page=page, page_size=page_size)

        # Mapear a Pydantic dentro de la sesión
        items = []
        for familia, miembro, persona in result['items']:
            familia_out = FamiliaOut(
                id=familia.id,
                estado=familia.estado,
                fechaCreacion=familia.fechaCreacion,
                representanteId=persona.id if persona else None,
                representante=PersonaOut.from_orm(persona) if persona else None
            )
            items.append(familia_out)

        return {
            "total_items": result['total_items'],
            "current_page": result['current_page'],
            "total_pages": result['total_pages'],
            "items": items
        }

    def get_familias_dashboard(self, page: int, page_size: int):
        """
        Consulta familias con su líder y parcialidad, usando paginate()
        y luego convierte los resultados a FamiliaDataLeader.
        """
        # Aliases
        lider = aliased(Persona)
        miembro = aliased(Persona)
        miembro_familia = aliased(MiembroFamilia)

        # Query principal
        query = (
            self.db.query(
                Familia.id.label("id"),
                lider.nombre.label("lider_nombre"),
                lider.apellido.label("lider_apellido"),
                lider.id.label("cedula"),
                Parcialidad.nombre.label("parcialidad"),
                func.count(miembro.id).label("miembros"),
                Familia.fechaCreacion.label("fechaCreacion"),
                Familia.estado.label("estado")

            )
            # LÍDER: unir solo MiembroFamilia activo y representante
            .join(
                miembro_familia,
                (miembro_familia.familiaId == Familia.id) &
                (miembro_familia.esRepresentante == 1) &
                (miembro_familia.activo == 1)
            )
            .join(lider, lider.id == miembro_familia.personaId)
            # PARCIALIDAD del líder
            .outerjoin(Parcialidad, Parcialidad.id == lider.idParcialidad)
            # CONTAR MIEMBROS
            .outerjoin(
                MiembroFamilia,
                (MiembroFamilia.familiaId == Familia.id) &
                (MiembroFamilia.activo == 1)
            )
            .outerjoin(miembro, miembro.id == MiembroFamilia.personaId)
            .group_by(
                Familia.id,
                lider.nombre,
                lider.apellido,
                lider.id,
                Parcialidad.nombre,
                Familia.estado
            )
            .order_by(Familia.id)
        )

        # Ejecutar paginación
        result = self.paginate(page, page_size, query)

        # Mapear a Pydantic
        result["items"] = [
            FamiliaDataLeader(
                id=row.id,
                lider_nombre=row.lider_nombre,
                lider_apellido=row.lider_apellido,
                cedula=row.cedula,
                parcialidad=row.parcialidad,
                miembros=row.miembros,
                fechaCreacion=row.fechaCreacion,
                estado=row.estado.value if hasattr(
                    row.estado, "value") else row.estado
            )
            for row in result["items"]
        ]

        return result

    def get_miembros_familia(self, id_familia: int, query: Optional[str], page: int, page_size: int):
        """
        Devuelve los miembros de una familia con información detallada:
        nombre, parentesco, parcialidad, cédula, edad y estado (ACTIVO/FALLECIDO).
        """
        # Aliases
        miembro_fam = aliased(MiembroFamilia)
        miembro = aliased(Persona)

        # 🔹 Calculamos edad
        edad_expr = func.timestampdiff(
            text("YEAR"), miembro.fechaNacimiento, func.current_date())

        # 🔹 Calculamos estado
        estado_expr = case(
            (miembro.fechaDefuncion.isnot(None), "FALLECIDO"),
            else_="ACTIVO"
        ).label("estado")

        # 🔹 Query principal
        q = (
            self.db.query(
                miembro.id.label("id"),
                miembro.nombre.label("nombre"),
                miembro.apellido.label("apellido"),
                miembro.parentesco.label("parentesco"),
                Parcialidad.nombre.label("parcialidad"),
                miembro.id.label("cedula"),
                edad_expr.label("edad"),
                estado_expr
            )
            .join(miembro_fam, (miembro_fam.personaId == miembro.id) & (miembro_fam.familiaId == id_familia) & (miembro_fam.activo == 1))
            .outerjoin(Parcialidad, Parcialidad.id == miembro.idParcialidad)
        )

        # 🔍 Búsqueda flexible
        if query:
            q = q.filter(
                or_(
                    miembro.nombre.ilike(f"%{query}%"),
                    miembro.apellido.ilike(f"%{query}%"),
                    miembro.id.like(f"%{query}%")
                )
            )

        # 🔹 Paginación
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
                estado=row.estado
            )
            for row in result["items"]
        ]

        return result

    def get_familia_resumen(self, id_familia: int) -> FamiliaResumenOut:
        """
        Devuelve un resumen con los datos principales de una familia.
        Incluye líder, parcialidad, total de miembros, miembros activos y defunciones.
        """
        # Aliases
        representante = aliased(Persona)
        miembro = aliased(Persona)
        miembro_familia = aliased(MiembroFamilia)

        query = (
            self.db.query(
                Familia.id.label("id"),
                func.concat(representante.nombre, " ",
                            representante.apellido).label("lider_familia"),
                Parcialidad.nombre.label("parcialidad"),
                func.count(miembro.id).label("total_miembros"),
                func.sum(func.if_(miembro.fechaDefuncion.is_(
                    None), 1, 0)).label("miembros_activos"),
                func.sum(func.if_(miembro.fechaDefuncion.isnot(
                    None), 1, 0)).label("defunciones"),
                Familia.fechaCreacion.label("fechaCreacion")
            )
            # Unimos al representante a través de MiembroFamilia
            .join(MiembroFamilia, (MiembroFamilia.familiaId == Familia.id) & (MiembroFamilia.esRepresentante == True))
            .join(representante, representante.id == MiembroFamilia.personaId)
            # Contamos todos los miembros
            .outerjoin(miembro_familia, miembro_familia.familiaId == Familia.id)
            .outerjoin(miembro, miembro.id == miembro_familia.personaId)
            .outerjoin(Parcialidad, Parcialidad.id == representante.idParcialidad)
            .filter(Familia.id == id_familia)
            .group_by(Familia.id, representante.nombre, representante.apellido, Parcialidad.nombre)
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
            fechaCreacion=result.fechaCreacion
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
