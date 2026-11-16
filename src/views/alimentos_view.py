import flet as ft
from sqlalchemy.exc import IntegrityError

from src.components.ui import (
    boton_primario,
    boton_secundario,
    campo,
    campo_etiquetado,
    chip,
    confirmar,
    encabezado,
    estado_vacio,
    mostrar_snack,
    tarjeta,
    titulo_seccion,
)
from src.config import (
    COLOR_AZUL_ACERO,
    COLOR_CARD_BG,
    COLOR_BORDER,
    COLOR_PELIGRO,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
)
from src.database import Database
from src.models import Alimento


class AlimentosView:
    """Catálogo interno de alimentos con valores por porción base."""

    def __init__(self, page: ft.Page, db: Database):
        self.page = page
        self.db = db
        self.editando_id: int | None = None
        self._cache_alimentos: list[Alimento] | None = None

        self.campo_nombre = campo(
            "Ej. Pechuga de pollo cocida",
            prefix_icon=ft.Icons.RESTAURANT,
        )
        self.campo_categoria = campo(
            "Ej. Proteínas",
            value="General",
        )
        self.campo_porcion = campo(
            "100",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.campo_calorias = campo(
            "165",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.campo_proteinas = campo(
            "31",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.campo_carbohidratos = campo(
            "0",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.campo_grasas = campo(
            "3.6",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.campo_busqueda = campo(
            "Buscar alimento o categoría…",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._filtrar,
            width=320,
        )

        self.boton_guardar = boton_primario(
            "Agregar Alimento",
            self._guardar,
            icono=ft.Icons.ADD,
            width=230,
        )
        self.boton_cancelar = boton_secundario(
            "Cancelar edición",
            self._cancelar_edicion,
            icono=ft.Icons.CLOSE,
        )
        self.boton_cancelar.visible = False

        self.lista = ft.ListView(expand=True, spacing=8, padding=0)
        self.contador = chip("0 alimentos", "info")
        self.lista_card: ft.Container | None = None

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
                            "Nombre del alimento",
                            self.campo_nombre,
                            expand=3,
                            icono=ft.Icons.RESTAURANT,
                        ),
                        campo_etiquetado(
                            "Categoría",
                            self.campo_categoria,
                            expand=2,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        campo_etiquetado(
                            "Porción base (g)",
                            self.campo_porcion,
                            expand=1,
                        ),
                        campo_etiquetado(
                            "Calorías (kcal)",
                            self.campo_calorias,
                            expand=1,
                        ),
                        campo_etiquetado(
                            "Proteínas (g)",
                            self.campo_proteinas,
                            expand=1,
                        ),
                        campo_etiquetado(
                            "Carbohidratos (g)",
                            self.campo_carbohidratos,
                            expand=1,
                        ),
                        campo_etiquetado(
                            "Grasas (g)",
                            self.campo_grasas,
                            expand=1,
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
                    "Catálogo de Alimentos",
                    "Valores nutricionales por porción base",
                    [self.contador],
                ),
                tarjeta(formulario),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        titulo_seccion(
                            "Alimentos disponibles",
                            ft.Icons.FOOD_BANK,
                        ),
                        self.campo_busqueda,
                    ],
                ),
                self.lista_card,
            ],
        )

    # ── Lógica de negocio ───────────────────────────────────────

    def _guardar(self, e):
        nombre = (self.campo_nombre.value or "").strip()
        if not nombre:
            mostrar_snack(
                self.page, "El nombre del alimento es obligatorio.", "peligro"
            )
            return

        try:
            porcion = float((self.campo_porcion.value or "").strip())
            calorias = float((self.campo_calorias.value or "").strip())
            proteinas = float(
                (self.campo_proteinas.value or "").strip()
            )
            carbohidratos = float(
                (self.campo_carbohidratos.value or "").strip()
            )
            grasas = float((self.campo_grasas.value or "").strip())
        except ValueError:
            mostrar_snack(
                self.page,
                "Los valores nutricionales deben ser numéricos.",
                "peligro",
            )
            return

        if porcion <= 0 or calorias < 0:
            mostrar_snack(
                self.page,
                "La porción debe ser mayor que cero y las calorías "
                "no pueden ser negativas.",
                "peligro",
            )
            return
        if min(proteinas, carbohidratos, grasas) < 0:
            mostrar_snack(
                self.page,
                "Los macronutrientes no pueden ser negativos.",
                "peligro",
            )
            return

        alimento = Alimento(
            nombre=nombre,
            categoria=(self.campo_categoria.value or "General").strip()
            or "General",
            porcion_base=porcion,
            calorias=calorias,
            proteinas=proteinas,
            carbohidratos=carbohidratos,
            grasas=grasas,
        )

        try:
            if self.editando_id:
                alimento.id = self.editando_id
                self.db.actualizar_alimento(alimento)
                mensaje = "Alimento actualizado correctamente."
            else:
                self.db.guardar_alimento(alimento)
                mensaje = "Alimento agregado al catálogo."
        except IntegrityError:
            mostrar_snack(
                self.page,
                "Ya existe un alimento con ese nombre.",
                "peligro",
            )
            return

        self._cancelar_edicion(None)
        self._refrescar_lista(recargar_db=True)
        self.page.update()
        mostrar_snack(self.page, mensaje)

    def _cargar_en_formulario(self, alimento: Alimento):
        self.editando_id = alimento.id
        self.campo_nombre.value = alimento.nombre
        self.campo_categoria.value = alimento.categoria or "General"
        self.campo_porcion.value = f"{alimento.porcion_base:g}"
        self.campo_calorias.value = f"{alimento.calorias:g}"
        self.campo_proteinas.value = f"{alimento.proteinas:g}"
        self.campo_carbohidratos.value = (
            f"{alimento.carbohidratos:g}"
        )
        self.campo_grasas.value = f"{alimento.grasas:g}"
        self.boton_guardar.content = "Guardar cambios"
        self.boton_cancelar.visible = True
        self.page.update()

    def _cancelar_edicion(self, e):
        self.editando_id = None
        self.campo_nombre.value = ""
        self.campo_categoria.value = "General"
        self.campo_porcion.value = ""
        self.campo_calorias.value = ""
        self.campo_proteinas.value = ""
        self.campo_carbohidratos.value = ""
        self.campo_grasas.value = ""
        self.boton_guardar.content = "Agregar Alimento"
        self.boton_cancelar.visible = False
        self.page.update()

    def _confirmar_eliminar(self, alimento: Alimento):
        def eliminar():
            self.db.eliminar_alimento(alimento.id)
            self._refrescar_lista(recargar_db=True)
            self.page.update()
            mostrar_snack(self.page, "Alimento eliminado.")

        confirmar(
            self.page,
            "Eliminar alimento",
            f"¿Desea eliminar «{alimento.nombre}» del catálogo? "
            "También se quitará de los planes que lo utilicen.",
            eliminar,
        )

    def _filtrar(self, e):
        self._refrescar_lista(recargar_db=False)
        try:
            self.lista.update()
            self.contador.update()
        except RuntimeError:
            pass

    def _refrescar_lista(self, recargar_db: bool = True):
        if recargar_db or self._cache_alimentos is None:
            self._cache_alimentos = self.db.obtener_alimentos()

        busqueda = (self.campo_busqueda.value or "").strip().lower()
        if busqueda:
            alimentos = [
                a for a in self._cache_alimentos
                if busqueda in a.nombre.lower() or busqueda in (a.categoria or "").lower()
            ]
        else:
            alimentos = self._cache_alimentos
        self.contador.content.value = (
            f"{len(alimentos)} alimento"
            if len(alimentos) == 1
            else f"{len(alimentos)} alimentos"
        )

        if alimentos:
            self.lista.controls = [
                self._fila_alimento(alimento) for alimento in alimentos
            ]
        else:
            self.lista.controls = [
                estado_vacio(
                    "No se encontraron alimentos.",
                    "Agregue un alimento o ajuste la búsqueda.",
                    ft.Icons.FOOD_BANK,
                )
            ]

    def _fila_alimento(self, alimento: Alimento) -> ft.Control:
        return ft.Container(
            bgcolor=COLOR_CARD_BG,
            
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Column(
                        spacing=2,
                        expand=True,
                        controls=[
                            ft.Text(
                                alimento.nombre,
                                size=13,
                                weight=ft.FontWeight.W_600,
                                color=COLOR_TEXT_PRIMARY,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                alimento.categoria or "General",
                                size=10,
                                color=COLOR_TEXT_SECONDARY,
                            ),
                        ],
                    ),
                    self._dato(
                        "Porción", f"{alimento.porcion_base:g} g"
                    ),
                    self._dato("kcal", f"{alimento.calorias:.0f}"),
                    self._dato("Prot.", f"{alimento.proteinas:.1f} g"),
                    self._dato(
                        "Carbs.", f"{alimento.carbohidratos:.1f} g"
                    ),
                    self._dato("Grasas", f"{alimento.grasas:.1f} g"),
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=17,
                                icon_color=COLOR_AZUL_ACERO,
                                tooltip="Editar alimento",
                                on_click=lambda e, a=alimento: self._cargar_en_formulario(
                                    a
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=17,
                                icon_color=COLOR_PELIGRO,
                                tooltip="Eliminar alimento",
                                on_click=lambda e, a=alimento: self._confirmar_eliminar(
                                    a
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _dato(self, etiqueta: str, valor: str) -> ft.Control:
        return ft.Column(
            spacing=1,
            width=58,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            controls=[
                ft.Text(etiqueta, size=9, color=COLOR_TEXT_MUTED),
                ft.Text(
                    valor,
                    size=11,
                    weight=ft.FontWeight.W_500,
                    color=COLOR_TEXT_PRIMARY,
                    text_align=ft.TextAlign.RIGHT,
                ),
            ],
        )

