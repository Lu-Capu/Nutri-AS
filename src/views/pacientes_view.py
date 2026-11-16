import flet as ft

from src.components.paciente_card import PacienteCard
from src.components.ui import (
    boton_primario,
    boton_secundario,
    campo,
    campo_etiquetado,
    chip,
    confirmar,
    dropdown,
    encabezado,
    estado_vacio,
    mostrar_snack,
    tarjeta,
    titulo_seccion,
)
from src.config import (
    COLOR_BORDER,
    COLOR_CARD_BG,
    FACTORES_ACTIVIDAD,
)
from src.database import Database
from src.models import Paciente
from src.nutricion import normalizar_factor_actividad


class PacientesView:
    def __init__(
        self,
        page: ft.Page,
        db: Database,
        on_abrir_paciente=None,
    ):
        self.page = page
        self.db = db
        self.on_abrir_paciente = on_abrir_paciente
        self.editando_id: int | None = None
        self._cache_pacientes: list[Paciente] | None = None

        self.campo_nombre = campo(
            "Nombre completo",
            prefix_icon=ft.Icons.PERSON,
        )
        self.campo_edad = campo(
            "40",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.campo_estatura = campo(
            "175.0",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.campo_peso = campo(
            "82.4",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.campo_peso_objetivo = campo(
            "70.0",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.campo_genero = dropdown(
            "Masculino / Femenino",
            [
                ("Masculino", "Masculino"),
                ("Femenino", "Femenino"),
                ("Otro", "Otro"),
            ],
        )
        self.campo_actividad = dropdown(
            "Nivel de actividad",
            [
                (f"{factor:.3f}", f"{nombre} · {factor}")
                for nombre, factor, _ in FACTORES_ACTIVIDAD
            ],
            value="1.200",
        )
        self.campo_busqueda = campo(
            "Buscar por nombre o género…",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._filtrar,
            width=320,
        )

        self.boton_guardar = boton_primario(
            "Registrar Paciente",
            self._guardar,
            icono=ft.Icons.PERSON_ADD,
            width=250,
        )
        self.boton_cancelar = boton_secundario(
            "Cancelar edición",
            self._cancelar_edicion,
            icono=ft.Icons.CLOSE,
        )
        self.boton_cancelar.visible = False

        self.lista = ft.ListView(expand=True, spacing=10, padding=0)
        self.contador = chip("0 pacientes", "info")

    # ── Vista ───────────────────────────────────────────────────

    def build(self) -> ft.Control:
        self._refrescar_lista()

        formulario = ft.Column(
            spacing=16,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        campo_etiquetado(
                            "Nombre completo",
                            self.campo_nombre,
                            expand=3,
                            icono=ft.Icons.PERSON,
                        ),
                        campo_etiquetado(
                            "Edad", self.campo_edad, expand=1
                        ),
                        campo_etiquetado(
                            "Género", self.campo_genero, expand=2
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        campo_etiquetado(
                            "Estatura (cm)",
                            self.campo_estatura,
                            expand=1,
                            icono=ft.Icons.HEIGHT,
                        ),
                        campo_etiquetado(
                            "Peso actual (kg)",
                            self.campo_peso,
                            expand=1,
                            icono=ft.Icons.MONITOR_WEIGHT,
                        ),
                        campo_etiquetado(
                            "Peso objetivo (kg)",
                            self.campo_peso_objetivo,
                            expand=1,
                            icono=ft.Icons.OUTLINED_FLAG,
                        ),
                        campo_etiquetado(
                            "Actividad física",
                            self.campo_actividad,
                            expand=2,
                            icono=ft.Icons.FITNESS_CENTER,
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    controls=[self.boton_guardar, self.boton_cancelar],
                ),
            ],
        )

        self.lista_card = ft.Container(
            expand=True,
            bgcolor=COLOR_CARD_BG,
            
            border_radius=12,
            padding=14,
            content=self.lista,
        )

        return ft.Column(
            expand=True,
            spacing=18,
            controls=[
                encabezado(
                    "Registro Clínico de Pacientes",
                    "Gestión de expedientes y datos antropométricos",
                    [self.contador],
                ),
                tarjeta(formulario),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        titulo_seccion(
                            "Pacientes registrados", ft.Icons.PEOPLE
                        ),
                        self.campo_busqueda,
                    ],
                ),
                self.lista_card,
            ],
        )

    # ── Lógica de negocio ───────────────────────────────────────

    def _guardar(self, e):
        try:
            if self.editando_id:
                paciente = self._leer_formulario()
                paciente.id = self.editando_id
                self.db.actualizar_paciente(paciente)
                mensaje = "Paciente actualizado correctamente."
            else:
                self.db.guardar_paciente(self._leer_formulario())
                mensaje = "Paciente registrado correctamente."
        except ValueError as error:
            mostrar_snack(self.page, str(error), "peligro")
            return

        self._cancelar_edicion(None)
        self._refrescar_lista(recargar_db=True)
        self.page.update()
        mostrar_snack(self.page, mensaje)

    def _leer_formulario(self) -> Paciente:
        nombre = (self.campo_nombre.value or "").strip()
        if not nombre:
            raise ValueError("El nombre completo es obligatorio.")
        if not self.campo_genero.value:
            raise ValueError("Seleccione el género del paciente.")

        try:
            edad = int((self.campo_edad.value or "").strip())
            estatura = float((self.campo_estatura.value or "").strip())
            peso = float((self.campo_peso.value or "").strip())
        except ValueError:
            raise ValueError(
                "Edad, estatura y peso deben ser valores numéricos."
            ) from None

        if edad <= 0 or estatura <= 0 or peso <= 0:
            raise ValueError(
                "Edad, estatura y peso deben ser mayores que cero."
            )

        peso_objetivo_texto = (self.campo_peso_objetivo.value or "").strip()
        peso_objetivo = None
        if peso_objetivo_texto:
            try:
                peso_objetivo = float(peso_objetivo_texto)
            except ValueError:
                raise ValueError(
                    "El peso objetivo debe ser un valor numérico."
                ) from None
            if peso_objetivo <= 0:
                raise ValueError(
                    "El peso objetivo debe ser mayor que cero."
                )

        factor = normalizar_factor_actividad(
            float(self.campo_actividad.value or "1.2")
        )

        return Paciente(
            nombre=nombre,
            edad=edad,
            genero=self.campo_genero.value,
            estatura=estatura,
            peso_actual=peso,
            peso_objetivo=peso_objetivo,
            actividad_fisica=factor,
        )

    def _cargar_en_formulario(self, paciente: Paciente):
        self.editando_id = paciente.id
        self.campo_nombre.value = paciente.nombre
        self.campo_edad.value = str(paciente.edad)
        self.campo_estatura.value = f"{paciente.estatura:g}"
        self.campo_peso.value = f"{paciente.peso_actual:g}"
        self.campo_peso_objetivo.value = (
            f"{paciente.peso_objetivo:g}" if paciente.peso_objetivo else ""
        )
        self.campo_genero.value = paciente.genero
        self.campo_actividad.value = (
            f"{normalizar_factor_actividad(paciente.actividad_fisica):.3f}"
        )
        self.boton_guardar.content = "Guardar cambios"
        self.boton_cancelar.visible = True
        self.page.update()

    def _cancelar_edicion(self, e):
        self.editando_id = None
        self.campo_nombre.value = ""
        self.campo_edad.value = ""
        self.campo_estatura.value = ""
        self.campo_peso.value = ""
        self.campo_peso_objetivo.value = ""
        self.campo_genero.value = None
        self.campo_actividad.value = "1.200"
        self.boton_guardar.content = "Registrar Paciente"
        self.boton_cancelar.visible = False
        self.page.update()

    def _confirmar_eliminar(self, paciente: Paciente):
        def eliminar():
            self.db.eliminar_paciente(paciente.id)
            self._refrescar_lista(recargar_db=True)
            self.page.update()
            mostrar_snack(self.page, "Paciente eliminado.")

        confirmar(
            self.page,
            "Eliminar paciente",
            f"¿Desea eliminar a {paciente.nombre}? También se borrarán "
            "sus mediciones y planes asociados.",
            eliminar,
        )

    def _abrir(self, paciente: Paciente):
        if self.on_abrir_paciente:
            self.on_abrir_paciente(paciente.id)

    def _filtrar(self, e):
        self._refrescar_lista(recargar_db=False)
        try:
            self.lista.update()
            self.contador.update()
        except RuntimeError:
            pass

    def _refrescar_lista(self, recargar_db: bool = True):
        if recargar_db or self._cache_pacientes is None:
            self._cache_pacientes = self.db.obtener_pacientes()

        busqueda = (self.campo_busqueda.value or "").strip().lower()
        if busqueda:
            pacientes = [
                p for p in self._cache_pacientes
                if busqueda in p.nombre.lower() or busqueda in (p.genero or "").lower()
            ]
        else:
            pacientes = self._cache_pacientes
        self.contador.content.value = (
            f"{len(pacientes)} paciente"
            if len(pacientes) == 1
            else f"{len(pacientes)} pacientes"
        )

        if pacientes:
            self.lista.controls = [
                PacienteCard(
                    paciente,
                    on_click=self._abrir,
                    on_editar=self._cargar_en_formulario,
                    on_eliminar=self._confirmar_eliminar,
                ).build()
                for paciente in pacientes
            ]
        else:
            self.lista.controls = [
                estado_vacio(
                    "No se encontraron pacientes.",
                    "Registre un paciente o ajuste la búsqueda.",
                    ft.Icons.PERSON_OFF,
                )
            ]

