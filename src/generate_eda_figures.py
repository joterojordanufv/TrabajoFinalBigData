import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROJECT_ROOT = Path("/Users/joterojordan/Documents/UFV/proyecto_bigdata_inmobiliario")

DATA_PATH = PROJECT_ROOT / "data/processed/properties_clean.csv"

OUTPUTS = PROJECT_ROOT / "outputs/figures"

OUTPUTS.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

df = pd.read_csv(DATA_PATH)

# 1
plt.figure(figsize=(10, 6))

sns.histplot(
    df["price_eur"],
    kde=True
)

plt.title("Distribución del precio de propiedades premium")

plt.xlabel("Precio (€)")

plt.ylabel("Frecuencia")

plt.savefig(
    OUTPUTS / "01_distribucion_precios.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# 2
plt.figure(figsize=(10, 6))

sns.boxplot(
    x="city",
    y="price_per_m2",
    data=df
)

plt.title("Comparación del precio por m² entre ciudades")

plt.xlabel("Ciudad")

plt.ylabel("Precio por m² (€)")

plt.savefig(
    OUTPUTS / "02_precio_m2_ciudad.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# 3
plt.figure(figsize=(10, 6))

sns.scatterplot(
    x="area_m2",
    y="price_eur",
    hue="city",
    s=120,
    data=df
)

plt.title("Relación entre superficie y precio")

plt.xlabel("Superficie (m²)")

plt.ylabel("Precio (€)")

plt.savefig(
    OUTPUTS / "03_superficie_precio.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# 4
plt.figure(figsize=(12, 6))

df["neighborhood"].value_counts().plot(
    kind="bar"
)

plt.title("Distribución de propiedades por barrio")

plt.xlabel("Barrio")

plt.ylabel("Número de propiedades")

plt.xticks(rotation=45)

plt.savefig(
    OUTPUTS / "04_frecuencia_barrios.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# 5
numeric_df = df[
    [
        "price_eur",
        "area_m2",
        "bedrooms",
        "bathrooms",
        "price_per_m2"
    ]
]

plt.figure(figsize=(10, 6))

sns.heatmap(
    numeric_df.corr(),
    annot=True,
    cmap="coolwarm"
)

plt.title("Correlación entre variables numéricas")

plt.savefig(
    OUTPUTS / "05_heatmap_correlaciones.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# 6
plt.figure(figsize=(10, 6))

df["property_type"].value_counts().plot(
    kind="pie",
    autopct="%1.1f%%"
)

plt.title("Distribución de tipos de propiedad")

plt.ylabel("")

plt.savefig(
    OUTPUTS / "06_tipos_propiedad.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# 7
city_avg = (
    df.groupby("city")["price_eur"]
    .mean()
    .sort_values(ascending=False)
)

plt.figure(figsize=(10, 6))

city_avg.plot(kind="bar")

plt.title("Precio medio por ciudad")

plt.xlabel("Ciudad")

plt.ylabel("Precio medio (€)")

plt.xticks(rotation=0)

plt.savefig(
    OUTPUTS / "07_precio_medio_ciudad.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# 8
plt.figure(figsize=(10, 6))

sns.boxplot(
    x="bedrooms",
    y="price_eur",
    data=df
)

plt.title("Relación entre habitaciones y precio")

plt.xlabel("Número de habitaciones")

plt.ylabel("Precio (€)")

plt.savefig(
    OUTPUTS / "08_habitaciones_precio.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("\nGráficas generadas correctamente.")
