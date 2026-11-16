import flet as ft

from src.config import (
    COLOR_ACENTO,
    COLOR_MENU_ACTIVO_BG,
    COLOR_MENU_BG,
    COLOR_MENU_HOVER,
    COLOR_MENU_ICON,
    COLOR_MENU_ICON_ACTIVO,
    COLOR_MENU_TEXT,
    COLOR_MENU_TEXT_ACTIVO,
    COLOR_TEXT_PRIMARY,
)


class MenuLateral:
    def __init__(self, on_change, seleccionado: int = 1):
        self.on_change = on_change
        self.seleccionado = seleccionado
        self.items_data = [
            ("Dashboard", ft.Icons.GRID_VIEW),
            ("Pacientes", ft.Icons.PERSON),
            ("Planes de Dieta", ft.Icons.RESTAURANT_MENU),
            ("Alimentos", ft.Icons.FOOD_BANK),
            ("Configuración", ft.Icons.SETTINGS_ROUNDED),
        ]
        self.column_container: ft.Column | None = None

    def build(self) -> ft.Control:
        self.column_container = ft.Column(
            spacing=4,
            controls=[
                self._build_item(idx, label, icon)
                for idx, (label, icon) in enumerate(self.items_data)
            ],
        )
        return ft.Container(
            width=220,
            bgcolor=COLOR_MENU_BG,
            padding=ft.Padding.only(left=14, right=14, top=28, bottom=20),
            content=ft.Column(
                spacing=0,
                controls=[
                    # Logo / Título de la app
                    ft.Container(
                        padding=ft.Padding.only(left=10, bottom=24),
                        content=ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(
                                    ft.Icons.SPA_OUTLINED,
                                    size=22,
                                    color=COLOR_ACENTO,
                                ),
                                ft.Text(
                                    "Nutri-AS",
                                    size=17,
                                    weight=ft.FontWeight.W_600,
                                    color=COLOR_TEXT_PRIMARY,
                                ),
                            ],
                        ),
                    ),
                    ft.Container(height=8),
                    self.column_container,
                ],
            ),
        )

    def _build_item(self, idx: int, label: str, icon: str) -> ft.Control:
        activo = idx == self.seleccionado
        return ft.Container(
            border_radius=10,
            bgcolor=COLOR_MENU_ACTIVO_BG if activo else ft.Colors.TRANSPARENT,
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            ink=True,
            ink_color=COLOR_MENU_HOVER,
            on_click=lambda e, i=idx: self._on_item_click(i),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        icon,
                        size=20,
                        color=COLOR_MENU_ICON_ACTIVO if activo else COLOR_MENU_ICON,
                    ),
                    ft.Text(
                        label,
                        size=14,
                        weight=ft.FontWeight.W_500 if activo else ft.FontWeight.NORMAL,
                        color=COLOR_MENU_TEXT_ACTIVO if activo else COLOR_MENU_TEXT,
                    ),
                ],
            ),
        )

    def seleccionar(self, index: int):
        """Marca un item como activo sin disparar la navegación."""
        self.seleccionado = index
        self._refrescar_items()

    def _refrescar_items(self):
        if not self.column_container:
            return
        self.column_container.controls = [
            self._build_item(idx, label, icon)
            for idx, (label, icon) in enumerate(self.items_data)
        ]
        try:
            self.column_container.update()
        except RuntimeError:
            pass

    def _on_item_click(self, index: int):
        if self.seleccionado == index:
            return
        self.seleccionar(index)
        if self.on_change:
            self.on_change(index)
