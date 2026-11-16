"""Catálogo inicial de alimentos.

Los valores son aproximados por cada 100 g de alimento y provienen de tablas
de composición de alimentos de uso habitual en consulta.
"""

ALIMENTOS_SEMILLA = [
    # ── Proteínas ──────────────────────────────────────────────
    {"nombre": "Pechuga de pollo cocida", "categoria": "Proteínas", "porcion_base": 100, "calorias": 165, "proteinas": 31.0, "carbohidratos": 0.0, "grasas": 3.6},
    {"nombre": "Carne de res magra cocida", "categoria": "Proteínas", "porcion_base": 100, "calorias": 217, "proteinas": 26.0, "carbohidratos": 0.0, "grasas": 11.0},
    {"nombre": "Filete de tilapia cocido", "categoria": "Proteínas", "porcion_base": 100, "calorias": 128, "proteinas": 26.0, "carbohidratos": 0.0, "grasas": 2.7},
    {"nombre": "Atún en agua", "categoria": "Proteínas", "porcion_base": 100, "calorias": 116, "proteinas": 26.0, "carbohidratos": 0.0, "grasas": 1.0},
    {"nombre": "Huevo entero", "categoria": "Proteínas", "porcion_base": 100, "calorias": 155, "proteinas": 13.0, "carbohidratos": 1.1, "grasas": 11.0},
    {"nombre": "Claras de huevo", "categoria": "Proteínas", "porcion_base": 100, "calorias": 52, "proteinas": 11.0, "carbohidratos": 0.7, "grasas": 0.2},
    {"nombre": "Lentejas cocidas", "categoria": "Proteínas", "porcion_base": 100, "calorias": 116, "proteinas": 9.0, "carbohidratos": 20.0, "grasas": 0.4},
    {"nombre": "Frijoles negros cocidos", "categoria": "Proteínas", "porcion_base": 100, "calorias": 132, "proteinas": 8.9, "carbohidratos": 23.7, "grasas": 0.5},
    {"nombre": "Garbanzos cocidos", "categoria": "Proteínas", "porcion_base": 100, "calorias": 164, "proteinas": 8.9, "carbohidratos": 27.4, "grasas": 2.6},
    {"nombre": "Tofu firme", "categoria": "Proteínas", "porcion_base": 100, "calorias": 76, "proteinas": 8.0, "carbohidratos": 1.9, "grasas": 4.8},

    # ── Lácteos ────────────────────────────────────────────────
    {"nombre": "Leche entera", "categoria": "Lácteos", "porcion_base": 100, "calorias": 61, "proteinas": 3.2, "carbohidratos": 4.8, "grasas": 3.3},
    {"nombre": "Yogur griego natural", "categoria": "Lácteos", "porcion_base": 100, "calorias": 59, "proteinas": 10.0, "carbohidratos": 3.6, "grasas": 0.4},
    {"nombre": "Queso fresco", "categoria": "Lácteos", "porcion_base": 100, "calorias": 264, "proteinas": 18.0, "carbohidratos": 2.0, "grasas": 20.0},

    # ── Carbohidratos ──────────────────────────────────────────
    {"nombre": "Arroz blanco cocido", "categoria": "Carbohidratos", "porcion_base": 100, "calorias": 130, "proteinas": 2.7, "carbohidratos": 28.0, "grasas": 0.3},
    {"nombre": "Arroz integral cocido", "categoria": "Carbohidratos", "porcion_base": 100, "calorias": 123, "proteinas": 2.6, "carbohidratos": 25.6, "grasas": 0.9},
    {"nombre": "Avena en hojuelas", "categoria": "Carbohidratos", "porcion_base": 100, "calorias": 389, "proteinas": 16.9, "carbohidratos": 66.3, "grasas": 6.9},
    {"nombre": "Pan integral", "categoria": "Carbohidratos", "porcion_base": 100, "calorias": 247, "proteinas": 13.0, "carbohidratos": 41.0, "grasas": 3.4},
    {"nombre": "Tortilla de maíz", "categoria": "Carbohidratos", "porcion_base": 100, "calorias": 218, "proteinas": 5.7, "carbohidratos": 44.6, "grasas": 2.9},
    {"nombre": "Papa cocida", "categoria": "Carbohidratos", "porcion_base": 100, "calorias": 87, "proteinas": 1.9, "carbohidratos": 20.0, "grasas": 0.1},
    {"nombre": "Camote cocido", "categoria": "Carbohidratos", "porcion_base": 100, "calorias": 90, "proteinas": 2.0, "carbohidratos": 20.7, "grasas": 0.2},
    {"nombre": "Pasta cocida", "categoria": "Carbohidratos", "porcion_base": 100, "calorias": 131, "proteinas": 5.0, "carbohidratos": 25.0, "grasas": 1.1},
    {"nombre": "Quinoa cocida", "categoria": "Carbohidratos", "porcion_base": 100, "calorias": 120, "proteinas": 4.4, "carbohidratos": 21.3, "grasas": 1.9},
    {"nombre": "Arepa de maíz", "categoria": "Carbohidratos", "porcion_base": 100, "calorias": 218, "proteinas": 5.5, "carbohidratos": 45.0, "grasas": 1.7},

    # ── Frutas ─────────────────────────────────────────────────
    {"nombre": "Manzana", "categoria": "Frutas", "porcion_base": 100, "calorias": 52, "proteinas": 0.3, "carbohidratos": 14.0, "grasas": 0.2},
    {"nombre": "Banano", "categoria": "Frutas", "porcion_base": 100, "calorias": 89, "proteinas": 1.1, "carbohidratos": 22.8, "grasas": 0.3},
    {"nombre": "Naranja", "categoria": "Frutas", "porcion_base": 100, "calorias": 47, "proteinas": 0.9, "carbohidratos": 11.8, "grasas": 0.1},
    {"nombre": "Fresas", "categoria": "Frutas", "porcion_base": 100, "calorias": 32, "proteinas": 0.7, "carbohidratos": 7.7, "grasas": 0.3},
    {"nombre": "Aguacate", "categoria": "Frutas", "porcion_base": 100, "calorias": 160, "proteinas": 2.0, "carbohidratos": 8.5, "grasas": 14.7},
    {"nombre": "Mango", "categoria": "Frutas", "porcion_base": 100, "calorias": 60, "proteinas": 0.8, "carbohidratos": 15.0, "grasas": 0.4},
    {"nombre": "Piña", "categoria": "Frutas", "porcion_base": 100, "calorias": 50, "proteinas": 0.5, "carbohidratos": 13.0, "grasas": 0.1},

    # ── Verduras ───────────────────────────────────────────────
    {"nombre": "Brócoli cocido", "categoria": "Verduras", "porcion_base": 100, "calorias": 34, "proteinas": 2.8, "carbohidratos": 6.6, "grasas": 0.4},
    {"nombre": "Espinaca", "categoria": "Verduras", "porcion_base": 100, "calorias": 23, "proteinas": 2.9, "carbohidratos": 3.6, "grasas": 0.4},
    {"nombre": "Tomate", "categoria": "Verduras", "porcion_base": 100, "calorias": 18, "proteinas": 0.9, "carbohidratos": 3.9, "grasas": 0.2},
    {"nombre": "Zanahoria", "categoria": "Verduras", "porcion_base": 100, "calorias": 41, "proteinas": 0.9, "carbohidratos": 9.6, "grasas": 0.2},
    {"nombre": "Lechuga", "categoria": "Verduras", "porcion_base": 100, "calorias": 15, "proteinas": 1.4, "carbohidratos": 2.9, "grasas": 0.2},

    # ── Grasas ─────────────────────────────────────────────────
    {"nombre": "Aceite de oliva", "categoria": "Grasas", "porcion_base": 100, "calorias": 884, "proteinas": 0.0, "carbohidratos": 0.0, "grasas": 100.0},
    {"nombre": "Almendras", "categoria": "Grasas", "porcion_base": 100, "calorias": 579, "proteinas": 21.0, "carbohidratos": 22.0, "grasas": 50.0},
    {"nombre": "Nueces", "categoria": "Grasas", "porcion_base": 100, "calorias": 654, "proteinas": 15.0, "carbohidratos": 14.0, "grasas": 65.0},
    {"nombre": "Maní", "categoria": "Grasas", "porcion_base": 100, "calorias": 567, "proteinas": 26.0, "carbohidratos": 16.0, "grasas": 49.0},
    {"nombre": "Semillas de chía", "categoria": "Grasas", "porcion_base": 100, "calorias": 486, "proteinas": 17.0, "carbohidratos": 42.0, "grasas": 31.0},
    {"nombre": "Mantequilla de maní", "categoria": "Grasas", "porcion_base": 100, "calorias": 588, "proteinas": 25.0, "carbohidratos": 20.0, "grasas": 50.0},
]
