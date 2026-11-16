import flet as ft

from src.components.ui import (
    TONOS,
    barra_progreso,
    boton_primario,
    boton_secundario,
    boton_texto,
    campo,
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
    COLOR_ACENTO,
    COLOR_AZUL_ACERO,
    COLOR_INPUT_BG,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    DISTRIBUCION_MACROS_DEFAULT,
    TIEMPOS_COMIDA,
)
from src.database import Database
from src.models import Paciente
from src.nutricion import (
    aporte_alimento,
    calcular_resultado,
    distribuir_macronutrientes,
)

ICONOS_COMIDA = {
    "Desayuno": ft.Icons.BREAKFAST_DINING,
    "Media Mañana": ft.Icons.COFFEE,
    "Almuerzo": ft.Icons.LUNCH_DINING,
    "Merienda": ft.Icons.COOKIE,
    "Cena": ft.Icons.DINNER_DINING,
}


class DietPlannerView:
    """Generador de planes de alimentación por tiempos de comida."""

    def __init__(
        self,
        page: ft.Page,
        db: Database,
        on_volver=None,
        on_ir_pacientes=None,
        paciente_id: int | None = None,
        plan_id: int | None = None,
    ):
        self.page = page
        self.db = db
        self.on_volver = on_volver
        self.on_ir_pacientes = on_ir_pacientes

        self.pacientes = db.obtener_pacientes()
        if paciente_id is None and self.pacientes:
            paciente_id = self.pacientes[0].id

        self.paciente_id = paciente_id
        self.paciente: Paciente | None = (
            db.obtener_paciente_por_id(paciente_id)
            if paciente_id
            else None
        )
        self.plan_id: int | None = None
        self.nombre_plan = ""
        self.geb: float | None = None
        self.get_target: float | None = None
        self.metas: dict | None = None
        self.items: dict[str, list[dict]] = {
            tiempo: [] for tiempo in TIEMPOS_COMIDA
        }

        self.alimentos = db.obtener_alimentos()
        self.alimentos_por_id = {
            alimento.id: alimento for alimento in self.alimentos
        }
        self._opciones_alimentos = [
            (
                str(alimento.id),
                f"{alimento.nombre} · {alimento.calorias:.0f} kcal/{alimento.porcion_base:g} g",
            )
            for alimento in self.alimentos
        ]

        if plan_id:
            self._cargar_plan(plan_id)
        elif self.paciente:
            self._nuevo_plan()

        self.root = ft.Column(expand=True, spacing=18)

    # ── Vista ───────────────────────────────────────────────────

    def build(self) -> ft.Control:
        self._renderizar(actualizar=False)
        return self.root

    def _renderizar(self, actualizar: bool = True):
        self.root.controls = self._construir()
        if actualizar:
            try:
                self.root.update()
            except RuntimeError:
                pass

    def _construir(self) -> list[ft.Control]:
        encabezado_vista = encabezado(
            "Planificador de Dietas",
            "Asigne porciones por tiempo de comida y verifique el GET",
            [
                boton_texto(
                    "Volver",
                    self._volver,
                    icono=ft.Icons.ARROW_BACK,
                )
            ]
            if self.on_volver
            else [],
        )

        if not self.paciente:
            controles_vacio = [
                estado_vacio(
                    "No hay pacientes disponibles.",
                    "Registre un paciente para comenzar a crear planes "
                    "de alimentación.",
                    ft.Icons.PERSON_ADD,
                )
            ]
            if self.on_ir_pacientes:
                controles_vacio.append(
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            boton_primario(
                                "Ir a pacientes",
                                lambda e: self.on_ir_pacientes(),
                                icono=ft.Icons.PERSON_ADD,
                            )
                        ],
                    )
                )
            return [
                encabezado_vista,
                tarjeta(
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                        controls=controles_vacio,
                    )
                ),
            ]

        if self.metas is None:
            return [
                encabezado_vista,
                tarjeta(
                    estado_vacio(
                        "No fue posible calcular los objetivos.",
                        "Revise los datos antropométricos del paciente.",
                        ft.Icons.INFO_OUTLINE,
                    )
                ),
            ]

        return [
            encabezado_vista,
            self._barra_herramientas(),
            ft.Row(
                expand=True,
                spacing=18,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.ListView(
                        expand=True,
                        spacing=12,
                        padding=0,
                        controls=[
                            self._tarjeta_comida(tiempo)
                            for tiempo in TIEMPOS_COMIDA
                        ],
                    ),
                    ft.Column(
                        width=320,
                        spacing=12,
                        controls=[self._tarjeta_totales()],
                    ),
                ],
            ),
        ]

    def _barra_herramientas(self) -> ft.Control:
        opciones_pacientes = [
            (str(p.id), p.nombre) for p in self.pacientes
        ]
        selector_paciente = dropdown(
            "Paciente",
            opciones_pacientes,
            value=str(self.paciente_id) if self.paciente_id else None,
            on_select=self._seleccionar_paciente,
            expand=True,
        )

        planes = self.db.obtener_planes_paciente(self.paciente_id)
        opciones_planes = [
            (str(plan.id), f"#{plan.id} · {plan.nombre}") for plan in planes
        ]
        selector_plan = dropdown(
            "Cargar plan guardado",
            opciones_planes,
            value=str(self.plan_id) if self.plan_id else None,
            on_select=self._seleccionar_plan,
            expand=True,
        )

        campo_nombre = campo(
            "Nombre del plan",
            value=self.nombre_plan,
            on_change=self._cambiar_nombre,
            prefix_icon=ft.Icons.EDIT,
        )
        campo_nombre.expand = True

        fila_superior = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[selector_paciente, selector_plan],
                ),
                chip(
                    f"GET: {self.get_target:.0f} kcal",
                    "normal",
                ),
            ],
        )

        fila_inferior = ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(content=campo_nombre, expand=True),
                boton_secundario(
                    "Nuevo",
                    self._boton_nuevo_plan,
                    icono=ft.Icons.ADD,
                    width=105,
                ),
                boton_primario(
                    "Guardar plan",
                    self._guardar_plan,
                    icono=ft.Icons.SAVE,
                    width=175,
                ),
            ],
        )

        return tarjeta(
            ft.Column(
                spacing=12,
                controls=[fila_superior, fila_inferior],
            ),
            padding=16,
        )

    def _tarjeta_comida(self, tiempo: str) -> ft.Control:
        items = self.items.get(tiempo, [])
        subtotal = self._subtotal(items)
        icono = ICONOS_COMIDA.get(tiempo, ft.Icons.RESTAURANT)

        filas = [
            self._fila_item(tiempo, indice, item)
            for indice, item in enumerate(items)
        ]
        if not filas:
            filas = [
                ft.Text(
                    "Sin alimentos asignados.",
                    size=11,
                    color=COLOR_TEXT_MUTED,
                    italic=True,
                )
            ]

        agregar_dropdown = dropdown(
            "Seleccionar alimento",
            self._opciones_alimentos,
        )
        campo_gramos = campo(
            "g",
            value="100",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=76,
            text_align=ft.TextAlign.CENTER,
        )

        def agregar(e):
            self._agregar_alimento(
                tiempo, agregar_dropdown, campo_gramos
            )

        boton_agregar = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE,
            icon_color=COLOR_ACENTO,
            tooltip="Agregar alimento",
            on_click=agregar,
        )

        return tarjeta(
            ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(
                                        icono,
                                        size=18,
                                        color=COLOR_ACENTO,
                                    ),
                                    ft.Text(
                                        tiempo,
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color=COLOR_TEXT_PRIMARY,
                                    ),
                                ],
                            ),
                            chip(
                                f"{subtotal['calorias']:.0f} kcal",
                                "info",
                            ),
                        ],
                    ),
                    ft.Column(spacing=6, controls=filas),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Container(
                                content=agregar_dropdown, expand=True
                            ),
                            campo_gramos,
                            boton_agregar,
                        ],
                    ),
                ],
            ),
            padding=16,
        )

    def _fila_item(self, tiempo: str, indice: int, item: dict) -> ft.Control:
        alimento = self.alimentos_por_id.get(item["alimento_id"])
        if not alimento:
            return ft.Container()
        aporte = aporte_alimento(alimento, item["gramos"])

        def eliminar(e):
            self.items[tiempo].pop(indice)
            self._renderizar()

        return ft.Container(
            bgcolor=COLOR_INPUT_BG,
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=10, vertical=7),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=1,
                        expand=True,
                        controls=[
                            ft.Text(
                                alimento.nombre,
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color=COLOR_TEXT_PRIMARY,
                            ),
                            ft.Text(
                                f"{aporte['proteinas']:.1f} P · "
                                f"{aporte['carbohidratos']:.1f} C · "
                                f"{aporte['grasas']:.1f} G",
                                size=10,
                                color=COLOR_TEXT_SECONDARY,
                            ),
                        ],
                    ),
                    ft.Text(
                        f"{item['gramos']:g} g",
                        size=11,
                        color=COLOR_TEXT_SECONDARY,
                        width=54,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                    ft.Text(
                        f"{aporte['calorias']:.0f} kcal",
                        size=11,
                        weight=ft.FontWeight.W_600,
                        color=COLOR_TEXT_PRIMARY,
                        width=64,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_size=16,
                        icon_color=TONOS["peligro"][0],
                        tooltip="Quitar alimento",
                        on_click=eliminar,
                    ),
                ],
            ),
        )

    def _tarjeta_totales(self) -> ft.Control:
        total = self._totales()
        objetivo = self.get_target or 0
        diferencia = total["calorias"] - objetivo
        proporcion = total["calorias"] / objetivo if objetivo else 0

        if abs(diferencia) <= objetivo * 0.05:
            chip_estado = chip("Plan equilibrado con el GET", "normal")
            color_kcal = TONOS["normal"][0]
        elif diferencia < 0:
            chip_estado = chip(
                f"Faltan {abs(diferencia):.0f} kcal", "advertencia"
            )
            color_kcal = TONOS["advertencia"][0]
        else:
            chip_estado = chip(
                f"Excede {diferencia:.0f} kcal", "peligro"
            )
            color_kcal = TONOS["peligro"][0]

        def fila_macro(
            nombre: str, actual: float, meta: float, color: str
        ) -> ft.Control:
            proporcion_macro = actual / meta if meta else 0
            return ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                nombre,
                                size=11,
                                color=COLOR_TEXT_SECONDARY,
                            ),
                            ft.Text(
                                f"{actual:.0f} / {meta:.0f} g",
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=COLOR_TEXT_PRIMARY,
                            ),
                        ],
                    ),
                    barra_progreso(proporcion_macro, color),
                ],
            )

        return tarjeta(
            ft.Column(
                spacing=14,
                controls=[
                    titulo_seccion(
                        "Resumen del día", ft.Icons.ASSESSMENT
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.END,
                                controls=[
                                    ft.Text(
                                        f"{total['calorias']:.0f}",
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        f"/ {objetivo:.0f} kcal",
                                        size=12,
                                        color=COLOR_TEXT_SECONDARY,
                                    ),
                                ],
                            ),
                            barra_progreso(proporcion, color_kcal),
                        ],
                    ),
                    chip_estado,
                    ft.Column(
                        spacing=10,
                        controls=[
                            fila_macro(
                                "Proteínas",
                                total["proteinas"],
                                self.metas["proteinas"],
                                COLOR_ACENTO,
                            ),
                            fila_macro(
                                "Carbohidratos",
                                total["carbohidratos"],
                                self.metas["carbohidratos"],
                                COLOR_AZUL_ACERO,
                            ),
                            fila_macro(
                                "Grasas",
                                total["grasas"],
                                self.metas["grasas"],
                                "#B89A5A",
                            ),
                        ],
                    ),
                    ft.Container(
                        bgcolor=COLOR_INPUT_BG,
                        border_radius=10,
                        padding=10,
                        content=ft.Column(
                            spacing=3,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            "GEB",
                                            size=11,
                                            color=COLOR_TEXT_SECONDARY,
                                        ),
                                        ft.Text(
                                            f"{self.geb:.0f} kcal",
                                            size=11,
                                            weight=ft.FontWeight.W_600,
                                            color=COLOR_TEXT_PRIMARY,
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(
                                            "GET (objetivo)",
                                            size=11,
                                            color=COLOR_TEXT_SECONDARY,
                                        ),
                                        ft.Text(
                                            f"{objetivo:.0f} kcal",
                                            size=11,
                                            weight=ft.FontWeight.W_600,
                                            color=COLOR_TEXT_PRIMARY,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    boton_primario(
                        "Guardar plan",
                        self._guardar_plan,
                        icono=ft.Icons.SAVE,
                    ),
                    boton_secundario(
                        "Vaciar plan",
                        self._vaciar_plan,
                        icono=ft.Icons.DELETE_OUTLINE,
                    ),
                ],
            ),
            padding=16,
        )

    # ── Cálculos ────────────────────────────────────────────────

    def _subtotal(self, items: list[dict]) -> dict[str, float]:
        total = {
            "calorias": 0.0,
            "proteinas": 0.0,
            "carbohidratos": 0.0,
            "grasas": 0.0,
        }
        for item in items:
            alimento = self.alimentos_por_id.get(item["alimento_id"])
            if not alimento:
                continue
            aporte = aporte_alimento(alimento, item["gramos"])
            for clave in total:
                total[clave] += aporte[clave]
        return total

    def _totales(self) -> dict[str, float]:
        totales = {
            "calorias": 0.0,
            "proteinas": 0.0,
            "carbohidratos": 0.0,
            "grasas": 0.0,
        }
        for items in self.items.values():
            subtotal = self._subtotal(items)
            for clave in totales:
                totales[clave] += subtotal[clave]
        return totales

    def _nuevo_plan(self):
        self.plan_id = None
        self.nombre_plan = ""
        self.items = {tiempo: [] for tiempo in TIEMPOS_COMIDA}
        self._calcular_objetivos()

    def _calcular_objetivos(self):
        if not self.paciente:
            self.geb = None
            self.get_target = None
            self.metas = None
            return
        try:
            resultado = calcular_resultado(
                peso_kg=self.paciente.peso_actual,
                estatura_cm=self.paciente.estatura,
                edad=self.paciente.edad,
                genero=self.paciente.genero,
                factor_actividad=self.paciente.actividad_fisica,
                peso_objetivo=self.paciente.peso_objetivo,
            )
            distribucion = distribuir_macronutrientes(
                resultado.get, *DISTRIBUCION_MACROS_DEFAULT
            )
        except ValueError:
            self.geb = None
            self.get_target = None
            self.metas = None
            return

        self.geb = resultado.geb
        self.get_target = resultado.get
        self.metas = {
            "proteinas": distribucion.gramos_proteinas,
            "carbohidratos": distribucion.gramos_carbohidratos,
            "grasas": distribucion.gramos_grasas,
        }

    def _cargar_plan(self, plan_id: int) -> bool:
        plan = self.db.obtener_plan_por_id(plan_id)
        if not plan:
            mostrar_snack(
                self.page, "El plan solicitado no existe.", "peligro"
            )
            return False

        self.plan_id = plan.id
        self.paciente_id = plan.paciente_id
        self.paciente = self.db.obtener_paciente_por_id(plan.paciente_id)
        self.nombre_plan = plan.nombre or ""
        self.geb = plan.geb
        self.get_target = plan.get_total
        self.metas = {
            "proteinas": plan.proteinas_meta,
            "carbohidratos": plan.carbs_meta,
            "grasas": plan.grasas_meta,
        }

        items = {tiempo: [] for tiempo in TIEMPOS_COMIDA}
        for item in plan.items:
            tiempo = (
                item.tiempo_comida
                if item.tiempo_comida in items
                else "Almuerzo"
            )
            items[tiempo].append(
                {
                    "alimento_id": item.alimento_id,
                    "gramos": item.gramos,
                }
            )
        self.items = items
        return True

    # ── Eventos ─────────────────────────────────────────────────

    def _seleccionar_paciente(self, e):
        valor = e.control.value
        if not valor:
            return
        self.paciente_id = int(valor)
        self.paciente = self.db.obtener_paciente_por_id(self.paciente_id)
        self._nuevo_plan()
        self._renderizar()

    def _seleccionar_plan(self, e):
        if not e.control.value:
            return
        if self._cargar_plan(int(e.control.value)):
            self._renderizar()

    def _boton_nuevo_plan(self, e):
        self._nuevo_plan()
        self._renderizar()

    def _cambiar_nombre(self, e):
        self.nombre_plan = e.control.value or ""

    def _agregar_alimento(self, tiempo: str, selector, campo_gramos):
        if not selector.value:
            mostrar_snack(
                self.page,
                "Seleccione un alimento antes de agregarlo.",
                "advertencia",
            )
            return
        try:
            gramos = float((campo_gramos.value or "").strip())
        except ValueError:
            mostrar_snack(
                self.page,
                "Ingrese una cantidad válida en gramos.",
                "advertencia",
            )
            return
        if gramos <= 0:
            mostrar_snack(
                self.page,
                "La cantidad debe ser mayor que cero.",
                "advertencia",
            )
            return

        self.items[tiempo].append(
            {
                "alimento_id": int(selector.value),
                "gramos": gramos,
            }
        )
        self._renderizar()

    def _guardar_plan(self, e):
        if not self.paciente_id or not self.metas:
            mostrar_snack(
                self.page,
                "No se pudieron calcular los objetivos del plan.",
                "peligro",
            )
            return

        items = [
            {
                "tiempo_comida": tiempo,
                "alimento_id": item["alimento_id"],
                "gramos": item["gramos"],
            }
            for tiempo in TIEMPOS_COMIDA
            for item in self.items.get(tiempo, [])
        ]
        if not items:
            mostrar_snack(
                self.page,
                "Agregue al menos un alimento al plan.",
                "advertencia",
            )
            return

        nombre = (
            self.nombre_plan.strip()
            or f"Plan de {self.paciente.nombre}"
        )
        try:
            plan = self.db.guardar_plan_completo(
                plan_id=self.plan_id,
                paciente_id=self.paciente_id,
                nombre=nombre,
                geb=self.geb,
                get_total=self.get_target,
                proteinas_meta=self.metas["proteinas"],
                carbs_meta=self.metas["carbohidratos"],
                grasas_meta=self.metas["grasas"],
                items=items,
            )
        except Exception as error:  # noqa: BLE001
            mostrar_snack(
                self.page,
                f"No se pudo guardar el plan: {error}",
                "peligro",
            )
            return

        self.plan_id = plan.id
        self.nombre_plan = plan.nombre
        mostrar_snack(
            self.page,
            f"Plan «{plan.nombre}» guardado correctamente.",
        )
        self._renderizar()

    def _vaciar_plan(self, e):
        def vaciar():
            self.items = {tiempo: [] for tiempo in TIEMPOS_COMIDA}
            self._renderizar()
            mostrar_snack(self.page, "Se vació el plan actual.", "info")

        confirmar(
            self.page,
            "Vaciar plan",
            "Se quitarán todos los alimentos asignados. "
            "Los cambios no se guardarán hasta pulsar «Guardar plan».",
            vaciar,
            texto_confirmar="Vaciar",
        )

    def _volver(self, e):
        if self.on_volver:
            self.on_volver()

