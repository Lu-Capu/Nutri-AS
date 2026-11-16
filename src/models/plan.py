from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class Plan(Base):
    """Plan de alimentación con sus objetivos calóricos y de macros."""

    __tablename__ = "PLANES_NUTRICIONALES"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("PACIENTE.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nombre: Mapped[str] = mapped_column(String, default="Plan de alimentación")
    geb: Mapped[float] = mapped_column(Float, nullable=False)
    get_total: Mapped[float] = mapped_column(Float, nullable=False)
    proteinas_meta: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_meta: Mapped[float] = mapped_column(Float, nullable=False)
    grasas_meta: Mapped[float] = mapped_column(Float, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    paciente: Mapped["Paciente"] = relationship(back_populates="planes")  # noqa: F821
    items: Mapped[list["PlanAlimento"]] = relationship(
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="PlanAlimento.id",
    )

    @property
    def calorias_objetivo(self) -> float:
        return self.get_total

    @property
    def proteinas_objetivo(self) -> float:
        return self.proteinas_meta

    @property
    def carbs_objetivo(self) -> float:
        return self.carbs_meta

    @property
    def grasas_objetivo(self) -> float:
        return self.grasas_meta


class PlanAlimento(Base):
    """Porción de un alimento asignada a un tiempo de comida de un plan."""

    __tablename__ = "PLAN_ALIMENTO"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(
        ForeignKey("PLANES_NUTRICIONALES.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tiempo_comida: Mapped[str] = mapped_column(String, nullable=False)
    alimento_id: Mapped[int] = mapped_column(
        ForeignKey("ALIMENTO.id", ondelete="CASCADE"), nullable=False, index=True
    )
    gramos: Mapped[float] = mapped_column(Float, nullable=False)

    plan: Mapped["Plan"] = relationship(back_populates="items")
    alimento: Mapped["Alimento"] = relationship(lazy="joined")  # noqa: F821
