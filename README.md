# Oferta Formativa: ETL + Visualizaciones

Repositorio que concentra dos piezas complementarias:

1. **Pipeline ETL** en Python que limpia y armoniza el dataset `oferta_formativa_chile_2025.csv` siguiendo principios SOLID y buenas prácticas de composición.
2. **Catálogo de visualizaciones Highcharts** empaquetado en `docs/` y servido mediante la plantilla `docs/index.html` para presentaciones del Observatorio Los Ríos.

## Estructura principal

```
├── config/                           # Configuración YAML centralizada
├── data/
│   ├── raw/                          # Archivos sin procesar (CSV original)
│   └── processed/                    # Artefactos limpios (Parquet, CSVs agregados)
├── docs/
│   ├── index.html                     # Landing page e assets de la plantilla
│   ├── styles.css
│   ├── interactive.js
│   ├── costos_medianos_scatter_highcharts.html
│   ├── carreras_por_ies_highcharts.html
│   ├── niveles_por_vacantes_highcharts.html
│   ├── modalidad_jornada_highcharts.html
│   └── vacantes_por_institucion_highcharts.html
├── notebooks/                        # Exploraciones y QA manual
├── scripts/                          # Wrappers (p.ej. `run_etl.py`)
├── src/oferta_formativa_etl/         # Código modular del pipeline
└── tests/                            # Suite pytest
```

## Requisitos

- Python 3.10+
- Dependencias listadas en `requirements.txt` (equivalentes a `pyproject.toml`)

Instala el entorno virtual y dependencias (se asume `.venv` ya creado):

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Ejecución del pipeline

Opción directa contra la CLI empaquetada:

```bash
.venv/bin/python -m oferta_formativa_etl.cli --config config/settings.yaml
```

Wrapper equivalente (mismo resultado, ayuda a depurar argumentos):

```bash
.venv/bin/python scripts/run_etl.py --config config/settings.yaml
```

### Artefactos generados

- `data/processed/oferta_formativa_clean.parquet`: dataset limpio y normalizado (nombres de IES, UF convertidas, filtros de vigencia, etc.).
- `docs/reports/oferta_formativa_summary.csv`: resumen agregado por región/área con métricas de vacantes, arancel y matrícula.

## Visualizaciones

Cada archivo HTML bajo `docs/` contiene un bundle autónomo de Highcharts v12.4 más los datos serializados. Se construyeron los siguientes tableros principales:

| Archivo | Descripción |
| --- | --- |
| `vacantes_por_institucion_highcharts.html` | Ranking horizontal de vacantes por institución. |
| `carreras_por_ies_highcharts.html` | Selector interactivo de carreras por IES con switch claro/oscuro. |
| `niveles_por_vacantes_highcharts.html` | Vacantes por nivel académico. |
| `modalidad_jornada_highcharts.html` | Cruce modalidad vs jornada en barras apiladas. |
| `costos_medianos_scatter_highcharts.html` | Comparativo de arancel y matrícula medianos. |

Todos ellos se orquestan mediante `docs/index.html`, que referencia cada HTML mediante iframes y añade navegación, estilo institucional y scripts (`docs/interactive.js`).

### Cómo previsualizar la plantilla

1. Ejecuta cualquier servidor estático apuntando a `docs/`:

```bash
cd docs
python -m http.server 8000
```

2. Abre `http://localhost:8000/index.html` en el navegador.

> **Nota:** Los iframes cargan archivos hermanos ubicados en `docs/`. Al desplegar en otro entorno debes mantener la misma estructura relativa.

### Regenerar `carreras_por_ies_highcharts.html`

El archivo se actualiza ejecutando un script corto que filtra la Región de Los Ríos desde `data/processed/oferta_formativa_clean.parquet` y compone el HTML in-line.

```bash
cd /Users/brunosanmartinnavarro/Documents/UACh/oferta-formativa-educacion-superior
.venv/bin/python scripts/run_etl.py --config config/settings.yaml  # asegura parquet actualizado
.venv/bin/python scripts/generate_carreras_por_ies.py              # ver nota inferior
```

> **Nota:** Actualmente el script vive como snippet manual (ver historial en terminal). Si se desea persistir, moverlo a `scripts/generate_carreras_por_ies.py` reutilizando el código ya probado.

## Pruebas

```bash
.venv/bin/python -m pytest
```

Las pruebas cubren transformaciones críticas (normalización de moneda, filtros de vigencia y derivados). Agrega casos nuevos bajo `tests/` cuando se introduzcan columnas o reglas adicionales.

## Personalización

- Configura nombres de columnas, filtros y rutas de salida en `config/settings.yaml`.
- Añade transformadores bajo `src/oferta_formativa_etl/transformers/` y regístralos en `pipeline.py`.
- Para la capa de visualizaciones, modifica estilos en `docs/styles.css` y la lógica de navegación en `docs/interactive.js`.

## Flujo recomendado

1. **Actualizar datos** con el pipeline ETL.
2. **Regenerar visualizaciones** que dependan del parquet (especialmente `carreras_por_ies_highcharts.html`).
3. **Previsualizar la plantilla** y validar que no haya scrolls internos ni desfaces de estilos.
4. **Publicar** subiendo el contenido de `docs/` (o la carpeta completa) al repositorio público o al hosting estático que utilice el Observatorio Los Ríos.
