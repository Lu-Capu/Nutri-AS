import flet as ft

from src.config import COLOR_AZUL_ACERO, COLOR_TEXT_MUTED, COLOR_TEXT_PRIMARY


class PlaceholderView:
    def __init__(self, titulo: str):
        self.titulo = titulo

    def build(self) -> ft.Control:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(
                        ft.Icons.CONSTRUCTION_ROUNDED,
                        size=48,
                        color=COLOR_AZUL_ACERO,
                    ),
                    ft.Text(
                        self.titulo,
                        size=20,
                        weight=ft.FontWeight.W_600,
                        color=COLOR_TEXT_PRIMARY,
                    ),
                    ft.Text(
                        "Próximamente",
                        size=14,
                        color=COLOR_TEXT_MUTED,
                    ),
                ],
            ),
        )
