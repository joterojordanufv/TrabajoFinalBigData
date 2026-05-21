import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


PROJECT_ROOT = Path("/Users/joterojordan/Documents/UFV/proyecto_bigdata_inmobiliario")

RAW_PATH = PROJECT_ROOT / "data/raw"
PROCESSED_PATH = PROJECT_ROOT / "data/processed"
OUTPUTS = PROJECT_ROOT / "outputs/figures"
REPORTS = PROJECT_ROOT / "outputs/reports"
TRACKING_PATH = PROJECT_ROOT / "logs/pipeline_tracking.json"

OUTPUTS.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def calculate_outliers_iqr(df):
    numeric_columns = df.select_dtypes(include=["number"]).columns
    total_outliers = 0

    for col in numeric_columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        total_outliers += len(
            df[
                (df[col] < lower)
                | (df[col] > upper)
            ]
        )

    return int(total_outliers)


def summarize_file(source_name, file_path):
    df = pd.read_csv(file_path)

    total_cells = df.shape[0] * df.shape[1]

    text_columns = df.select_dtypes(include=["object"]).columns

    blank_values = 0

    for col in text_columns:
        blank_values += (
            df[col]
            .astype(str)
            .str.strip()
            .eq("")
            .sum()
        )

    null_values = df.isnull().sum().sum()

    if total_cells > 0:
        null_pct = round(null_values / total_cells * 100, 2)
        blank_pct = round(blank_values / total_cells * 100, 2)
    else:
        null_pct = 0
        blank_pct = 0

    return {
        "fuente": source_name,
        "registros": df.shape[0],
        "variables": df.shape[1],
        "nulos_pct": null_pct,
        "blancos_pct": blank_pct,
        "duplicados": int(df.duplicated().sum()),
        "outliers_detectados": calculate_outliers_iqr(df)
    }


def generate_quality_summary():
    files = {
        "Idealista Madrid": RAW_PATH / "idealista_madrid_raw.csv",
        "Rightmove London": RAW_PATH / "rightmove_london_raw.csv",
        "Funda Amsterdam": RAW_PATH / "funda_amsterdam_raw.csv",
        "Eurostat HPI": RAW_PATH / "eurostat_hpi.csv",
        "Dataset limpio unificado": PROCESSED_PATH / "properties_clean.csv",
        "Eurostat HPI limpio": PROCESSED_PATH / "eurostat_hpi_clean.csv"
    }

    rows = []

    for source_name, file_path in files.items():
        rows.append(
            summarize_file(
                source_name,
                file_path
            )
        )

    quality_df = pd.DataFrame(rows)

    total_row = {
        "fuente": "TOTAL / MEDIA",
        "registros": quality_df["registros"].sum(),
        "variables": round(quality_df["variables"].mean(), 2),
        "nulos_pct": round(quality_df["nulos_pct"].mean(), 2),
        "blancos_pct": round(quality_df["blancos_pct"].mean(), 2),
        "duplicados": quality_df["duplicados"].sum(),
        "outliers_detectados": quality_df["outliers_detectados"].sum()
    }

    quality_df = pd.concat(
        [
            quality_df,
            pd.DataFrame([total_row])
        ],
        ignore_index=True
    )

    quality_df.to_csv(
        REPORTS / "tabla_resumen_calidad.csv",
        index=False
    )

    print("Tabla resumen de calidad generada.")


def generate_tracking_summary_and_funnel():
    with open(TRACKING_PATH, "r", encoding="utf-8") as file:
        tracking_data = json.load(file)

    tracking_df = pd.DataFrame(
        tracking_data["pipeline_runs"]
    )

    tracking_df = tracking_df[
        [
            "timestamp",
            "phase",
            "source",
            "input_rows",
            "output_rows",
            "discarded_rows",
            "reason"
        ]
    ]

    tracking_df.to_csv(
        REPORTS / "tabla_tracking_pipeline.csv",
        index=False
    )

    funnel_df = (
        tracking_df
        .dropna(subset=["output_rows"])
        .groupby("phase", as_index=False)["output_rows"]
        .sum()
        .sort_values("output_rows", ascending=True)
    )

    plt.figure(figsize=(12, 7))

    plt.barh(
        funnel_df["phase"],
        funnel_df["output_rows"]
    )

    plt.title("Funnel de registros por fase del pipeline")
    plt.xlabel("Registros de salida")
    plt.ylabel("Fase del pipeline")
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "09_funnel_tracking_pipeline.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("Tabla de tracking y funnel generados.")


def generate_temporal_series():
    df = pd.read_csv(
        PROCESSED_PATH / "properties_clean.csv"
    )

    df["scraping_date"] = pd.to_datetime(
        df["scraping_date"],
        errors="coerce"
    )

    temporal_df = (
        df
        .groupby("scraping_date", as_index=False)
        .size()
        .rename(columns={"size": "num_properties"})
        .sort_values("scraping_date")
    )

    plt.figure(figsize=(12, 6))

    plt.plot(
        temporal_df["scraping_date"],
        temporal_df["num_properties"],
        marker="o",
        linewidth=1
    )

    plt.title("Serie temporal de propiedades extraídas")
    plt.xlabel("Fecha de extracción")
    plt.ylabel("Número de propiedades")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        OUTPUTS / "10_serie_temporal_registros.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("Serie temporal generada.")


def generate_pairplot():
    df = pd.read_csv(
        PROCESSED_PATH / "properties_clean.csv"
    )

    selected_columns = [
        "price_eur",
        "area_m2",
        "bedrooms",
        "bathrooms",
        "price_per_m2",
        "city"
    ]

    plot = sns.pairplot(
        df[selected_columns],
        hue="city",
        corner=True
    )

    plot.fig.suptitle(
        "Pairplot de variables continuas",
        y=1.02
    )

    plot.savefig(
        OUTPUTS / "11_pairplot_variables_continuas.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close("all")

    print("Pairplot generado.")


def main():
    generate_quality_summary()
    generate_tracking_summary_and_funnel()
    generate_temporal_series()
    generate_pairplot()

    print("\nTodos los outputs obligatorios han sido generados correctamente.")


if __name__ == "__main__":
    main()
