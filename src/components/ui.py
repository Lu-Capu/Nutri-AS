"""Componentes y helpers visuales reutilizables."""

import flet as ft

from src.config import (
    COLOR_ACENTO,
    COLOR_ACENTO_HOVER,
    COLOR_ADVERTENCIA,
    COLOR_ADVERTENCIA_LIGHT,
    COLOR_AZUL_ACERO,
    COLOR_AZUL_ACERO_LIGHT,
    COLOR_BORDER,
    COLOR_CARD_BG,
    COLOR_EXITO,
    COLOR_EXITO_LIGHT,
    COLOR_INPUT_BG,
    COLOR_INPUT_BORDER,
    COLOR_INPUT_FOCUSED_BORDER,
    COLOR_PELIGRO,
    COLOR_PELIGRO_LIGHT,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_ON_ACCENT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)

TONOS = {
    "normal": (COLOR_EXITO, COLOR_EXITO_LIGHT),
    "exito": (COLOR_EXITO, COLOR_EXITO_LIGHT),
    "advertencia": (COLOR_ADVERTENCIA, COLOR_ADVERTENCIA_LIGHT),
    "peligro": (COLOR_PELIGRO, COLOR_PELIGRO_LIGHT),
    "info": (COLOR_AZUL_ACERO, COLOR_AZUL_ACERO_LIGHT),
}


# ── Contenedores ────────────────────────────────────────────────

def tarjeta(
    contenido: ft.Control,
    padding: int | ft.Padding = 20,
    expand: bool | int = False,
) -> ft.Container:
    return ft.Container(
        content=contenido,
        bgcolor=COLOR_CARD_BG,
        border_radius=12,
        padding=padding,
        expand=expand,
    )


def encabezado(
    titulo: str,
    subtitulo: str | None = None,
    acciones: list[ft.Control] | None = None,
) -> ft.Control:
    textos = [
        ft.Text(
            titulo,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=COLOR_TEXT_PRIMARY,
        )
    ]
    if subtitulo:
        textos.append(
            ft.Text(subtitulo, size=13, color=COLOR_TEXT_SECONDARY)
        )
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(spacing=4, controls=textos),
            ft.Row(spacing=8, controls=acciones or []),
        ],
    )


def titulo_seccion(texto: str, icono=None) -> ft.Control:
    controles = []
    if icono:
        controles.append(ft.Icon(icono, size=18, color=COLOR_AZUL_ACERO))
    controles.append(
        ft.Text(
            texto,
            size=16,
            weight=ft.FontWeight.W_600,
            color=COLOR_TEXT_PRIMARY,
        )
    )
    return ft.Row(
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=controles,
    )


# ── Campos de formulario ────────────────────────────────────────

def campo(
    hint: str,
    value: str = "",
    keyboard_type=ft.KeyboardType.TEXT,
    prefix_icon=None,
    suffix_icon=None,
    width=None,
    expand: bool | int | None = None,
    on_change=None,
    on_submit=None,
    read_only: bool = False,
    text_align=ft.TextAlign.LEFT,
) -> ft.TextField:
    return ft.TextField(
        value=value,
        hint_text=hint,
        keyboard_type=keyboard_type,
        prefix_icon=prefix_icon,
        suffix_icon=suffix_icon,
        width=width,
        expand=expand,
        on_change=on_change,
        on_submit=on_submit,
        read_only=read_only,
        text_align=text_align,
        bgcolor=COLOR_INPUT_BG,
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=COLOR_INPUT_FOCUSED_BORDER,
        border_radius=10,
        dense=True,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        text_size=14,
        color=COLOR_TEXT_PRIMARY,
        hint_style=ft.TextStyle(size=14, color=COLOR_TEXT_MUTED),
    )


def dropdown(
    hint: str,
    opciones: list[tuple[str, str]],
    value: str | None = None,
    on_select=None,
    width=None,
    expand: bool | int | None = None,
) -> ft.Dropdown:
    return ft.Dropdown(
        value=value,
        hint_text=hint,
        options=[
            ft.DropdownOption(key=clave, text=texto)
            for clave, texto in opciones
        ],
        on_select=on_select,
        width=width,
        expand=expand,
        bgcolor=COLOR_INPUT_BG,
        border_color=ft.Colors.TRANSPARENT,
        focused_border_color=COLOR_INPUT_FOCUSED_BORDER,
        border_radius=10,
        dense=True,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=10),
        text_size=14,
        color=COLOR_TEXT_PRIMARY,
        hint_style=ft.TextStyle(size=14, color=COLOR_TEXT_MUTED),
    )


def campo_etiquetado(
    etiqueta: str,
    control: ft.Control,
    expand: int = 1,
    icono=None,
) -> ft.Column:
    fila_etiqueta = []
    if icono:
        fila_etiqueta.append(
            ft.Icon(icono, size=14, color=COLOR_AZUL_ACERO)
        )
    fila_etiqueta.append(
        ft.Text(
            etiqueta,
            size=12,
            weight=ft.FontWeight.W_600,
            color=COLOR_TEXT_PRIMARY,
        )
    )
    return ft.Column(
        expand=expand,
        spacing=6,
        controls=[
            ft.Row(spacing=4, controls=fila_etiqueta),
            control,
        ],
    )


# ── Botones ─────────────────────────────────────────────────────

def _estilo_primario() -> ft.ButtonStyle:
    return ft.ButtonStyle(
        color=COLOR_TEXT_ON_ACCENT,
        bgcolor=COLOR_ACENTO,
        overlay_color=COLOR_ACENTO_HOVER,
        shape=ft.RoundedRectangleBorder(radius=10),
        padding=ft.Padding.symmetric(horizontal=18, vertical=10),
        elevation=0,
    )


