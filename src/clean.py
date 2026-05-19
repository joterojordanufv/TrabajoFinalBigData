import pandas as pd
import numpy as np
from pathlib import Path
from tracker import log_step


RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")


def load_raw_files():
    idealista = pd.read_csv(RAW_PATH / "idealista_madrid_raw.csv")
    rightmove = pd.read_csv(RAW_PATH / "rightmove_london_raw.csv")

    df = pd.concat([idealista, rightmove], ignore_index=True)

    log_step(
        phase="MERGE_RAW",
        source="Idealista + Rightmove",
        input_rows=len(idealista) + len(rightmove),
        output_rows=len(df),
        discarded_rows=0,
        reason="Unificación inicial de fuentes raw",
        details={
            "files": [
                "idealista_madrid_raw.csv",
                "rightmove_london_raw.csv"
            ]
        }
    )

    return df


def remove_blank_strings(df):
    input_rows = len(df)

    text_columns = df.select_dtypes(include=["object"]).columns
    blank_count = 0

    for col in text_columns:
        blank_count += (df[col].astype(str).str.strip() == "").sum()
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace("", np.nan)

    log_step(
        phase="T03_BLANCOS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Eliminación de espacios y cadenas vacías",
        details={
            "blank_values_corrected": int(blank_count)
        }
    )

    return df


def remove_duplicates(df):
    input_rows = len(df)

    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["source", "property_id"], keep="first")

    discarded = input_rows - len(df)

    log_step(
        phase="T01_DUPLICADOS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=discarded,
        reason="Eliminación de duplicados exactos y duplicados por clave source + property_id",
        details={
            "duplicate_criteria": "source + property_id"
        }
    )

    return df


def handle_missing_values(df):
    input_rows = len(df)

    missing_before = df.isnull().sum().to_dict()

    critical_columns = [
        "property_id",
        "city",
        "country",
        "neighborhood",
        "property_type",
        "price_eur",
        "area_m2",
        "price_per_m2"
    ]

    df = df.dropna(subset=critical_columns)

    if "bedrooms" in df.columns:
        df["bedrooms"] = df["bedrooms"].fillna(df["bedrooms"].median())

    if "bathrooms" in df.columns:
        df["bathrooms"] = df["bathrooms"].fillna(df["bathrooms"].median())

    missing_after = df.isnull().sum().to_dict()

    log_step(
        phase="T02_NULOS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=input_rows - len(df),
        reason="Tratamiento de nulos: eliminación en campos críticos e imputación por mediana en campos secundarios",
        details={
            "missing_before": missing_before,
            "missing_after": missing_after
        }
    )

    return df


def cast_data_types(df):
    input_rows = len(df)

    df["property_id"] = df["property_id"].astype(str)
    df["source"] = df["source"].astype(str)
    df["city"] = df["city"].astype(str)
    df["country"] = df["country"].astype(str)
    df["neighborhood"] = df["neighborhood"].astype(str)
    df["property_type"] = df["property_type"].astype(str)

    df["price_eur"] = pd.to_numeric(df["price_eur"], errors="coerce")
    df["area_m2"] = pd.to_numeric(df["area_m2"], errors="coerce")
    df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce").astype("Int64")
    df["bathrooms"] = pd.to_numeric(df["bathrooms"], errors="coerce").astype("Int64")
    df["price_per_m2"] = pd.to_numeric(df["price_per_m2"], errors="coerce")

    df["scraping_date"] = pd.to_datetime(df["scraping_date"], errors="coerce")

    log_step(
        phase="T04_TIPOS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Conversión de tipos de datos según semántica de negocio",
        details={
            "numeric_columns": ["price_eur", "area_m2", "bedrooms", "bathrooms", "price_per_m2"],
            "datetime_columns": ["scraping_date"]
        }
    )

    return df


def normalize_dates(df):
    input_rows = len(df)

    df["scraping_date"] = pd.to_datetime(df["scraping_date"], errors="coerce", utc=True)
    df["scraping_date"] = df["scraping_date"].dt.strftime("%Y-%m-%d %H:%M:%S")

    log_step(
        phase="T05_FECHAS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Normalización de fechas a formato ISO-8601",
        details={
            "date_format": "YYYY-MM-DD HH:MM:SS UTC"
        }
    )

    return df


