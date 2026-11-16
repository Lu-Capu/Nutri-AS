import os
import sys
from pathlib import Path

DB_NAME = "Nutricion.db"


def _resolver_ruta_db() -> Path:
    """Devuelve una ruta de BD escribible en escritorio y móvil."""
    # Rutas proporcionadas por Flet en apps empaquetadas/móvil
    for var in ("FLET_APP_STORAGE_DATA", "FLET_APP_DATA", "FLET_APP_CONSOLE"):
        valor = os.environ.get(var)
        if valor:
            try:
                base = Path(valor)
                base.mkdir(parents=True, exist_ok=True)
                return base / DB_NAME
            except Exception:
                pass

    # Fallback escritorio/desarrollo: junto al proyecto (o junto al ejecutable)
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent
    return base / DB_NAME


DB_PATH = _resolver_ruta_db()

# ═══════════════════════════════════════════════════════════════
# Paleta suave y neutra
# ═══════════════════════════════════════════════════════════════

# Fondo general
COLOR_FONDO_APP = "#F5F4F1"

# Tarjetas y contenedores
COLOR_CARD_BG = "#FFFFFF"

# Azul suave — estructura y textos principales
COLOR_AZUL_MARINA = "#3E5C76"

# Acento salvia suave — acciones principales
COLOR_ACENTO = "#6B8F71"
COLOR_ACENTO_HOVER = "#5F8065"
COLOR_ACENTO_LIGHT = "#EEF4EF"

# Azul grisáceo — iconos y texto secundario
COLOR_AZUL_ACERO = "#7D93A8"
COLOR_AZUL_ACERO_LIGHT = "#EEF2F5"

# Textos
COLOR_TEXT_PRIMARY = "#2F3E4C"
COLOR_TEXT_SECONDARY = "#6B7C8C"
COLOR_TEXT_MUTED = "#9AA9B5"
COLOR_TEXT_ON_ACCENT = "#FFFFFF"

# Inputs
COLOR_INPUT_BG = "#F7F7F5"
COLOR_INPUT_BORDER = "#E3E6E8"
COLOR_INPUT_FOCUSED_BORDER = "#9BB7A0"

# Bordes generales
COLOR_BORDER = "#ECEAE6"

# Menú lateral (claro y discreto)
COLOR_MENU_BG = "#F8F7F4"
COLOR_MENU_TEXT = "#6B7C8C"
COLOR_MENU_TEXT_ACTIVO = "#2F3E4C"
COLOR_MENU_ACTIVO_BG = "#EAEFEC"
COLOR_MENU_HOVER = "#EFEDEA"
COLOR_MENU_ICON = "#8A9AAA"
COLOR_MENU_ICON_ACTIVO = COLOR_ACENTO

# ═══════════════════════════════════════════════════════════════
# Colores de estado (suaves)
# ═══════════════════════════════════════════════════════════════

COLOR_EXITO = "#5F8F6B"
COLOR_EXITO_LIGHT = "#EDF4EF"
COLOR_ADVERTENCIA = "#A67C52"
COLOR_ADVERTENCIA_LIGHT = "#F6F1EA"
COLOR_PELIGRO = "#A5645A"
COLOR_PELIGRO_LIGHT = "#F6ECEB"

# ═══════════════════════════════════════════════════════════════
# Parámetros clínicos
# ═══════════════════════════════════════════════════════════════

# (nombre visible, factor de actividad, descripción)
FACTORES_ACTIVIDAD = [
    ("Sedentario", 1.2, "Poco o ningún ejercicio"),
    ("Actividad ligera", 1.375, "Ejercicio 1–3 días por semana"),
    ("Actividad moderada", 1.55, "Ejercicio 3–5 días por semana"),
    ("Actividad intensa", 1.725, "Ejercicio 6–7 días por semana"),
    ("Muy intensa", 1.9, "Ejercicio diario intenso o trabajo físico"),
]

TIEMPOS_COMIDA = [
    "Desayuno",
    "Media Mañana",
    "Almuerzo",
    "Merienda",
    "Cena",
]

# Distribución porcentual por defecto de macronutrientes
DISTRIBUCION_MACROS_DEFAULT = (20, 50, 30)  # proteínas, carbohidratos, grasas

# Energía por gramo de cada macronutriente (kcal)
KCAL_POR_GRAMO = {"proteinas": 4.0, "carbohidratos": 4.0, "grasas": 9.0}
