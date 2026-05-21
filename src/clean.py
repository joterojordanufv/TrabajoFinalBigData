import pandas as pd
from pathlib import Path

from tracker import log_step


RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")

PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


def load_raw_data():
    spain = pd.read_csv(RAW_PATH / "spain_real_estate_raw.csv")
    uk = pd.read_csv(RAW_PATH / "uk_real_estate_raw.csv")
    netherlands = pd.read_csv(RAW_PATH / "netherlands_real_estate_raw.csv")
    eurostat = pd.read_csv(RAW_PATH / "eurostat_hpi.csv")

    return spain, uk, netherlands, eurostat


def merge_sources(spain, uk, netherlands):
    df = pd.concat(
        [
            spain,
            uk,
            netherlands
        ],
        ignore_index=True
    )

    log_step(
        phase="MERGE_RAW",
        source="Spain + UK + Netherlands",
        input_rows=len(spain) + len(uk) + len(netherlands),
        output_rows=len(df),
        discarded_rows=0,
        reason="Unificación de datasets reales nacionales"
    )

    return df


def clean_blank_values(df):
    input_rows = len(df)

    text_columns = df.select_dtypes(include=["object"]).columns
    blank_count = 0

    for col in text_columns:
        blank_count += df[col].astype(str).str.strip().eq("").sum()
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace("", pd.NA)

    log_step(
        phase="T03_BLANCOS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason=f"Corrección de blancos en columnas textuales: {blank_count} valores"
    )

    return df


def remove_duplicates(df):
    input_rows = len(df)

    df = df.drop_duplicates()
    df = df.drop_duplicates(
        subset=["source", "property_id"],
        keep="first"
    )

    discarded = input_rows - len(df)

    log_step(
        phase="T01_DUPLICADOS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=discarded,
        reason="Eliminación de duplicados exactos y por clave source + property_id"
    )

    return df


