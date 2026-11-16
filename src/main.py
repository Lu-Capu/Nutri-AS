import sys
from pathlib import Path

import flet as ft

# Permite ejecutar este archivo directamente (py src/main.py) desde la raíz del proyecto
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.app import App
from src.database import Database


def main(page: ft.Page):
    db = Database()
    db.inicializar_bd()
    App(page, db).iniciar()


if __name__ == "__main__":
    ft.run(main=main)
