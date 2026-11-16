from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Paciente(Base):
    __tablename__ = "PACIENTE"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False, index=True)
    edad: Mapped[int] = mapped_column(Integer, nullable=False)
    genero: Mapped[str] = mapped_column(String, nullable=False)
    estatura: Mapped[float] = mapped_column(Float, nullable=False)
    peso_actual: Mapped[float] = mapped_column(Float, nullable=False)
    peso_objetivo: Mapped[float | None] = mapped_column(Float, nullable=True)
    actividad_fisica: Mapped[float] = mapped_column(Float, default=1.2)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    mediciones: Mapped[list["Medicion"]] = relationship(  # noqa: F821
        back_populates="paciente",
        cascade="all, delete-orphan",
        order_by="Medicion.fecha",
    )
    planes: Mapped[list["Plan"]] = relationship(  # noqa: F821
        back_populates="paciente",
        cascade="all, delete-orphan",
    )
