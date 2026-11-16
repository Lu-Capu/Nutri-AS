from pathlib import Path

import flet as ft

from src.components.menu_lateral import MenuLateral
from src.config import COLOR_ACENTO, COLOR_FONDO_APP
from src.database import Database
from src.views.alimentos_view import AlimentosView
from src.views.dashboard_view import DashboardView
from src.views.dieta_view import DietPlannerView
from src.views.paciente_detalle_view import PacienteDetalleView
from src.views.pacientes_view import PacientesView
from src.views.placeholder_view import PlaceholderView


class App:
    def __init__(self, page: ft.Page, db: Database):
        self.page = page
        self.db = db
        self.indice_actual = 0

        self.contenido = ft.Container(
            expand=True,
            padding=ft.Padding.only(left=20, right=28, top=24, bottom=24),
        )
        self.menu = MenuLateral(on_change=self._cambiar_seccion, seleccionado=0)
        self.secciones = {
            0: self._vista_dashboard,
            1: self._vista_pacientes,
            2: self._vista_dieta,
            3: self._vista_alimentos,
            4: lambda: PlaceholderView("Configuración").build(),
        }

    def iniciar(self):
        self.page.title = "NutriClínico — Software de Nutrición"
        self.page.padding = 0
        self.page.bgcolor = COLOR_FONDO_APP
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(
            color_scheme_seed=COLOR_ACENTO,
            use_material3=True,
        )
        self.page.window.width = 1280
        self.page.window.height = 780
        self.page.window.min_width = 1000
        self.page.window.min_height = 640

        assets_dir = Path(__file__).resolve().parent.parent / "assets"
        for icon_name in ("icon.ico", "icon.png", "icon"):
            icon_path = assets_dir / icon_name
            if icon_path.exists():
                self.page.window.icon = str(icon_path)
                break

        menu_control = self.menu.build()
        self.contenido.content = self._vista_dashboard()

        self.page.add(
            ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    menu_control,
                    self.contenido,
                ],
            )
        )

    # ── Navegación ──────────────────────────────────────────────

    def _vista_dashboard(self) -> ft.Control:
        return DashboardView(
            self.page,
            self.db,
            on_abrir_paciente=self.abrir_paciente,
            on_navegar=self._ir_a_seccion,
        ).build()

    def _vista_pacientes(self) -> ft.Control:
        return PacientesView(
            self.page,
            self.db,
            on_abrir_paciente=self.abrir_paciente,
        ).build()

    def _vista_dieta(self) -> ft.Control:
        return DietPlannerView(
            self.page,
            self.db,
            on_ir_pacientes=lambda: self._ir_a_seccion(1),
        ).build()

    def _vista_alimentos(self) -> ft.Control:
        return AlimentosView(self.page, self.db).build()

    def _cambiar_seccion(self, e):
        indice = (
            e
            if isinstance(e, int)
            else getattr(getattr(e, "control", None), "selected_index", 0)
        )
        self._ir_a_seccion(indice)

    def _ir_a_seccion(self, indice: int):
        if indice not in self.secciones:
            return
        self.indice_actual = indice
        self.menu.seleccionar(indice)
        self._mostrar(indice)

    def _mostrar(self, indice: int):
        constructor = self.secciones.get(indice)
        if not constructor:
            return
        try:
            self.contenido.content = constructor()
        except Exception as ex:
            self.contenido.content = ft.Container(
                padding=20,
                content=ft.Text(f"Error al cargar la vista: {ex}", color="red"),
            )
        try:
            self.contenido.update()
        except RuntimeError:
            pass

    def abrir_paciente(self, paciente_id: int):
        self.indice_actual = 1
        self.menu.seleccionar(1)
        self.contenido.content = PacienteDetalleView(
            self.page,
            self.db,
            paciente_id,
            on_volver=lambda: self._ir_a_seccion(1),
            on_crear_plan=self._crear_plan_para_paciente,
        ).build()
        try:
            self.contenido.update()
        except RuntimeError:
            pass

    def _crear_plan_para_paciente(self, paciente_id: int):
        self.indice_actual = 2
        self.menu.seleccionar(2)
        self.contenido.content = DietPlannerView(
            self.page,
            self.db,
            paciente_id=paciente_id,
            on_volver=lambda: self.abrir_paciente(paciente_id),
            on_ir_pacientes=lambda: self._ir_a_seccion(1),
        ).build()
        try:
            self.contenido.update()
        except RuntimeError:
            pass
