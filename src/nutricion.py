"""Motor de cálculos nutricionales del MVP.

Fórmulas implementadas:
- Gasto Energético Basal (GEB): Mifflin-St. Jeor.
- Gasto Energético Total (GET): GEB x factor de actividad física.
- Índice de Masa Corporal (IMC) y su clasificación (OMS).
- Distribución personalizada de macronutrientes en gramos y porcentajes.
"""

from dataclasses import dataclass

from src.config import FACTORES_ACTIVIDAD, KCAL_POR_GRAMO


@dataclass
class ResultadoNutricional:
    imc: float
    clasificacion: str
    tono: str
    peso_ideal_min: float
    peso_ideal_max: float
    geb: float
    factor_actividad: float
    get: float
    peso_objetivo: float | None = None
    diferencia_objetivo: float | None = None


@dataclass
class DistribucionMacros:
    porcentaje_proteinas: float
    porcentaje_carbohidratos: float
    porcentaje_grasas: float
    gramos_proteinas: float
    gramos_carbohidratos: float
    gramos_grasas: float
    kcal_proteinas: float
    kcal_carbohidratos: float
    kcal_grasas: float

    @property
    def kcal_totales(self) -> float:
        return self.kcal_proteinas + self.kcal_carbohidratos + self.kcal_grasas


# ── Actividad física ────────────────────────────────────────────

def opciones_actividad() -> list[tuple[str, float, str]]:
    """Devuelve las opciones (etiqueta, factor, descripción) de actividad."""
    return list(FACTORES_ACTIVIDAD)


def etiqueta_actividad(factor: float) -> str:
    """Devuelve el nombre visible del nivel de actividad de un factor dado."""
    for nombre, valor, _ in FACTORES_ACTIVIDAD:
        if abs(valor - factor) < 0.001:
            return nombre
    return "Sedentario"


def normalizar_factor_actividad(factor: float | None) -> float:
    """Convierte un factor inválido (o el 0 de registros antiguos) en 1.2."""
    if factor is None or factor < 1.1 or factor > 2.5:
        return 1.2
    return float(factor)


# ── Antropometría ───────────────────────────────────────────────

def calcular_imc(peso_kg: float, estatura_cm: float) -> float:
    if peso_kg <= 0 or estatura_cm <= 0:
        raise ValueError("El peso y la estatura deben ser mayores que cero.")
    estatura_m = estatura_cm / 100
    return peso_kg / (estatura_m ** 2)


def clasificar_imc(imc: float) -> tuple[str, str]:
    """Clasifica el IMC según la OMS y devuelve (texto, tono).

    El tono es uno de: "normal", "advertencia", "peligro".
    """
    if imc < 18.5:
        return "Bajo peso", "advertencia"
    if imc < 25:
        return "Peso normal", "normal"
    if imc < 30:
        return "Sobrepeso", "advertencia"
    if imc < 35:
        return "Obesidad grado I", "peligro"
    if imc < 40:
        return "Obesidad grado II", "peligro"
    return "Obesidad grado III", "peligro"


def rango_peso_ideal(estatura_cm: float) -> tuple[float, float]:
    """Rango de peso asociado a un IMC saludable (18.5 – 24.9)."""
    estatura_m = estatura_cm / 100
    return 18.5 * estatura_m ** 2, 24.9 * estatura_m ** 2


# ── Energía ─────────────────────────────────────────────────────

def calcular_geb(
    peso_kg: float,
    estatura_cm: float,
    edad: int,
    genero: str,
) -> float:
    """Gasto Energético Basal con la ecuación de Mifflin-St. Jeor.

    Hombres:  (10 x peso) + (6.25 x estatura) - (5 x edad) + 5
    Mujeres:  (10 x peso) + (6.25 x estatura) - (5 x edad) - 161
    """
    if peso_kg <= 0 or estatura_cm <= 0 or edad <= 0:
        raise ValueError("Peso, estatura y edad deben ser mayores que cero.")

    base = (10 * peso_kg) + (6.25 * estatura_cm) - (5 * edad)
    genero_normalizado = (genero or "").strip().lower()

    if genero_normalizado.startswith("m"):
        ajuste = 5
    elif genero_normalizado.startswith("f"):
        ajuste = -161
    else:
        # Valor neutro para "Otro": promedio de ambos ajustes.
        ajuste = -78

    return base + ajuste


