# NutriClínico — MVP de Nutrición Humana

Software clínico de escritorio para la consulta nutricional diaria, desarrollado
con **Python + Flet** y **SQLite + SQLAlchemy**.

## Funcionalidades

### Dashboard
- Resumen de pacientes, planes guardados y alimentos del catálogo.
- IMC promedio y distribución de pacientes por estado nutricional.
- Listado de pacientes recientes con acceso directo a su ficha.
- Accesos rápidos a las secciones principales.

### Gestión de pacientes
- Registro de nombre, edad, género, estatura, peso actual, peso objetivo y
  nivel de actividad física.
- Búsqueda por nombre o género.
- Edición y eliminación de expedientes.
- Ficha clínica individual con evolución antropométrica.

### Motor de cálculos nutricionales
- **GEB** con la ecuación validada de **Mifflin-St. Jeor**.
- **GET** aplicando el factor de actividad física (1.2 a 1.9).
- **IMC** con clasificación de la OMS.
- Rango de peso saludable estimado.
- Distribución personalizada de **proteínas, carbohidratos y grasas** en gramos,
  porcentajes y kilocalorías.

### Catálogo de alimentos
- Catálogo inicial con 41 alimentos de uso habitual (proteínas, lácteos,
  carbohidratos, frutas, verduras y grasas).
- Valores por porción base: calorías, proteínas, carbohidratos y grasas.
- Alta, edición, búsqueda y eliminación de alimentos.

### Generador de planes de alimentación
- Asignación de alimentos y porciones en cinco tiempos de comida:
  Desayuno, Media Mañana, Almuerzo, Merienda y Cena.
- Subtotales por comida y totales diarios en tiempo real.
- Comparación visual contra el GET y las metas de macronutrientes.
- Guardado, edición y carga de planes por paciente.

## Estructura del proyecto

```
BRN/
├── Nutricion.db              # Base de datos SQLite (se crea/migra sola)
├── requirements.txt
├── README.md
└── src/
    ├── main.py               # Punto de entrada
    ├── app.py                # Navegación y composición de vistas
    ├── config.py             # Paleta de colores y parámetros clínicos
    ├── nutricion.py          # Motor de cálculos nutricionales
    ├── database.py           # Fachada SQLAlchemy + migraciones + semilla
    ├── data/
    │   └── alimentos_semilla.py
    ├── models/
    │   ├── paciente.py
    │   ├── medicion.py
    │   ├── alimento.py
    │   └── plan.py
    ├── components/
    │   ├── menu_lateral.py
    │   ├── paciente_card.py
    │   └── ui.py             # Componentes visuales reutilizables
    └── views/
        ├── dashboard_view.py
        ├── pacientes_view.py
        ├── paciente_detalle_view.py
        ├── dieta_view.py
        ├── alimentos_view.py
        └── placeholder_view.py
```

## Instalación y ejecución

Desde la carpeta del proyecto:

```powershell
# 1. Crear el entorno virtual (solo la primera vez)
python -m venv venv

# 2. Instalar dependencias
.\venv\Scripts\pip.exe install -r requirements.txt

# 3. Ejecutar la aplicación
.\venv\Scripts\python.exe src\main.py
```

La aplicación abre una ventana de escritorio. La primera ejecución crea las
tablas faltantes, migra columnas de versiones anteriores y carga el catálogo
inicial de alimentos.

## Modelo de datos

| Tabla | Contenido |
|---|---|
| `PACIENTE` | Datos personales y antropométricos, peso objetivo y factor de actividad |
| `MEDICION` | Historial de peso y estatura por paciente (evolución) |
| `ALIMENTO` | Catálogo con valores nutricionales por porción base |
| `PLANES_NUTRICIONALES` | Plan con GEB, GET y metas de macros |
| `PLAN_ALIMENTO` | Alimentos y gramos asignados a cada tiempo de comida |

## Fórmulas implementadas

**Mifflin-St. Jeor**

```
Hombres:  GEB = (10 × peso) + (6.25 × estatura) − (5 × edad) + 5
Mujeres:  GEB = (10 × peso) + (6.25 × estatura) − (5 × edad) − 161
GET = GEB × factor de actividad física
```

**Índice de Masa Corporal**

```
IMC = peso (kg) / estatura (m)²
```

**Macronutrientes**

```
gramos = (GET × porcentaje / 100) / kcal por gramo
Proteínas y carbohidratos: 4 kcal/g · Grasas: 9 kcal/g
```

## Notas

- Los valores del catálogo son aproximados y sirven como referencia para el MVP.
- La base de datos existente se conserva: la aplicación agrega las columnas y
  tablas nuevas sin borrar los pacientes registrados.
- Esta herramienta es de apoyo clínico y no sustituye el criterio profesional.