def boton_primario(
    texto: str,
    on_click,
    icono=None,
    width=None,
    disabled: bool = False,
) -> ft.FilledButton:
    return ft.FilledButton(
        content=texto,
        icon=icono,
        icon_color=COLOR_TEXT_ON_ACCENT,
        height=44,
        width=width,
        disabled=disabled,
        style=_estilo_primario(),
        on_click=on_click,
    )


def boton_secundario(
    texto: str,
    on_click,
    icono=None,
    width=None,
    disabled: bool = False,
) -> ft.OutlinedButton:
    return ft.OutlinedButton(
        content=texto,
        icon=icono,
        icon_color=COLOR_TEXT_SECONDARY,
        height=42,
        width=width,
        disabled=disabled,
        style=ft.ButtonStyle(
            color=COLOR_TEXT_PRIMARY,
            bgcolor=COLOR_INPUT_BG,
            side=ft.BorderSide(0, ft.Colors.TRANSPARENT),
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.Padding.symmetric(horizontal=16, vertical=8),
        ),
        on_click=on_click,
    )


def boton_texto(
    texto: str,
    on_click,
    icono=None,
    color=COLOR_AZUL_ACERO,
) -> ft.TextButton:
    return ft.TextButton(
        content=texto,
        icon=icono,
        icon_color=color,
        style=ft.ButtonStyle(
            color=color,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
        ),
        on_click=on_click,
    )


# ── Indicadores ─────────────────────────────────────────────────

def chip(texto: str, tono: str = "info") -> ft.Container:
    color, fondo = TONOS.get(tono, TONOS["info"])
    return ft.Container(
        bgcolor=fondo,
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        content=ft.Text(
            texto,
            size=11,
            weight=ft.FontWeight.W_600,
            color=color,
        ),
    )


def barra_progreso(valor: float, color: str = COLOR_ACENTO) -> ft.ProgressBar:
    return ft.ProgressBar(
        value=max(0.0, min(valor, 1.0)),
        color=color,
        bgcolor=COLOR_INPUT_BG,
        bar_height=8,
        border_radius=4,
    )


def stat_card(
    etiqueta: str,
    valor: str,
    icono,
    tono: str = "normal",
    detalle: str | None = None,
) -> ft.Control:
    color, fondo = TONOS.get(tono, TONOS["normal"])
    controles = [
        ft.Text(
            valor,
            size=28,
            weight=ft.FontWeight.BOLD,
            color=COLOR_TEXT_PRIMARY,
        )
    ]
    if detalle:
        controles.append(
            ft.Text(detalle, size=11, color=COLOR_TEXT_SECONDARY)
        )
    return tarjeta(
        ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=46,
                    height=46,
                    border_radius=14,
                    bgcolor=fondo,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(icono, size=22, color=color),
                ),
                ft.Column(
                    spacing=2,
                    expand=True,
                    controls=[
                        ft.Text(
                            etiqueta,
                            size=12,
                            color=COLOR_TEXT_SECONDARY,
                        ),
                        *controles,
                    ],
                ),
            ],
        ),
        padding=16,
        expand=True,
    )


def separador() -> ft.Divider:
    return ft.Divider(height=1, color=COLOR_BORDER)


# ── Estados vacíos y mensajes ───────────────────────────────────

def estado_vacio(
    titulo: str,
    subtitulo: str | None = None,
    icono=ft.Icons.INFO_OUTLINE,
) -> ft.Control:
    controles = [
        ft.Icon(icono, size=42, color=COLOR_TEXT_MUTED),
        ft.Text(titulo, size=15, color=COLOR_TEXT_SECONDARY),
    ]
    if subtitulo:
        controles.append(
            ft.Text(
                subtitulo,
                size=12,
                color=COLOR_TEXT_MUTED,
                text_align=ft.TextAlign.CENTER,
            )
        )
    return ft.Container(
        padding=36,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=controles,
        ),
    )


def mostrar_snack(page: ft.Page, mensaje: str, tipo: str = "exito"):
    colores = {
        "exito": COLOR_EXITO,
        "advertencia": COLOR_ADVERTENCIA,
        "peligro": COLOR_PELIGRO,
        "info": COLOR_AZUL_ACERO,
    }
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=colores.get(tipo, COLOR_EXITO),
        )
    )


def confirmar(
    page: ft.Page,
    titulo: str,
    mensaje: str,
    al_confirmar,
    texto_confirmar: str = "Eliminar",
):
    def _cancelar(e):
        page.pop_dialog()

    def _aceptar(e):
        page.pop_dialog()
        al_confirmar()

    page.show_dialog(
        ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, size=18, weight=ft.FontWeight.W_600),
            content=ft.Text(mensaje, size=14, color=COLOR_TEXT_SECONDARY),
            actions=[
                ft.TextButton(
                    content="Cancelar",
                    on_click=_cancelar,
                    style=ft.ButtonStyle(color=COLOR_AZUL_ACERO),
                ),
                ft.FilledButton(
                    content=texto_confirmar,
                    on_click=_aceptar,
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_PELIGRO,
                        color=ft.Colors.WHITE,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
        )
    )


def safe_update(*controles: ft.Control | None):
    """Actualiza controles de Flet de forma segura ignorando excepciones de desmonte."""
    for c in controles:
        if c is not None:
            try:
                c.update()
            except Exception:
                pass

