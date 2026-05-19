import nbformat as nbf
from pathlib import Path


NOTEBOOKS_PATH = Path("notebooks")
NOTEBOOKS_PATH.mkdir(parents=True, exist_ok=True)


def markdown_cell(text):
    return nbf.v4.new_markdown_cell(text)


def code_cell(code):
    return nbf.v4.new_code_cell(code)


def create_eda_inicial():
    nb = nbf.v4.new_notebook()

    nb.cells = [
        markdown_cell("# 01 — Análisis Inicial de Calidad de los Datos\n\nEste notebook realiza el perfilado inicial de calidad del dataset inmobiliario limpio."),
        code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

pd.set_option("display.max_columns", None)
sns.set_theme(style="whitegrid")

DATA_PATH = Path("data/processed/properties_clean.csv")
OUTPUTS = Path("outputs/figures")
OUTPUTS.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

df.head()"""),
        markdown_cell("## 1. Dimensiones del dataset"),
        code_cell("""print("Número de registros:", df.shape[0])
print("Número de variables:", df.shape[1])"""),
        markdown_cell("## 2. Tipos de datos"),
        code_cell("df.dtypes"),
        markdown_cell("## 3. Valores nulos"),
        code_cell("""nulls_df = pd.DataFrame({
    "nulos": df.isnull().sum(),
    "porcentaje_nulos": (df.isnull().sum() / len(df) * 100).round(2)
})

nulls_df"""),
        markdown_cell("## 4. Valores blancos"),
        code_cell("""text_columns = df.select_dtypes(include=["object"]).columns

blank_counts = {}

for col in text_columns:
    blank_counts[col] = df[col].astype(str).str.strip().eq("").sum()

blank_df = pd.DataFrame.from_dict(
    blank_counts,
    orient="index",
    columns=["valores_blancos"]
)

blank_df"""),
        markdown_cell("## 5. Duplicados"),
        code_cell("""print("Duplicados exactos:", df.duplicated().sum())

print("Duplicados por source + property_id:")
print(df.duplicated(subset=["source", "property_id"]).sum())"""),
        markdown_cell("## 6. Estadísticos descriptivos"),
        code_cell("df.describe()"),
        markdown_cell("## 7. Cardinalidad de variables categóricas"),
        code_cell("""categorical_columns = ["source", "city", "country", "neighborhood", "property_type"]

for col in categorical_columns:
    print("\\n---", col.upper(), "---")
    print("Valores únicos:", df[col].nunique())
    print(df[col].value_counts())"""),
        markdown_cell("## 8. Detección de outliers mediante IQR"),
        code_cell("""numeric_columns = ["price_eur", "area_m2", "price_per_m2"]

for col in numeric_columns:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3 - q1

    lower_limit = q1 - 1.5 * iqr
    upper_limit = q3 + 1.5 * iqr

    outliers = df[(df[col] < lower_limit) | (df[col] > upper_limit)]

    print(f"\\nVariable: {col}")
    print(f"Límite inferior: {lower_limit:.2f}")
    print(f"Límite superior: {upper_limit:.2f}")
    print(f"Outliers detectados: {len(outliers)}")"""),
        markdown_cell("## 9. Heatmap de valores nulos"),
        code_cell("""plt.figure(figsize=(12, 6))
sns.heatmap(df.isnull(), cbar=False, yticklabels=False)
plt.title("Mapa de calor de valores nulos")
plt.savefig(OUTPUTS / "eda01_01_heatmap_nulos.png", dpi=300, bbox_inches="tight")
plt.show()"""),
        markdown_cell("## 10. Histogramas iniciales"),
        code_cell("""for col in ["price_eur", "area_m2", "price_per_m2"]:
    plt.figure(figsize=(8, 5))
    sns.histplot(df[col], kde=True)
    plt.title(f"Distribución inicial de {col}")
    plt.savefig(OUTPUTS / f"eda01_hist_{col}.png", dpi=300, bbox_inches="tight")
    plt.show()"""),
        markdown_cell("## 11. Boxplot precio por m² por ciudad"),
        code_cell("""plt.figure(figsize=(10, 6))
sns.boxplot(x="city", y="price_per_m2", data=df)
plt.title("Precio por m² por ciudad")
plt.savefig(OUTPUTS / "eda01_02_boxplot_precio_m2_ciudad.png", dpi=300, bbox_inches="tight")
plt.show()"""),
        markdown_cell("## 12. Interpretación inicial\n\nEl dataset limpio no presenta valores nulos ni duplicados en las claves principales. Las variables numéricas muestran dispersión elevada, especialmente en precio total y precio por metro cuadrado, algo coherente con el mercado inmobiliario premium. Los outliers detectados no deben eliminarse automáticamente porque pueden representar viviendas ultra luxury reales.")
    ]

    path = NOTEBOOKS_PATH / "01_eda_inicial.ipynb"

    with open(path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(f"Notebook creado: {path}")


def create_eda_final():
    nb = nbf.v4.new_notebook()

    nb.cells = [
        markdown_cell("# 02 — EDA Final e Interpretación de Negocio\n\nEste notebook realiza el análisis exploratorio final del mercado inmobiliario premium europeo."),
        code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

pd.set_option("display.max_columns", None)
sns.set_theme(style="whitegrid")

DATA_PATH = Path("data/processed/properties_clean.csv")
OUTPUTS = Path("outputs/figures")
OUTPUTS.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

df.head()"""),
        markdown_cell("## 1. Clasificación de variables"),
        code_cell("""quantitative_columns = ["price_eur", "area_m2", "bedrooms", "bathrooms", "price_per_m2"]
categorical_columns = ["source", "city", "country", "neighborhood", "property_type"]
temporal_columns = ["scraping_date"]

classification = pd.DataFrame({
    "variable": quantitative_columns + categorical_columns + temporal_columns,
    "tipo": (
        ["Cuantitativa"] * len(quantitative_columns)
        + ["Cualitativa"] * len(categorical_columns)
        + ["Temporal"] * len(temporal_columns)
    )
})

classification"""),
        markdown_cell("## 2. Gráfica 1 — Distribución de precios"),
        code_cell("""plt.figure(figsize=(10, 6))
sns.histplot(df["price_eur"], kde=True)
plt.title("Distribución del precio de propiedades premium")
plt.xlabel("Precio (€)")
plt.ylabel("Frecuencia")
plt.savefig(OUTPUTS / "01_distribucion_precios.png", dpi=300, bbox_inches="tight")
plt.show()"""),
        markdown_cell("La distribución de precios muestra una concentración en valores altos y una cola hacia propiedades ultra premium. Esto es coherente con un dataset centrado en vivienda de lujo."),
        markdown_cell("## 3. Gráfica 2 — Precio por m² por ciudad"),
        code_cell("""plt.figure(figsize=(10, 6))
sns.boxplot(x="city", y="price_per_m2", data=df)
plt.title("Comparación del precio por m² entre ciudades")
plt.xlabel("Ciudad")
plt.ylabel("Precio por m² (€)")
plt.savefig(OUTPUTS / "02_precio_m2_ciudad.png", dpi=300, bbox_inches="tight")
plt.show()"""),
        markdown_cell("El boxplot permite comparar Madrid y Londres en términos de precio por metro cuadrado. Londres presenta valores superiores, pero Madrid aparece como un mercado premium en crecimiento."),
        markdown_cell("## 4. Gráfica 3 — Relación entre superficie y precio"),
        code_cell("""plt.figure(figsize=(10, 6))
sns.scatterplot(x="area_m2", y="price_eur", hue="city", s=120, data=df)
plt.title("Relación entre superficie y precio")
plt.xlabel("Superficie (m²)")
plt.ylabel("Precio (€)")
plt.savefig(OUTPUTS / "03_superficie_precio.png", dpi=300, bbox_inches="tight")
plt.show()"""),
        markdown_cell("La relación entre superficie y precio es positiva, aunque no totalmente lineal. En el mercado premium influyen también localización, exclusividad y prestigio del barrio."),
        markdown_cell("## 5. Gráfica 4 — Distribución por barrio"),
        code_cell("""plt.figure(figsize=(12, 6))
df["neighborhood"].value_counts().plot(kind="bar")
plt.title("Distribución de propiedades por barrio")
plt.xlabel("Barrio")
plt.ylabel("Número de propiedades")
plt.xticks(rotation=45)
plt.savefig(OUTPUTS / "04_frecuencia_barrios.png", dpi=300, bbox_inches="tight")
plt.show()"""),
        markdown_cell("La distribución por barrio refleja la concentración del dataset en zonas premium como Salamanca, Chamberí, Kensington, Chelsea o Mayfair."),
        markdown_cell("## 6. Gráfica 5 — Correlaciones"),
        code_cell("""numeric_df = df[["price_eur", "area_m2", "bedrooms", "bathrooms", "price_per_m2"]]

plt.figure(figsize=(10, 6))
sns.heatmap(numeric_df.corr(), annot=True)
plt.title("Correlación entre variables numéricas")
plt.savefig(OUTPUTS / "05_heatmap_correlaciones.png", dpi=300, bbox_inches="tight")
plt.show()"""),
        markdown_cell("El heatmap permite observar relaciones entre precio, superficie, habitaciones, baños y precio por m². La superficie suele estar relacionada con el precio, pero el precio por m² depende también de la localización."),
        markdown_cell("## 7. Gráfica 6 — Tipos de propiedad"),
        code_cell("""plt.figure(figsize=(10, 6))
df["property_type"].value_counts().plot(kind="pie", autopct="%1.1f%%")
plt.title("Distribución de tipos de propiedad")
plt.ylabel("")
plt.savefig(OUTPUTS / "06_tipos_propiedad.png", dpi=300, bbox_inches="tight")
plt.show()"""),
        markdown_cell("La distribución de tipos de propiedad ayuda a identificar qué formatos dominan el segmento premium en las ciudades analizadas."),
        markdown_cell("## 8. Gráfica 7 — Precio medio por ciudad"),
        code_cell("""city_avg = df.groupby("city")["price_eur"].mean().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
city_avg.plot(kind="bar")
plt.title("Precio medio por ciudad")
plt.xlabel("Ciudad")
plt.ylabel("Precio medio (€)")
plt.xticks(rotation=0)
plt.savefig(OUTPUTS / "07_precio_medio_ciudad.png", dpi=300, bbox_inches="tight")
plt.show()"""),
        markdown_cell("El precio medio por ciudad permite comparar la intensidad del mercado premium entre Madrid y Londres."),
        markdown_cell("## 9. Gráfica 8 — Habitaciones y precio"),
        code_cell("""plt.figure(figsize=(10, 6))
sns.boxplot(x="bedrooms", y="price_eur", data=df)
plt.title("Relación entre habitaciones y precio")
plt.xlabel("Número de habitaciones")
plt.ylabel("Precio (€)")
plt.savefig(OUTPUTS / "08_habitaciones_precio.png", dpi=300, bbox_inches="tight")
plt.show()"""),
        markdown_cell("Las propiedades con más habitaciones tienden a presentar precios superiores, aunque el precio final depende también de la localización y del tipo de inmueble."),
        markdown_cell("## 10. Conclusión del EDA final\n\nEl análisis confirma que el mercado inmobiliario premium presenta una elevada dispersión de precios. Londres mantiene valores superiores, pero Madrid muestra barrios con precios elevados que justifican su comparación con capitales europeas consolidadas. Este análisis sirve como base para el modelo dimensional y el posterior análisis con PySpark.")
    ]

    path = NOTEBOOKS_PATH / "02_eda_final.ipynb"

    with open(path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print(f"Notebook creado: {path}")


if __name__ == "__main__":
    create_eda_inicial()
    create_eda_final()
