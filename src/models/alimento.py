from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Alimento(Base):
    """Alimento del catálogo interno.

    Los valores nutricionales corresponden a la ``porcion_base`` (por lo
    general 100 g).
    """

    __tablename__ = "ALIMENTO"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    categoria: Mapped[str] = mapped_column(String, default="General", index=True)
    porcion_base: Mapped[float] = mapped_column(Float, default=100.0)
    calorias: Mapped[float] = mapped_column(Float, nullable=False)
    proteinas: Mapped[float] = mapped_column(Float, nullable=False)
    carbohidratos: Mapped[float] = mapped_column(Float, nullable=False)
    grasas: Mapped[float] = mapped_column(Float, nullable=False)
