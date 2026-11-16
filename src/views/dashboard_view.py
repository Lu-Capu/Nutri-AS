from datetime import datetime

import flet as ft

from src.components.ui import (
    TONOS,
    barra_progreso,
    boton_primario,
    boton_secundario,
    chip,
    encabezado,
    estado_vacio,
    stat_card,
    tarjeta,
    titulo_seccion,
)
from src.config import (
    COLOR_ACENTO,
    COLOR_ACENTO_LIGHT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)
from src.database import Database
from src.models import Paciente
from src.nutricion import calcular_imc, clasificar_imc

MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


class DashboardView:
    def __init__(
        self,
        page: ft.Page,
        db: Database,
        on_abrir_paciente=None,
        on_navegar=None,
    ):
        self.page = page
        self.db = db
        self.on_abrir_paciente = on_abrir_paciente
        self.on_navegar = on_navegar

    def build(self) -> ft.Control:
        metricas = self.db.obtener_metricas_dashboard()
        total_pacientes = metricas["total_pacientes"]
        total_planes = metricas["total_planes"]
        total_alimentos = metricas["total_alimentos"]
        promedio_val = metricas["promedio_imc"]

        if promedio_val is not None:
            clasificacion, tono_imc = clasificar_imc(promedio_val)
            promedio_imc = f"{promedio_val:.1f}"
            detalle_imc = clasificacion
        else:
            promedio_imc, detalle_imc, tono_imc = "—", "Sin datos suficientes", "info"

        pacientes_recientes = metricas["pacientes_recientes"]
        hoy = datetime.now()
        subtitulo = (
            f"Resumen de la consulta · {hoy.day} de "
            f"{MESES[hoy.month - 1]} de {hoy.year}"
        )

        pacientes_todos = self.db.obtener_pacientes() if total_pacientes > 0 else []

        return ft.Column(
            expand=True,
            spacing=18,
            controls=[
                encabezado("Panel de Control", subtitulo),
                ft.Row(
                    spacing=14,
                    controls=[
                        stat_card("Pacientes", str(total_pacientes), ft.Icons.PEOPLE, "normal", "Expedientes registrados"),
                        stat_card("Planes guardados", str(total_planes), ft.Icons.RESTAURANT_MENU, "info", "Planes de alimentación"),
                        stat_card("Alimentos", str(total_alimentos), ft.Icons.FOOD_BANK, "info", "En el catálogo interno"),
                        stat_card("IMC promedio", promedio_imc, ft.Icons.SCALE, tono_imc, detalle_imc),
                    ],
                ),
                ft.Row(
                    expand=True,
                    spacing=18,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        self._tarjeta_pacientes(pacientes_recientes),
                        ft.Column(
                            width=330,
                            spacing=18,
                            controls=[
                                self._tarjeta_accesos(),
                                self._tarjeta_distribucion(pacientes_todos),
                            ],
                        ),
                    ],
                ),
            ],
        )

    def _tarjeta_pacientes(self, pacientes: list[Paciente]) -> ft.Control:
        if pacientes:
            filas = [self._fila_paciente(paciente) for paciente in pacientes[:8]]
            contenido = ft.ListView(expand=True, spacing=8, padding=0, controls=filas)
        else:
            contenido = estado_vacio(
                "Aún no hay pacientes registrados.",
                "Comience registrando un nuevo paciente.",
                ft.Icons.PERSON_ADD,
            )

        return tarjeta(
            ft.Column(
                expand=True,
                spacing=12,
                controls=[
                    titulo_seccion("Pacientes recientes", ft.Icons.HISTORY),
                    contenido,
                ],
            ),
            expand=True,
        )

    def _fila_paciente(self, paciente: Paciente) -> ft.Control:
        if paciente.estatura and paciente.peso_actual:
            imc = calcular_imc(paciente.peso_actual, paciente.estatura)
            clasificacion, tono = clasificar_imc(imc)
        else:
            imc = None
            clasificacion, tono = "Sin IMC", "info"

        return ft.Container(
            bgcolor="#FAFAF8",
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            ink=bool(self.on_abrir_paciente),
            on_click=(
                lambda e, p=paciente: self._abrir(p)
                if self.on_abrir_paciente
                else None
            ),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=32,
                        height=32,
                        border_radius=16,
                        bgcolor=COLOR_ACENTO_LIGHT,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.PERSON_OUTLINE, size=16, color=COLOR_ACENTO),
                    ),
                    ft.Column(
                        spacing=1,
                        expand=True,
                        controls=[
                            ft.Text(
                                paciente.nombre,
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=COLOR_TEXT_PRIMARY,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{paciente.edad} años · {paciente.peso_actual:.1f} kg",
                                size=10,
                                color=COLOR_TEXT_SECONDARY,
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=2,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Text(
                                f"IMC {imc:.1f}" if imc else "—",
                                size=11,
                                color=COLOR_TEXT_SECONDARY,
                            ),
                            chip(clasificacion, tono),
                        ],
                    ),
                ],
            ),
        )

    def _tarjeta_accesos(self) -> ft.Control:
        return tarjeta(
            ft.Column(
                spacing=12,
                controls=[
                    titulo_seccion(
                        "Accesos rápidos",
                        ft.Icons.BOLT if hasattr(ft.Icons, "BOLT") else ft.Icons.INSIGHTS,
                    ),
                    boton_primario("Nuevo paciente", lambda e: self._navegar(1), icono=ft.Icons.PERSON_ADD),
                    boton_secundario("Crear plan de dieta", lambda e: self._navegar(2), icono=ft.Icons.RESTAURANT_MENU),
                    boton_secundario("Catálogo de alimentos", lambda e: self._navegar(3), icono=ft.Icons.FOOD_BANK),
                ],
            )
        )

    def _tarjeta_distribucion(self, pacientes: list[Paciente]) -> ft.Control:
        grupos = {
            "Bajo peso": (0, TONOS["advertencia"][0]),
            "Peso normal": (0, TONOS["normal"][0]),
            "Sobrepeso": (0, TONOS["advertencia"][0]),
            "Obesidad": (0, TONOS["peligro"][0]),
        }
        for paciente in pacientes:
            if not paciente.peso_actual or not paciente.estatura:
                continue
            imc = calcular_imc(paciente.peso_actual, paciente.estatura)
            if imc < 18.5:
                grupos["Bajo peso"] = (grupos["Bajo peso"][0] + 1, grupos["Bajo peso"][1])
            elif imc < 25:
                grupos["Peso normal"] = (grupos["Peso normal"][0] + 1, grupos["Peso normal"][1])
            elif imc < 30:
                grupos["Sobrepeso"] = (grupos["Sobrepeso"][0] + 1, grupos["Sobrepeso"][1])
            else:
                grupos["Obesidad"] = (grupos["Obesidad"][0] + 1, grupos["Obesidad"][1])

        total = sum(cantidad for cantidad, _ in grupos.values())
        filas = []
        for nombre, (cantidad, color) in grupos.items():
            proporcion = cantidad / total if total else 0
            filas.append(
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(nombre, size=11, color=COLOR_TEXT_SECONDARY),
                                ft.Text(str(cantidad), size=11, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY),
                            ],
                        ),
                        barra_progreso(proporcion, color),
                    ],
                )
            )

        return tarjeta(
            ft.Column(
                spacing=12,
                controls=[
                    titulo_seccion("Estado nutricional", ft.Icons.INSIGHTS),
                    *(
                        filas
                        if total
                        else [
                            ft.Text(
                                "Sin datos antropométricos para graficar.",
                                size=11,
                                color=COLOR_TEXT_MUTED,
                            )
                        ]
                    ),
                ],
            )
        )

    def _abrir(self, paciente: Paciente):
        if self.on_abrir_paciente:
            self.on_abrir_paciente(paciente.id)

    def _navegar(self, indice: int):
        if self.on_navegar:
            self.on_navegar(indice)
