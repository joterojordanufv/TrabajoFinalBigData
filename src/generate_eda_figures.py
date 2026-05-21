from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


PROJECT_ROOT = Path("/Users/joterojordan/Documents/UFV/proyecto_bigdata_inmobiliario")

DATA_PATH = PROJECT_ROOT / "data/processed/properties_clean.csv"
OUTPUTS = PROJECT_ROOT / "outputs/figures"

OUTPUTS.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def load_data():
    df = pd.read_csv(DATA_PATH)

    df["scraping_date"] = pd.to_datetime(
        df["scraping_date"],
        errors="coerce"
    )

    return df


def prepare_plot_data(df):
    price_limit = df["price_eur"].quantile(0.99)
    price_m2_limit = df["price_per_m2"].quantile(0.99)
    area_limit = df["area_m2"].quantile(0.99)

    plot_df = df[
        (df["price_eur"] <= price_limit)
        & (df["price_per_m2"] <= price_m2_limit)
        & (df["area_m2"] <= area_limit)
    ].copy()

    return plot_df


def save_distribution_prices(plot_df):
    plt.figure(figsize=(12, 7))

    sns.histplot(
        data=plot_df,
        x="price_eur",
        hue="country",
        bins=60,
        kde=True,
        element="step"
    )

    plt.title("Distribución de precios por país")
    plt.xlabel("Precio (€)")
    plt.ylabel("Frecuencia")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "01_distribucion_precios.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_price_m2_country(plot_df):
    plt.figure(figsize=(12, 7))

    sns.boxplot(
        data=plot_df,
        x="country",
        y="price_per_m2",
        hue="luxury_label"
    )

    plt.title("Precio por m² por país y segmento")
    plt.xlabel("País")
    plt.ylabel("Precio por m² (€)")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "02_precio_m2_ciudad.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_area_price_scatter(plot_df):
    sample_df = plot_df.sample(
        n=min(5000, len(plot_df)),
        random_state=42
    )

    plt.figure(figsize=(12, 7))

    sns.scatterplot(
        data=sample_df,
        x="area_m2",
        y="price_eur",
        hue="country",
        style="luxury_label",
        alpha=0.6
    )

    plt.title("Relación entre superficie y precio")
    plt.xlabel("Superficie (m²)")
    plt.ylabel("Precio (€)")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "03_superficie_precio.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_top_cities(plot_df):
    top_cities = (
        plot_df
        .groupby(["country", "city"], as_index=False)["price_eur"]
        .mean()
        .sort_values("price_eur", ascending=False)
        .head(20)
    )

    plt.figure(figsize=(12, 8))

    sns.barplot(
        data=top_cities,
        x="price_eur",
        y="city",
        hue="country"
    )

    plt.title("Top 20 ciudades por precio medio")
    plt.xlabel("Precio medio (€)")
    plt.ylabel("Ciudad")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "04_frecuencia_barrios.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_correlation_heatmap(plot_df):
    numeric_df = plot_df[
        [
            "price_eur",
            "area_m2",
            "bedrooms",
            "bathrooms",
            "price_per_m2",
            "luxury_threshold_country"
        ]
    ]

    plt.figure(figsize=(10, 7))

    sns.heatmap(
        numeric_df.corr(),
        annot=True,
        cmap="coolwarm",
        fmt=".2f"
    )

    plt.title("Heatmap de correlaciones")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "05_heatmap_correlaciones.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_property_types(plot_df):
    property_counts = (
        plot_df["property_type"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    property_counts.columns = [
        "property_type",
        "count"
    ]

    plt.figure(figsize=(12, 7))

    sns.barplot(
        data=property_counts,
        x="count",
        y="property_type"
    )

    plt.title("Top 10 tipos de propiedad")
    plt.xlabel("Número de propiedades")
    plt.ylabel("Tipo de propiedad")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "06_tipos_propiedad.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_avg_price_country(plot_df):
    country_avg = (
        plot_df
        .groupby("country", as_index=False)["price_eur"]
        .mean()
        .sort_values("price_eur", ascending=False)
    )

    plt.figure(figsize=(10, 6))

    sns.barplot(
        data=country_avg,
        x="country",
        y="price_eur"
    )

    plt.title("Precio medio por país")
    plt.xlabel("País")
    plt.ylabel("Precio medio (€)")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "07_precio_medio_ciudad.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_bedrooms_price(plot_df):
    bedroom_df = plot_df[
        plot_df["bedrooms"] <= plot_df["bedrooms"].quantile(0.99)
    ]

    plt.figure(figsize=(12, 7))

    sns.boxplot(
        data=bedroom_df,
        x="bedrooms",
        y="price_eur",
        hue="country"
    )

    plt.title("Relación entre habitaciones y precio")
    plt.xlabel("Número de habitaciones")
    plt.ylabel("Precio (€)")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "08_habitaciones_precio.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_luxury_distribution(df):
    luxury_counts = (
        df
        .groupby(["country", "luxury_label"], as_index=False)
        .size()
    )

    plt.figure(figsize=(10, 6))

    sns.barplot(
        data=luxury_counts,
        x="country",
        y="size",
        hue="luxury_label"
    )

    plt.title("Distribución Luxury / Standard por país")
    plt.xlabel("País")
    plt.ylabel("Número de propiedades")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "12_luxury_distribution.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def save_null_heatmap(df):
    sample_df = df.sample(
        n=min(5000, len(df)),
        random_state=42
    )

    plt.figure(figsize=(12, 6))

    sns.heatmap(
        sample_df.isnull(),
        cbar=False,
        yticklabels=False,
        cmap="viridis"
    )

    plt.title("Mapa de valores nulos tras ETL")
    plt.xlabel("Variables")
    plt.ylabel("Registros")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "eda01_01_heatmap_nulos.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def main():
    df = load_data()
    plot_df = prepare_plot_data(df)

    save_distribution_prices(plot_df)
    save_price_m2_country(plot_df)
    save_area_price_scatter(plot_df)
    save_top_cities(plot_df)
    save_correlation_heatmap(plot_df)
    save_property_types(plot_df)
    save_avg_price_country(plot_df)
    save_bedrooms_price(plot_df)
    save_luxury_distribution(df)
    save_null_heatmap(df)

    print("Gráficas EDA actualizadas correctamente.")
    print(f"Archivos guardados en: {OUTPUTS}")


if __name__ == "__main__":
    main()