def calcular_get(geb: float, factor_actividad: float) -> float:
    return geb * normalizar_factor_actividad(factor_actividad)


def calcular_resultado(
    peso_kg: float,
    estatura_cm: float,
    edad: int,
    genero: str,
    factor_actividad: float,
    peso_objetivo: float | None = None,
) -> ResultadoNutricional:
    """Calcula en una sola llamada todos los indicadores de la ficha clínica."""
    imc = calcular_imc(peso_kg, estatura_cm)
    clasificacion, tono = clasificar_imc(imc)
    imc_min, imc_max = rango_peso_ideal(estatura_cm)
    geb = calcular_geb(peso_kg, estatura_cm, edad, genero)
    factor = normalizar_factor_actividad(factor_actividad)
    get = calcular_get(geb, factor)

    diferencia = None
    if peso_objetivo and peso_objetivo > 0:
        diferencia = peso_objetivo - peso_kg

    return ResultadoNutricional(
        imc=imc,
        clasificacion=clasificacion,
        tono=tono,
        peso_ideal_min=imc_min,
        peso_ideal_max=imc_max,
        geb=geb,
        factor_actividad=factor,
        get=get,
        peso_objetivo=peso_objetivo,
        diferencia_objetivo=diferencia,
    )


# ── Macronutrientes ─────────────────────────────────────────────

def distribuir_macronutrientes(
    calorias_objetivo: float,
    porcentaje_proteinas: float = 20,
    porcentaje_carbohidratos: float = 50,
    porcentaje_grasas: float = 30,
) -> DistribucionMacros:
    """Convierte los porcentajes de macros en gramos diarios."""
    suma = porcentaje_proteinas + porcentaje_carbohidratos + porcentaje_grasas
    if abs(suma - 100) > 0.5:
        raise ValueError(
            "La suma de los porcentajes de macronutrientes debe ser 100% "
            f"(actualmente suma {suma:.0f}%)."
        )
    if calorias_objetivo <= 0:
        raise ValueError("El objetivo calórico debe ser mayor que cero.")

    kcal_proteinas = calorias_objetivo * porcentaje_proteinas / 100
    kcal_carbohidratos = calorias_objetivo * porcentaje_carbohidratos / 100
    kcal_grasas = calorias_objetivo * porcentaje_grasas / 100

    return DistribucionMacros(
        porcentaje_proteinas=porcentaje_proteinas,
        porcentaje_carbohidratos=porcentaje_carbohidratos,
        porcentaje_grasas=porcentaje_grasas,
        gramos_proteinas=kcal_proteinas / KCAL_POR_GRAMO["proteinas"],
        gramos_carbohidratos=kcal_carbohidratos
        / KCAL_POR_GRAMO["carbohidratos"],
        gramos_grasas=kcal_grasas / KCAL_POR_GRAMO["grasas"],
        kcal_proteinas=kcal_proteinas,
        kcal_carbohidratos=kcal_carbohidratos,
        kcal_grasas=kcal_grasas,
    )


def aporte_alimento(
    alimento,
    gramos: float,
) -> dict[str, float]:
    """Calcula el aporte nutricional de una cantidad de alimento.

    ``alimento`` debe exponer ``porcion_base``, ``calorias``, ``proteinas``,
    ``carbohidratos`` y ``grasas``.
    """
    porcion = alimento.porcion_base or 100
    factor = gramos / porcion
    return {
        "calorias": alimento.calorias * factor,
        "proteinas": alimento.proteinas * factor,
        "carbohidratos": alimento.carbohidratos * factor,
        "grasas": alimento.grasas * factor,
    }