def normalize_text(df):
    input_rows = len(df)

    text_columns = [
        "city",
        "country",
        "neighborhood",
        "property_type",
        "source"
    ]

    for col in text_columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    log_step(
        phase="T06_TEXTO",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Normalización de texto: minúsculas y eliminación de espacios",
        details={
            "normalized_columns": text_columns
        }
    )

    return df


def validate_business_ranges(df):
    input_rows = len(df)

    df = df[df["price_eur"] > 0]
    df = df[df["area_m2"] > 0]
    df = df[df["bedrooms"].between(0, 20)]
    df = df[df["bathrooms"].between(0, 20)]
    df = df[df["price_per_m2"] > 0]

    discarded = input_rows - len(df)

    log_step(
        phase="T07_RANGOS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=discarded,
        reason="Validación de rangos de negocio: precios, superficies, habitaciones y baños positivos y coherentes",
        details={
            "criteria": {
                "price_eur": "> 0",
                "area_m2": "> 0",
                "bedrooms": "0-20",
                "bathrooms": "0-20",
                "price_per_m2": "> 0"
            }
        }
    )

    return df


def detect_outliers_iqr(df):
    input_rows = len(df)

    numeric_columns = ["price_eur", "area_m2", "price_per_m2"]
    outlier_summary = {}

    for col in numeric_columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1

        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr

        outliers = df[(df[col] < lower_limit) | (df[col] > upper_limit)]
        outlier_summary[col] = int(len(outliers))

    log_step(
        phase="T08_OUTLIERS",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Detección de outliers mediante IQR. No se eliminan automáticamente por tratarse de mercado premium",
        details={
            "method": "IQR",
            "outliers_detected": outlier_summary
        }
    )

    return df


def pseudonymize_pii(df):
    input_rows = len(df)

    df["property_hash"] = (
        df["source"].astype(str)
        + "_"
        + df["property_id"].astype(str)
    ).apply(lambda x: pd.util.hash_pandas_object(pd.Series([x])).astype(str).iloc[0])

    log_step(
        phase="T09_SEUDONIMIZACION",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Seudonimización de identificadores de propiedad mediante hash",
        details={
            "fields_pseudonymized": ["source", "property_id"],
            "new_field": "property_hash"
        }
    )

    return df


def validate_referential_integrity(df):
    input_rows = len(df)

    orphan_neighborhoods = df["neighborhood"].isnull().sum()
    orphan_cities = df["city"].isnull().sum()

    log_step(
        phase="T10_VALIDACION_REFERENCIAL",
        source="Dataset unificado",
        input_rows=input_rows,
        output_rows=len(df),
        discarded_rows=0,
        reason="Validación referencial básica previa al modelo dimensional",
        details={
            "orphan_neighborhoods": int(orphan_neighborhoods),
            "orphan_cities": int(orphan_cities)
        }
    )

    return df


def save_clean_dataset(df):
    PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

    output_file = PROCESSED_PATH / "properties_clean.csv"
    df.to_csv(output_file, index=False)

    log_step(
        phase="SAVE_PROCESSED",
        source="Dataset limpio",
        input_rows=len(df),
        output_rows=len(df),
        discarded_rows=0,
        reason="Guardado del dataset limpio en data/processed",
        details={
            "output_file": str(output_file)
        }
    )

    print(f"Dataset limpio guardado en: {output_file}")


def main():
    df = load_raw_files()
    df = remove_blank_strings(df)
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = cast_data_types(df)
    df = normalize_dates(df)
    df = normalize_text(df)
    df = validate_business_ranges(df)
    df = detect_outliers_iqr(df)
    df = pseudonymize_pii(df)
    df = validate_referential_integrity(df)
    save_clean_dataset(df)

    print("\nLimpieza ETL completada correctamente.")


if __name__ == "__main__":
    main()
