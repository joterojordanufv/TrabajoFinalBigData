# 🏠 European Premium Real Estate Big Data Pipeline

## 📌 Descripción del Proyecto

Este proyecto desarrolla un pipeline completo de ingeniería de datos orientado al análisis del mercado inmobiliario premium europeo, comparando propiedades luxury de Madrid y Londres utilizando técnicas ETL, modelado dimensional, SQL y análisis Big Data con PySpark.

El objetivo principal es estudiar el posicionamiento de Madrid dentro del mercado inmobiliario luxury europeo mediante una arquitectura de datos reproducible y automatizada.

---

# 🚀 Tecnologías Utilizadas

- Python 3
- Pandas
- NumPy
- Matplotlib
- Seaborn
- SQLite
- PySpark
- Google Colab
- Git & GitHub

---

# 📂 Arquitectura del Proyecto

```text
proyecto_bigdata_inmobiliario/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── final/
│
├── notebooks/
│
├── outputs/
│   └── figures/
│
├── sql/
│
├── src/
│
├── logs/
│
└── README.md
```

---

# ⚙️ Pipeline ETL

El pipeline desarrollado incluye:

1. Extracción de datos inmobiliarios
2. Limpieza y transformación ETL
3. Validación de calidad
4. Generación de métricas
5. Modelado dimensional
6. Carga SQL
7. Generación de visualizaciones
8. Análisis OLAP con PySpark

---

# 🧹 Procesos de Calidad Aplicados

- Eliminación de duplicados
- Tratamiento de nulos
- Validación de tipos
- Normalización textual
- Detección de outliers
- Validación referencial
- Seudonimización

---

# ⭐ Modelo Dimensional

## Tabla de hechos

- fact_properties

## Tablas dimensión

- dim_city
- dim_neighborhood
- dim_property_type
- dim_source
- dim_time

El modelo sigue una arquitectura Star Schema preparada para análisis OLAP y explotación analítica multidimensional.

---

# 📊 Visualizaciones Generadas

El proyecto genera automáticamente:

- Distribución de precios
- Comparativa precio/m²
- Scatter plots
- Heatmaps
- Correlaciones
- Rankings de barrios premium
- Comparativas entre ciudades

Las visualizaciones se exportan automáticamente a:

```text
outputs/figures/
```

---

# 🗄️ Base de Datos SQL

El Data Warehouse se implementó utilizando SQLite.

Archivo generado:

```text
data/final/real_estate_dw.db
```

Incluye:
- claves primarias
- claves foráneas
- integridad referencial
- modelo dimensional completo

---

# 🔥 PySpark y Big Data

El proyecto incorpora análisis Big Data mediante PySpark y Google Colab.

Entre las operaciones implementadas destacan:

- joins distribuidos
- agregaciones analíticas
- rollups
- cubes OLAP
- análisis multidimensional

---

# ▶️ Ejecución del Pipeline

Ejecutar pipeline completo:

```bash
python3 src/main.py
```

---

# 📈 Resultados Principales

El análisis realizado muestra que:

- Londres mantiene los precios premium más elevados.
- Madrid presenta un crecimiento importante dentro del segmento luxury.
- Existen barrios madrileños que comienzan a aproximarse a mercados premium internacionales.

---

# 👥 Autores

- Pepe Otero
- Javier Gonzalez
- Pablo Bringas
- Juan Carlos Alva

---

# 📚 Contexto Académico

Proyecto desarrollado para la asignatura de Big Data e Ingeniería de Datos.

Universidad Francisco de Vitoria (UFV)

---

# 📄 Licencia

Proyecto académico con fines educativos.
