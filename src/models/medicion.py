from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Medicion(Base):
    """Registro de evolución antropométrica de un paciente."""

    __tablename__ = "MEDICION"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("PACIENTE.id", ondelete="CASCADE"), nullable=False, index=True
    )
    peso: Mapped[float] = mapped_column(Float, nullable=False)
    estatura: Mapped[float | None] = mapped_column(Float, nullable=True)
    fecha: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    paciente: Mapped["Paciente"] = relationship(  # noqa: F821
        back_populates="mediciones"
    )
