import flet as ft

from src.components.ui import chip
from src.config import (
    COLOR_AZUL_ACERO,
    COLOR_ACENTO,
    COLOR_ACENTO_LIGHT,
    COLOR_CARD_BG,
    COLOR_PELIGRO,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)
from src.models import Paciente
from src.nutricion import (
    calcular_imc,
    clasificar_imc,
    etiqueta_actividad,
    normalizar_factor_actividad,
)


class PacienteCard:
    def __init__(
        self,
        paciente: Paciente,
        on_click=None,
        on_editar=None,
        on_eliminar=None,
    ):
        self.paciente = paciente
        self.on_click = on_click
        self.on_editar = on_editar
        self.on_eliminar = on_eliminar

    def build(self) -> ft.Control:
        p = self.paciente
        return ft.Container(
            bgcolor=COLOR_CARD_BG,
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=18, vertical=12),
            ink=bool(self.on_click),
            on_click=self._abrir if self.on_click else None,
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=12,
                controls=[
                    ft.Row(
                        spacing=12,
                        expand=True,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=38,
                                height=38,
                                border_radius=19,
                                bgcolor=COLOR_ACENTO_LIGHT,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    ft.Icons.PERSON_OUTLINE,
                                    size=19,
                                    color=COLOR_ACENTO,
                                ),
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        p.nombre,
                                        size=14,
                                        weight=ft.FontWeight.W_600,
                                        color=COLOR_TEXT_PRIMARY,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        f"{p.edad} años · {p.genero} · "
                                        f"{etiqueta_actividad(normalizar_factor_actividad(p.actividad_fisica))}",
                                        size=11,
                                        color=COLOR_TEXT_SECONDARY,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=22,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self._dato("Peso", f"{p.peso_actual:.1f} kg"),
                            self._dato("Estatura", f"{p.estatura:.0f} cm"),
                            self._imc(),
                        ],
                    ),
                    ft.Row(
                        spacing=2,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=18,
                                icon_color=COLOR_AZUL_ACERO,
                                tooltip="Editar paciente",
                                on_click=self._editar,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=18,
                                icon_color=COLOR_PELIGRO,
                                tooltip="Eliminar paciente",
                                on_click=self._eliminar,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _imc(self) -> ft.Control:
        p = self.paciente
        if not p.estatura or p.estatura <= 0 or not p.peso_actual:
            return chip("Sin IMC", "info")
        imc = calcular_imc(p.peso_actual, p.estatura)
        clasificacion, tono = clasificar_imc(imc)
        return ft.Column(
            spacing=3,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            controls=[
                ft.Text(
                    f"IMC {imc:.1f}",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=COLOR_TEXT_PRIMARY,
                ),
                chip(clasificacion, tono),
            ],
        )

    def _dato(self, etiqueta: str, valor: str) -> ft.Control:
        return ft.Column(
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            controls=[
                ft.Text(etiqueta, size=11, color=COLOR_TEXT_MUTED),
                ft.Text(
                    valor,
                    size=13,
                    weight=ft.FontWeight.W_500,
                    color=COLOR_TEXT_PRIMARY,
                ),
            ],
        )

    def _abrir(self, e):
        if self.on_click:
            self.on_click(self.paciente)

    def _editar(self, e):
        if self.on_editar:
            self.on_editar(self.paciente)

    def _eliminar(self, e):
        if self.on_eliminar:
            self.on_eliminar(self.paciente)
