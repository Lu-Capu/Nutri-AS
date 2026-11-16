import flet as ft

from src.components.ui import (
    TONOS,
    boton_primario,
    campo,
    campo_etiquetado,
    chip,
    dropdown,
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
    FACTORES_ACTIVIDAD,
)
from src.database import Database
from src.models import Paciente
from src.nutricion import (
    calcular_resultado,
    distribuir_macronutrientes,
    etiqueta_actividad,
    normalizar_factor_actividad,
)


class PacienteDetalleView:
    """Ficha clínica del paciente con cálculos energéticos en vivo."""

    def __init__(
        self,
        page: ft.Page,
        db: Database,
        paciente_id: int,
        on_volver=None,
        on_crear_plan=None,
    ):
        self.page = page
        self.db = db
        self.on_volver = on_volver
        self.on_crear_plan = on_crear_plan
        self.paciente: Paciente | None = db.obtener_paciente_por_id(
            paciente_id
        )
        self.resultado = None
        self.distribucion = None

        if not self.paciente:
            return

        p = self.paciente
        self.campo_nombre = campo(
            "Nombre completo",
            value=p.nombre,
            prefix_icon=ft.Icons.PERSON,
            on_change=self._recalcular,
        )
        self.campo_edad = campo(
            "Edad",
            value=str(p.edad),
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._recalcular,
        )
        self.campo_estatura = campo(
            "Estatura (cm)",
            value=f"{p.estatura:g}",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._recalcular,
        )
        self.campo_peso = campo(
            "Peso (kg)",
            value=f"{p.peso_actual:g}",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._recalcular,
        )
        self.campo_peso_objetivo = campo(
            "Peso objetivo (kg)",
            value=f"{p.peso_objetivo:g}" if p.peso_objetivo else "",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._recalcular,
        )
        self.campo_genero = dropdown(
            "Género",
            [
                ("Masculino", "Masculino"),
                ("Femenino", "Femenino"),
                ("Otro", "Otro"),
            ],
            value=p.genero,
            on_select=self._recalcular,
        )
        factor_actual = normalizar_factor_actividad(p.actividad_fisica)
        self.campo_actividad = dropdown(
            "Nivel de actividad",
            [
                (f"{factor:.3f}", f"{nombre} · {factor}")
                for nombre, factor, _ in FACTORES_ACTIVIDAD
            ],
            value=f"{factor_actual:.3f}",
            on_select=self._recalcular,
        )

        self.campo_proteinas = self._campo_porcentaje("20")
        self.campo_carbohidratos = self._campo_porcentaje("50")
        self.campo_grasas = self._campo_porcentaje("30")

        self.panel_resultados = ft.Column(spacing=10)
        self.panel_macros = ft.Column(spacing=14)
        self.panel_evolucion = ft.Column(spacing=8)

    # ── Vista ───────────────────────────────────────────────────

    def build(self) -> ft.Control:
        if not self.paciente:
            return estado_vacio(
                "Paciente no encontrado",
                "El expediente solicitado no existe o fue eliminado.",
                ft.Icons.PERSON_OFF,
            )

        self._actualizar_paneles(actualizar=False)
        self._refrescar_evolucion()

        return ft.Column(
            expand=True,
            spacing=18,
            controls=[
                self._build_encabezado(),
                ft.Row(
                    spacing=18,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            width=360,
                            spacing=18,
                            controls=[
                                self._build_datos_card(),
                                tarjeta(
                                    ft.Column(
                                        spacing=12,
                                        controls=[
                                            titulo_seccion(
                                                "Evolución de peso",
                                                ft.Icons.TRENDING_UP,
                                            ),
                                            self.panel_evolucion,
                                        ],
                                    )
                                ),
                            ],
                        ),
                        ft.Column(
                            expand=True,
                            spacing=18,
                            controls=[
                                self._build_resultados_card(),
                                self._build_macros_card(),
                            ],
                        ),
                    ],
                ),
            ],
        )

    def _build_encabezado(self) -> ft.Control:
        p = self.paciente
        self.lbl_nombre_header = ft.Text(
            p.nombre,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=COLOR_TEXT_PRIMARY,
        )
        self.lbl_meta_header = ft.Text(
            f"{p.edad} años · {p.genero} · "
            f"{etiqueta_actividad(normalizar_factor_actividad(p.actividad_fisica))}",
            size=12,
            color=COLOR_TEXT_SECONDARY,
        )
        botones = []
        if self.on_crear_plan:
            botones.append(
                boton_primario(
                    "Crear plan de alimentación",
                    self._crear_plan,
                    icono=ft.Icons.RESTAURANT_MENU,
                    width=250,
                )
            )

        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=COLOR_AZUL_ACERO,
                            tooltip="Volver a pacientes",
                            on_click=self._volver,
                        ),
                        ft.Container(
                            width=46,
                            height=46,
                            border_radius=23,
                            bgcolor=COLOR_ACENTO + "18",
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.PERSON,
                                size=24,
                                color=COLOR_ACENTO,
                            ),
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                self.lbl_nombre_header,
                                self.lbl_meta_header,
                            ],
                        ),
                    ],
                ),
                ft.Row(spacing=8, controls=botones),
            ],
        )

    def _build_datos_card(self) -> ft.Control:
        contenido = ft.Column(
            spacing=14,
            controls=[
                titulo_seccion(
                    "Datos antropométricos", ft.Icons.MONITOR_WEIGHT
                ),
                campo_etiquetado(
                    "Nombre completo",
                    self.campo_nombre,
                    icono=ft.Icons.PERSON,
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        campo_etiquetado(
                            "Edad", self.campo_edad, expand=1
                        ),
                        campo_etiquetado(
                            "Estatura (cm)",
                            self.campo_estatura,
                            expand=1,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        campo_etiquetado(
                            "Peso actual (kg)",
                            self.campo_peso,
                            expand=1,
                        ),
                        campo_etiquetado(
                            "Peso objetivo (kg)",
                            self.campo_peso_objetivo,
                            expand=1,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        campo_etiquetado(
                            "Género", self.campo_genero, expand=1
                        ),
                        campo_etiquetado(
                            "Actividad",
                            self.campo_actividad,
                            expand=1,
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        boton_primario(
                            "Guardar y registrar medición",
                            self._guardar,
                            icono=ft.Icons.SAVE,
                        )
                    ],
                ),
            ],
        )
        return tarjeta(contenido)

    def _build_resultados_card(self) -> ft.Control:
        return tarjeta(
            ft.Column(
                spacing=14,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            titulo_seccion(
                                "Evaluación nutricional",
                                ft.Icons.ASSESSMENT,
                            ),
                            chip(
                                "Cálculo en tiempo real", "info"
                            ),
                        ],
                    ),
                    self.panel_resultados,
                ],
            )
        )

    def _build_macros_card(self) -> ft.Control:
        porcentajes = ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        titulo_seccion(
                            "Distribución de macronutrientes",
                            ft.Icons.PIE_CHART if hasattr(ft.Icons, "PIE_CHART") else ft.Icons.INSIGHTS,
                        ),
                        chip(
                            "La suma debe ser 100 %", "advertencia"
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        campo_etiquetado(
                            "Proteínas (%)",
                            self.campo_proteinas,
                            expand=1,
                        ),
                        campo_etiquetado(
                            "Carbohidratos (%)",
                            self.campo_carbohidratos,
                            expand=1,
                        ),
                        campo_etiquetado(
                            "Grasas (%)", self.campo_grasas, expand=1
                        ),
                    ],
                ),
            ],
        )
        return tarjeta(
            ft.Column(
                spacing=16,
                controls=[porcentajes, self.panel_macros],
            )
        )

    # ── Cálculos ────────────────────────────────────────────────

    def _campo_porcentaje(self, valor: str) -> ft.TextField:
        return campo(
            "0",
            value=valor,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._recalcular,
            text_align=ft.TextAlign.CENTER,
        )

    def _leer_numeros(self) -> dict:
        try:
            peso = float((self.campo_peso.value or "").strip())
            estatura = float(
                (self.campo_estatura.value or "").strip()
            )
            edad = int((self.campo_edad.value or "").strip())
        except ValueError:
            raise ValueError(
                "Complete peso, estatura y edad con valores numéricos."
            ) from None

        if peso <= 0 or estatura <= 0 or edad <= 0:
            raise ValueError(
                "Peso, estatura y edad deben ser mayores que cero."
            )

        texto_objetivo = (self.campo_peso_objetivo.value or "").strip()
        peso_objetivo = None
        if texto_objetivo:
            try:
                peso_objetivo = float(texto_objetivo)
            except ValueError:
                raise ValueError(
                    "El peso objetivo debe ser numérico."
                ) from None

        genero = self.campo_genero.value or "Otro"
        factor = normalizar_factor_actividad(
            float(self.campo_actividad.value or "1.2")
        )

        return {
            "peso": peso,
            "estatura": estatura,
            "edad": edad,
            "genero": genero,
            "factor": factor,
            "peso_objetivo": peso_objetivo,
        }

    def _leer_porcentajes(self) -> tuple[float, float, float]:
        try:
            proteinas = float(
                (self.campo_proteinas.value or "").strip()
            )
            carbohidratos = float(
                (self.campo_carbohidratos.value or "").strip()
            )
            grasas = float((self.campo_grasas.value or "").strip())
        except ValueError:
            raise ValueError(
                "Los porcentajes deben ser valores numéricos."
            ) from None
        return proteinas, carbohidratos, grasas

    def _actualizar_paneles(self, actualizar: bool = True):
        try:
            datos = self._leer_numeros()
            proteinas, carbohidratos, grasas = self._leer_porcentajes()
            resultado = calcular_resultado(
                peso_kg=datos["peso"],
                estatura_cm=datos["estatura"],
                edad=datos["edad"],
                genero=datos["genero"],
                factor_actividad=datos["factor"],
                peso_objetivo=datos["peso_objetivo"],
            )
            distribucion = distribuir_macronutrientes(
                resultado.get,
                proteinas,
                carbohidratos,
                grasas,
            )
        except ValueError as error:
            self.panel_resultados.controls = [
                ft.Container(
                    bgcolor=TONOS["advertencia"][1],
                    border_radius=10,
                    padding=14,
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.INFO_OUTLINE,
                                size=18,
                                color=TONOS["advertencia"][0],
                            ),
                            ft.Text(
                                str(error),
                                size=12,
                                color=TONOS["advertencia"][0],
                                expand=True,
                            ),
                        ],
                    ),
                )
            ]
            self.panel_macros.controls = []
            if actualizar:
                self._actualizar(*(
                    self.panel_resultados,
                    self.panel_macros,
                ))
            return

        self.resultado = resultado
        self.distribucion = distribucion
        self.panel_resultados.controls = self._construir_resultados(
            resultado
        )
        self.panel_macros.controls = self._construir_macros(
            resultado, distribucion
        )
        if actualizar:
            self._actualizar(*(
                self.panel_resultados,
                self.panel_macros,
            ))

    def _actualizar(self, *controles):
        for control in controles:
            try:
                control.update()
            except RuntimeError:
                pass

    def _construir_resultados(self, resultado) -> list[ft.Control]:
        tono_imc = resultado.tono
        return [
            ft.Row(
                spacing=10,
                controls=[
                    self._caja_resultado(
                        "IMC",
                        f"{resultado.imc:.1f}",
                        "kg/m²",
                        ft.Icons.SCALE,
                        tono_imc,
                        resultado.clasificacion,
                    ),
                    self._caja_resultado(
                        "GEB",
                        f"{resultado.geb:.0f}",
                        "kcal/día",
                        ft.Icons.LOCAL_FIRE_DEPARTMENT,
                        "info",
                        "Mifflin-St. Jeor",
                    ),
                    self._caja_resultado(
                        "GET",
                        f"{resultado.get:.0f}",
                        "kcal/día",
                        ft.Icons.FITNESS_CENTER,
                        "normal",
                        f"Factor {resultado.factor_actividad:g}",
                    ),
                ],
            ),
            ft.Container(
                bgcolor=COLOR_INPUT_BG,
                border_radius=10,
                padding=12,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(
                                    "Peso saludable estimado",
                                    size=11,
                                    color=COLOR_TEXT_SECONDARY,
                                ),
                                ft.Text(
                                    f"{resultado.peso_ideal_min:.1f} – "
                                    f"{resultado.peso_ideal_max:.1f} kg",
                                    size=13,
                                    weight=ft.FontWeight.W_600,
                                    color=COLOR_TEXT_PRIMARY,
                                ),
                            ],
                        ),
                        self._diferencia_objetivo(resultado),
                    ],
                ),
            ),
        ]

    def _caja_resultado(
        self,
        etiqueta: str,
        valor: str,
        unidad: str,
        icono,
        tono: str,
        detalle: str,
    ) -> ft.Control:
        color, fondo = TONOS.get(tono, TONOS["info"])
        return ft.Container(
            expand=True,
            bgcolor=fondo,
            border_radius=12,
            padding=14,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Icon(icono, size=16, color=color),
                            ft.Text(
                                etiqueta,
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=color,
                            ),
                        ],
                    ),
                    ft.Text(
                        valor,
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXT_PRIMARY,
                    ),
                    ft.Text(unidad, size=10, color=COLOR_TEXT_SECONDARY),
                    ft.Text(
                        detalle,
                        size=11,
                        weight=ft.FontWeight.W_600,
                        color=color,
                    ),
                ],
            ),
        )

    def _diferencia_objetivo(self, resultado) -> ft.Control:
        if resultado.peso_objetivo is None:
            return ft.Column(
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.END,
                controls=[
                    ft.Text(
                        "Peso objetivo",
                        size=11,
                        color=COLOR_TEXT_SECONDARY,
                    ),
                    ft.Text(
                        "No definido",
                        size=13,
                        color=COLOR_TEXT_MUTED,
                    ),
                ],
            )

        diferencia = resultado.diferencia_objetivo or 0
        if abs(diferencia) < 0.1:
            texto = "En objetivo"
            color = TONOS["normal"][0]
        elif diferencia < 0:
            texto = f"{abs(diferencia):.1f} kg por perder"
            color = TONOS["advertencia"][0]
        else:
            texto = f"{diferencia:.1f} kg por ganar"
            color = TONOS["info"][0]

        return ft.Column(
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            controls=[
                ft.Text(
                    "Respecto al objetivo",
                    size=11,
                    color=COLOR_TEXT_SECONDARY,
                ),
                ft.Text(
                    texto,
                    size=13,
                    weight=ft.FontWeight.W_600,
                    color=color,
                ),
            ],
        )

    def _construir_macros(self, resultado, distribucion) -> list[ft.Control]:
        return [
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        "Objetivo energético",
                        size=12,
                        color=COLOR_TEXT_SECONDARY,
                    ),
                    ft.Text(
                        f"{resultado.get:.0f} kcal/día",
                        size=13,
                        weight=ft.FontWeight.W_600,
                        color=COLOR_TEXT_PRIMARY,
                    ),
                ],
            ),
            ft.Row(
                spacing=4,
                controls=[
                    ft.Container(
                        expand=max(1, int(distribucion.porcentaje_proteinas)),
                        height=10,
                        border_radius=4,
                        bgcolor=COLOR_ACENTO,
                    ),
                    ft.Container(
                        expand=max(
                            1, int(distribucion.porcentaje_carbohidratos)
                        ),
                        height=10,
                        border_radius=4,
                        bgcolor=COLOR_AZUL_ACERO,
                    ),
                    ft.Container(
                        expand=max(1, int(distribucion.porcentaje_grasas)),
                        height=10,
                        border_radius=4,
                        bgcolor="#B89A5A",
                    ),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    self._macro_card(
                        "Proteínas",
                        distribucion.gramos_proteinas,
                        distribucion.porcentaje_proteinas,
                        distribucion.kcal_proteinas,
                        COLOR_ACENTO,
                    ),
                    self._macro_card(
                        "Carbohidratos",
                        distribucion.gramos_carbohidratos,
                        distribucion.porcentaje_carbohidratos,
                        distribucion.kcal_carbohidratos,
                        COLOR_AZUL_ACERO,
                    ),
                    self._macro_card(
                        "Grasas",
                        distribucion.gramos_grasas,
                        distribucion.porcentaje_grasas,
                        distribucion.kcal_grasas,
                        "#B89A5A",
                    ),
                ],
            ),
        ]

    def _macro_card(
        self,
        nombre: str,
        gramos: float,
        porcentaje: float,
        kcal: float,
        color: str,
    ) -> ft.Control:
        return ft.Container(
            expand=True,
            bgcolor=COLOR_INPUT_BG,
            border_radius=12,
            padding=12,
            content=ft.Column(
                spacing=3,
                controls=[
                    ft.Row(
                        spacing=6,
                        controls=[
                            ft.Container(
                                width=8,
                                height=8,
                                border_radius=4,
                                bgcolor=color,
                            ),
                            ft.Text(
                                nombre,
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=COLOR_TEXT_SECONDARY,
                            ),
                        ],
                    ),
                    ft.Text(
                        f"{gramos:.0f} g",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_TEXT_PRIMARY,
                    ),
                    ft.Text(
                        f"{porcentaje:.0f} % · {kcal:.0f} kcal",
                        size=10,
                        color=COLOR_TEXT_SECONDARY,
                    ),
                ],
            ),
        )

    def _refrescar_evolucion(self):
        mediciones = self.db.obtener_mediciones(self.paciente.id)
        if not mediciones:
            self.panel_evolucion.controls = [
                estado_vacio(
                    "Sin mediciones registradas.",
                    "Guarde la ficha para iniciar el seguimiento.",
                    ft.Icons.SHOW_CHART
                    if hasattr(ft.Icons, "SHOW_CHART")
                    else ft.Icons.INSIGHTS,
                )
            ]
            return

        ultimas = mediciones[-8:]
        peso_maximo = max(m.peso for m in ultimas)
        filas = []
        peso_previo = None
        for medicion in ultimas:
            ancho = max(14, int(150 * medicion.peso / peso_maximo))
            if peso_previo is None:
                delta = ""
                color_delta = COLOR_TEXT_MUTED
            else:
                diferencia = medicion.peso - peso_previo
                delta = f"{diferencia:+.1f} kg"
                color_delta = (
                    TONOS["advertencia"][0]
                    if diferencia > 0
                    else TONOS["normal"][0]
                )
            filas.append(
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            medicion.fecha.strftime("%d/%m"),
                            size=10,
                            width=40,
                            color=COLOR_TEXT_SECONDARY,
                        ),
                        ft.Container(
                            width=150,
                            height=8,
                            border_radius=4,
                            bgcolor=COLOR_INPUT_BG,
                            content=ft.Container(
                                width=ancho,
                                height=8,
                                border_radius=4,
                                bgcolor=COLOR_ACENTO,
                            ),
                        ),
                        ft.Text(
                            f"{medicion.peso:.1f} kg",
                            size=11,
                            weight=ft.FontWeight.W_600,
                            color=COLOR_TEXT_PRIMARY,
                            width=52,
                        ),
                        ft.Text(delta, size=10, color=color_delta),
                    ],
                )
            )
            peso_previo = medicion.peso

        self.panel_evolucion.controls = filas

    # ── Eventos ─────────────────────────────────────────────────

    def _recalcular(self, e=None):
        self._actualizar_paneles(actualizar=True)

    def _guardar(self, e):
        try:
            datos = self._leer_numeros()
        except ValueError as error:
            mostrar_snack(self.page, str(error), "peligro")
            return

        p = self.paciente
        p.nombre = (self.campo_nombre.value or "").strip() or p.nombre
        p.edad = datos["edad"]
        p.estatura = datos["estatura"]
        p.peso_actual = datos["peso"]
        p.peso_objetivo = datos["peso_objetivo"]
        p.genero = datos["genero"]
        p.actividad_fisica = datos["factor"]
        self.db.actualizar_paciente(p)

        mediciones = self.db.obtener_mediciones(p.id)
        registro_medicion = False
        if not mediciones or abs(mediciones[-1].peso - p.peso_actual) > 0.05:
            self.db.registrar_medicion(
                p.id, p.peso_actual, p.estatura
            )
            registro_medicion = True

        self._refrescar_evolucion()
        self._actualizar_paneles()
        self.lbl_nombre_header.value = p.nombre
        self.lbl_meta_header.value = (
            f"{p.edad} años · {p.genero} · "
            f"{etiqueta_actividad(normalizar_factor_actividad(p.actividad_fisica))}"
        )
        self._actualizar(
            self.panel_evolucion,
            self.lbl_nombre_header,
            self.lbl_meta_header,
        )
        mensaje = (
            "Ficha actualizada y medición registrada."
            if registro_medicion
            else "Ficha actualizada correctamente."
        )
        mostrar_snack(self.page, mensaje)

    def _crear_plan(self, e):
        if self.on_crear_plan:
            self.on_crear_plan(self.paciente.id)

    def _volver(self, e):
        if self.on_volver:
            self.on_volver()

