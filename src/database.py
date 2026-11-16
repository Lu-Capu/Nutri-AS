"""Capa de acceso a datos basada en SQLAlchemy + SQLite."""

from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event, func, inspect, or_, select, text
from sqlalchemy.orm import selectinload, sessionmaker

from src.config import DB_PATH
from src.data.alimentos_semilla import ALIMENTOS_SEMILLA
from src.models import (
    Alimento,
    Base,
    Medicion,
    Paciente,
    Plan,
    PlanAlimento,
)


class Database:
    """Fachada de persistencia utilizada por las vistas de la aplicación."""

    def __init__(self, ruta_db: str | Path | None = None):
        ruta = Path(ruta_db) if ruta_db else DB_PATH
        if not ruta.is_absolute():
            ruta = DB_PATH.parent / ruta
        self.ruta_db = ruta
        self.engine = create_engine(f"sqlite:///{ruta.as_posix()}")

        @event.listens_for(self.engine, "connect")
        def _activar_claves_foraneas(conexion, _registro):
            cursor = conexion.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=DELETE")
            cursor.close()

        self.SessionLocal = sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    # ── Infraestructura ─────────────────────────────────────────

    @contextmanager
    def sesion(self):
        sesion = self.SessionLocal()
        try:
            yield sesion
            sesion.commit()
        except Exception:
            sesion.rollback()
            raise
        finally:
            sesion.close()

    def inicializar_bd(self):
        """Crea las tablas, migra columnas antiguas, crea índices y siembra el catálogo."""
        Base.metadata.create_all(self.engine)
        self._migrar_columnas()
        self._crear_indices()
        self._sembrar_catalogo()

    def _crear_indices(self):
        """Crea índices clave para búsquedas instantáneas y uniones rápidas."""
        indices = [
            'CREATE INDEX IF NOT EXISTS "ix_paciente_nombre" ON "PACIENTE" ("nombre")',
            'CREATE INDEX IF NOT EXISTS "ix_alimento_categoria" ON "ALIMENTO" ("categoria")',
            'CREATE INDEX IF NOT EXISTS "ix_medicion_paciente_id" ON "MEDICION" ("paciente_id")',
            'CREATE INDEX IF NOT EXISTS "ix_plan_paciente_id" ON "PLANES_NUTRICIONALES" ("paciente_id")',
            'CREATE INDEX IF NOT EXISTS "ix_plan_alimento_plan_id" ON "PLAN_ALIMENTO" ("plan_id")',
            'CREATE INDEX IF NOT EXISTS "ix_plan_alimento_alimento_id" ON "PLAN_ALIMENTO" ("alimento_id")',
        ]
        with self.engine.begin() as conexion:
            for sql in indices:
                try:
                    conexion.execute(text(sql))
                except Exception:
                    pass

    def _migrar_columnas(self):
        """Agrega columnas nuevas a bases de datos creadas con versiones previas."""
        columnas_nuevas = {
            "PACIENTE": {
                "peso_objetivo": "REAL",
            },
            "ALIMENTO": {
                "categoria": "TEXT DEFAULT 'General'",
            },
            "PLANES_NUTRICIONALES": {
                "nombre": "TEXT DEFAULT 'Plan de alimentación'",
                "activo": "INTEGER DEFAULT 1",
            },
        }

        inspector = inspect(self.engine)
        tablas = set(inspector.get_table_names())

        with self.engine.begin() as conexion:
            for tabla, columnas in columnas_nuevas.items():
                if tabla not in tablas:
                    continue
                existentes = {
                    columna["name"] for columna in inspector.get_columns(tabla)
                }
                for nombre, definicion in columnas.items():
                    if nombre not in existentes:
                        conexion.execute(
                            text(
                                f'ALTER TABLE "{tabla}" '
                                f'ADD COLUMN "{nombre}" {definicion}'
                            )
                        )

    def _sembrar_catalogo(self):
        with self.sesion() as sesion:
            total = sesion.scalar(select(func.count(Alimento.id))) or 0
            if total > 0:
                return
            sesion.add_all(Alimento(**datos) for datos in ALIMENTOS_SEMILLA)

    # ── Pacientes ───────────────────────────────────────────────

    def guardar_paciente(self, paciente: Paciente) -> Paciente:
        with self.sesion() as sesion:
            sesion.add(paciente)
            sesion.flush()
            return paciente

    def actualizar_paciente(self, paciente: Paciente) -> Paciente:
        """Actualiza solo los datos clínicos sin tocar mediciones ni planes."""
        with self.sesion() as sesion:
            actual = sesion.get(Paciente, paciente.id)
            if not actual:
                raise ValueError("El paciente solicitado no existe.")
            actual.nombre = paciente.nombre
            actual.edad = paciente.edad
            actual.genero = paciente.genero
            actual.estatura = paciente.estatura
            actual.peso_actual = paciente.peso_actual
            actual.peso_objetivo = paciente.peso_objetivo
            actual.actividad_fisica = paciente.actividad_fisica
            sesion.flush()
            return actual

    def obtener_pacientes(self, busqueda: str | None = None) -> list[Paciente]:
        consulta = select(Paciente)
        if busqueda:
            patron = f"%{busqueda.strip()}%"
            consulta = consulta.where(
                or_(
                    Paciente.nombre.ilike(patron),
                    Paciente.genero.ilike(patron),
                )
            )
        consulta = consulta.order_by(Paciente.id.desc())
        with self.sesion() as sesion:
            return list(sesion.scalars(consulta))

    def obtener_paciente_por_id(self, paciente_id: int) -> Paciente | None:
        with self.sesion() as sesion:
            return sesion.get(Paciente, paciente_id)

    def eliminar_paciente(self, paciente_id: int) -> bool:
        with self.sesion() as sesion:
            paciente = sesion.get(Paciente, paciente_id)
            if not paciente:
                return False
            sesion.delete(paciente)
            return True

    def contar_pacientes(self) -> int:
        with self.sesion() as sesion:
            return sesion.scalar(select(func.count(Paciente.id))) or 0

    # ── Mediciones (evolución antropométrica) ───────────────────

    def registrar_medicion(
        self,
        paciente_id: int,
        peso: float,
        estatura: float | None = None,
    ) -> Medicion:
        with self.sesion() as sesion:
            medicion = Medicion(
                paciente_id=paciente_id,
                peso=peso,
                estatura=estatura,
            )
            sesion.add(medicion)
            sesion.flush()
            return medicion

    def obtener_mediciones(self, paciente_id: int) -> list[Medicion]:
        consulta = (
            select(Medicion)
            .where(Medicion.paciente_id == paciente_id)
            .order_by(Medicion.fecha.asc(), Medicion.id.asc())
        )
        with self.sesion() as sesion:
            return list(sesion.scalars(consulta))

    def eliminar_medicion(self, medicion_id: int) -> bool:
        with self.sesion() as sesion:
            medicion = sesion.get(Medicion, medicion_id)
            if not medicion:
                return False
            sesion.delete(medicion)
            return True

    # ── Catálogo de alimentos ───────────────────────────────────

    def guardar_alimento(self, alimento: Alimento) -> Alimento:
        with self.sesion() as sesion:
            sesion.add(alimento)
            sesion.flush()
            return alimento

    def actualizar_alimento(self, alimento: Alimento) -> Alimento:
        with self.sesion() as sesion:
            return sesion.merge(alimento)

    def obtener_alimentos(
        self,
        busqueda: str | None = None,
        categoria: str | None = None,
    ) -> list[Alimento]:
        consulta = select(Alimento)
        if busqueda:
            patron = f"%{busqueda.strip()}%"
            consulta = consulta.where(
                or_(
                    Alimento.nombre.ilike(patron),
                    Alimento.categoria.ilike(patron),
                )
            )
        if categoria:
            consulta = consulta.where(Alimento.categoria == categoria)
        consulta = consulta.order_by(Alimento.categoria, Alimento.nombre)
        with self.sesion() as sesion:
            return list(sesion.scalars(consulta))

    def obtener_alimento_por_id(self, alimento_id: int) -> Alimento | None:
        with self.sesion() as sesion:
            return sesion.get(Alimento, alimento_id)

    def eliminar_alimento(self, alimento_id: int) -> bool:
        with self.sesion() as sesion:
            alimento = sesion.get(Alimento, alimento_id)
            if not alimento:
                return False
            sesion.delete(alimento)
            return True

    def contar_alimentos(self) -> int:
        with self.sesion() as sesion:
            return sesion.scalar(select(func.count(Alimento.id))) or 0

    def obtener_categorias_alimentos(self) -> list[str]:
        consulta = (
            select(Alimento.categoria)
            .distinct()
            .order_by(Alimento.categoria)
        )
        with self.sesion() as sesion:
            return [categoria for categoria in sesion.scalars(consulta) if categoria]

    # ── Planes de alimentación ──────────────────────────────────

    def guardar_plan_completo(
        self,
        *,
        paciente_id: int,
        nombre: str,
        geb: float,
        get_total: float,
        proteinas_meta: float,
        carbs_meta: float,
        grasas_meta: float,
        items: list[dict],
        plan_id: int | None = None,
    ) -> Plan:
        """Crea o reemplaza un plan con todos sus alimentos asignados."""
        with self.sesion() as sesion:
            if plan_id:
                plan = sesion.get(Plan, plan_id)
                if not plan:
                    raise ValueError("El plan solicitado no existe.")
                plan.items.clear()
            else:
                plan = Plan()

            plan.paciente_id = paciente_id
            plan.nombre = nombre
            plan.geb = geb
            plan.get_total = get_total
            plan.proteinas_meta = proteinas_meta
            plan.carbs_meta = carbs_meta
            plan.grasas_meta = grasas_meta
            plan.activo = True

            for item in items:
                plan.items.append(
                    PlanAlimento(
                        tiempo_comida=item["tiempo_comida"],
                        alimento_id=item["alimento_id"],
                        gramos=item["gramos"],
                    )
                )

            sesion.add(plan)
            sesion.flush()
            return plan

    def obtener_planes_paciente(self, paciente_id: int) -> list[Plan]:
        consulta = (
            select(Plan)
            .where(Plan.paciente_id == paciente_id)
            .options(
                selectinload(Plan.items).selectinload(PlanAlimento.alimento)
            )
            .order_by(Plan.id.desc())
        )
        with self.sesion() as sesion:
            return list(sesion.scalars(consulta))

    def obtener_plan_por_id(self, plan_id: int) -> Plan | None:
        consulta = (
            select(Plan)
            .where(Plan.id == plan_id)
            .options(
                selectinload(Plan.items).selectinload(PlanAlimento.alimento),
                selectinload(Plan.paciente),
            )
        )
        with self.sesion() as sesion:
            return sesion.scalar(consulta)

    def obtener_planes_recientes(self, limite: int = 5) -> list[Plan]:
        consulta = (
            select(Plan)
            .options(selectinload(Plan.paciente))
            .order_by(Plan.id.desc())
            .limit(limite)
        )
        with self.sesion() as sesion:
            return list(sesion.scalars(consulta))

    def eliminar_plan(self, plan_id: int) -> bool:
        with self.sesion() as sesion:
            plan = sesion.get(Plan, plan_id)
            if not plan:
                return False
            sesion.delete(plan)
            return True

    def contar_planes(self) -> int:
        with self.sesion() as sesion:
            return sesion.scalar(select(func.count(Plan.id))) or 0

    def obtener_metricas_dashboard(self) -> dict:
        """Obtiene métricas agregadas del panel de control de forma optimizada."""
        with self.sesion() as sesion:
            total_pacientes = sesion.scalar(select(func.count(Paciente.id))) or 0
            total_planes = sesion.scalar(select(func.count(Plan.id))) or 0
            total_alimentos = sesion.scalar(select(func.count(Alimento.id))) or 0

            promedio_imc = sesion.scalar(
                select(
                    func.avg(
                        Paciente.peso_actual
                        * 10000.0
                        / (Paciente.estatura * Paciente.estatura)
                    )
                ).where(Paciente.estatura > 0, Paciente.peso_actual > 0)
            )

            recientes = list(
                sesion.scalars(
                    select(Paciente).order_by(Paciente.id.desc()).limit(5)
                )
            )

            return {
                "total_pacientes": total_pacientes,
                "total_planes": total_planes,
                "total_alimentos": total_alimentos,
                "promedio_imc": round(promedio_imc, 1) if promedio_imc else None,
                "pacientes_recientes": recientes,
            }


if __name__ == "__main__":
    Database().inicializar_bd()