def handle_nulls(df):
    input_rows = len(df)

    numeric_columns = [
        "price_eur",
        "area_m2",
        "price_per_m2",
        "bedrooms",
        "bathrooms",
        "floor"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

            if df[col].isnull().sum() > 0:
                median_value = df[col].median()

                if pd.isna(median_value):
                    median_value = 0

                df[col] = df[col].fillna(median_value)

    text_columns = [
        "source",
        "country",
        "city",
        "neighborhood",
        "property_type",
        "listing_url"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna("Not available")

    log_step(
        phase="T02_NULOS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Imputación de nulos mediante mediana en numéricas y valor por defecto en categóricas"
    )

    return df


def validate_types(df):
    input_rows = len(df)

    numeric_columns = [
        "price_eur",
        "area_m2",
        "price_per_m2",
        "bedrooms",
        "bathrooms",
        "floor"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df["scraping_date"] = pd.to_datetime(
        df["scraping_date"],
        errors="coerce"
    )

    log_step(
        phase="T04_TIPOS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Conversión de tipos numéricos y temporales"
    )

    return df


def normalize_dates(df):
    input_rows = len(df)

    df["scraping_date"] = pd.to_datetime(
        df["scraping_date"],
        errors="coerce"
    )

    df["scraping_date"] = df["scraping_date"].fillna(
        pd.Timestamp.today()
    )

    df["scraping_date"] = df["scraping_date"].dt.strftime("%Y-%m-%d")

    log_step(
        phase="T05_FECHAS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Normalización de fechas a formato ISO-8601"
    )

    return df


def normalize_text(df):
    input_rows = len(df)

    text_columns = [
        "source",
        "country",
        "city",
        "neighborhood",
        "property_type"
    ]

    for col in text_columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.title()
        )

    log_step(
        phase="T06_TEXTO",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Normalización textual de variables categóricas"
    )

    return df


def validate_ranges(df):
    input_rows = len(df)

    df = df[
        (df["price_eur"] > 0)
        & (df["area_m2"] > 0)
        & (df["price_per_m2"] > 0)
        & (df["bedrooms"] >= 0)
        & (df["bathrooms"] >= 0)
    ]

    discarded = input_rows - len(df)

    log_step(
        phase="T07_RANGOS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=discarded,
        reason="Validación de rangos mínimos de negocio"
    )

    return df


def detect_outliers(df):
    input_rows = len(df)

    numeric_columns = [
        "price_eur",
        "area_m2",
        "price_per_m2"
    ]

    outlier_counts = {}

    for col in numeric_columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = df[
            (df[col] < lower)
            | (df[col] > upper)
        ]

        outlier_counts[col] = len(outliers)

    log_step(
        phase="T08_OUTLIERS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason=f"Detección de outliers mediante IQR sin eliminación: {outlier_counts}"
    )

    return df


def create_luxury_segment(df):
    input_rows = len(df)

    df["luxury_threshold_country"] = (
        df
        .groupby("country")["price_eur"]
        .transform(lambda x: x.quantile(0.90))
    )

    df["luxury_segment"] = df["price_eur"] >= df["luxury_threshold_country"]

    df["luxury_label"] = df["luxury_segment"].map(
        {
            True: "Luxury",
            False: "Standard"
        }
    )

    log_step(
        phase="LUXURY_SEGMENT",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Creación de segmento luxury mediante percentil 90 de precio por país"
    )

    return df


def pseudonymize_data(df):
    input_rows = len(df)

    df["property_id"] = (
        df["source"].astype(str)
        + "_"
        + df["property_id"].astype(str)
    ).apply(
        lambda x: f"PROP_{abs(hash(x)) % 100000000}"
    )

    log_step(
        phase="T09_SEUDONIMIZACION",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Seudonimización de identificadores de propiedad"
    )

    return df


def validate_referential_integrity(df):
    input_rows = len(df)

    valid_sources = [
        "Spanish Housing Dataset",
        "Uk Land Registry",
        "Dutch Housing Dataset"
    ]

    df = df[df["source"].isin(valid_sources)]

    discarded = input_rows - len(df)

    log_step(
        phase="T10_VALIDACION_REFERENCIAL",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=discarded,
        reason="Validación referencial de fuentes permitidas"
    )

    return df


def save_processed_data(real_estate_df, eurostat_df):
    real_estate_df.to_csv(
        PROCESSED_PATH / "properties_clean.csv",
        index=False
    )

    eurostat_df.to_csv(
        PROCESSED_PATH / "eurostat_hpi_clean.csv",
        index=False
    )

    log_step(
        phase="SAVE_PROCESSED",
        source="Dataset inmobiliario limpio",
        input_rows=len(real_estate_df),
        output_rows=len(real_estate_df),
        discarded_rows=0,
        reason="Exportación de dataset inmobiliario real limpio"
    )

    log_step(
        phase="SAVE_PROCESSED",
        source="Eurostat HPI limpio",
        input_rows=len(eurostat_df),
        output_rows=len(eurostat_df),
        discarded_rows=0,
        reason="Exportación de Eurostat HPI limpio"
    )

    print(f"Dataset inmobiliario limpio guardado: {len(real_estate_df)} registros")
    print(f"Dataset Eurostat HPI limpio guardado: {len(eurostat_df)} registros")


def main():
    spain, uk, netherlands, eurostat = load_raw_data()

    df = merge_sources(
        spain,
        uk,
        netherlands
    )

    df = clean_blank_values(df)
    df = remove_duplicates(df)
    df = handle_nulls(df)
    df = validate_types(df)
    df = normalize_dates(df)
    df = normalize_text(df)
    df = validate_ranges(df)
    df = detect_outliers(df)
    df = create_luxury_segment(df)
    df = pseudonymize_data(df)
    df = validate_referential_integrity(df)

    save_processed_data(
        df,
        eurostat
    )

    print("\nLimpieza ETL completada correctamente.")


if __name__ == "__main__":
    main()
