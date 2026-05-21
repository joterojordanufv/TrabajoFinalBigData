import pandas as pd
from pathlib import Path

from tracker import log_step


RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")

PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


def load_raw_data():
    idealista = pd.read_csv(
        RAW_PATH / "idealista_madrid_raw.csv"
    )

    rightmove = pd.read_csv(
        RAW_PATH / "rightmove_london_raw.csv"
    )

    funda = pd.read_csv(
        RAW_PATH / "funda_amsterdam_raw.csv"
    )

    eurostat = pd.read_csv(
        RAW_PATH / "eurostat_hpi.csv"
    )

    return idealista, rightmove, funda, eurostat


def merge_real_estate_sources(
    idealista,
    rightmove,
    funda
):
    df = pd.concat(
        [
            idealista,
            rightmove,
            funda
        ],
        ignore_index=True
    )

    log_step(
        phase="MERGE_RAW",
        source="Idealista + Rightmove + Funda",
        input_rows=(
            len(idealista)
            + len(rightmove)
            + len(funda)
        ),
        output_rows=len(df),
        discarded_rows=0,
        reason="Unificación de fuentes inmobiliarias"
    )

    print(
        f"[TRACKING] MERGE_RAW - Dataset combinado: "
        f"{len(df)} registros"
    )

    return df


def remove_blank_spaces(df):
    text_columns = df.select_dtypes(
        include=["object"]
    ).columns

    for col in text_columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

    log_step(
        phase="T03_BLANCOS",
        source="Dataset unificado",
        input_rows=len(df),
        output_rows=len(df),
        discarded_rows=0,
        reason="Eliminación de espacios en blanco"
    )

    return df


def remove_duplicates(df):
    before = len(df)

    df = df.drop_duplicates(
        subset=["source", "property_id"],
        keep="first"
    )

    after = len(df)

    log_step(
        phase="T01_DUPLICADOS",
        source="Dataset unificado",
        input_rows=before,
        output_rows=after,
        discarded_rows=before - after,
        reason="Eliminación de duplicados"
    )

    return df


def handle_nulls(df):
    before = len(df)

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
            df[col] = df[col].fillna(
                df[col].median()
            )

    text_columns = [
        "property_type",
        "neighborhood"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna(
                "Unknown"
            )

    after = len(df)

    log_step(
        phase="T02_NULOS",
        source="Dataset unificado",
        input_rows=before,
        output_rows=after,
        discarded_rows=0,
        reason="Tratamiento de valores nulos"
    )

    return df


def validate_types(df):
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
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    log_step(
        phase="T04_TIPOS",
        source="Dataset unificado",
        input_rows=len(df),
        output_rows=len(df),
        discarded_rows=0,
        reason="Validación de tipos de dato"
    )

    return df


def normalize_dates(df):
    df["scraping_date"] = pd.to_datetime(
        df["scraping_date"],
        errors="coerce"
    )

    df["scraping_date"] = (
        df["scraping_date"]
        .dt.strftime("%Y-%m-%d")
    )

    log_step(
        phase="T05_FECHAS",
        source="Dataset unificado",
        input_rows=len(df),
        output_rows=len(df),
        discarded_rows=0,
        reason="Normalización de fechas ISO-8601"
    )

    return df


def normalize_text(df):
    text_columns = [
        "city",
        "country",
        "neighborhood",
        "property_type"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.title()
            )

    log_step(
        phase="T06_TEXTO",
        source="Dataset unificado",
        input_rows=len(df),
        output_rows=len(df),
        discarded_rows=0,
        reason="Normalización textual"
    )

    return df


def validate_ranges(df):
    before = len(df)

    df = df[
        (df["price_eur"] > 0)
        & (df["area_m2"] > 0)
        & (df["bedrooms"] >= 0)
        & (df["bathrooms"] >= 0)
    ]

    after = len(df)

    log_step(
        phase="T07_RANGOS",
        source="Dataset unificado",
        input_rows=before,
        output_rows=after,
        discarded_rows=before - after,
        reason="Validación de rangos"
    )

    return df


def remove_outliers(df):
    before = len(df)

    numeric_columns = [
        "price_eur",
        "area_m2",
        "price_per_m2"
    ]

    for col in numeric_columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        df = df[
            (df[col] >= lower)
            & (df[col] <= upper)
        ]

    after = len(df)

    log_step(
        phase="T08_OUTLIERS",
        source="Dataset unificado",
        input_rows=before,
        output_rows=after,
        discarded_rows=before - after,
        reason="Eliminación de outliers"
    )

    return df


def pseudonymize_data(df):
    df["property_id"] = (
        df["property_id"]
        .astype(str)
        .apply(
            lambda x: f"PROP_{abs(hash(x)) % 1000000}"
        )
    )

    log_step(
        phase="T09_SEUDONIMIZACION",
        source="Dataset unificado",
        input_rows=len(df),
        output_rows=len(df),
        discarded_rows=0,
        reason="Seudonimización de identificadores"
    )

    return df


def validate_referential_integrity(df):
    valid_sources = [
        "Idealista",
        "Rightmove",
        "Funda"
    ]

    before = len(df)

    df = df[
        df["source"].isin(valid_sources)
    ]

    after = len(df)

    log_step(
        phase="T10_VALIDACION_REFERENCIAL",
        source="Dataset unificado",
        input_rows=before,
        output_rows=after,
        discarded_rows=before - after,
        reason="Validación referencial"
    )

    return df


def save_processed_data(
    real_estate_df,
    eurostat_df
):
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
        source="Dataset limpio",
        input_rows=len(real_estate_df),
        output_rows=len(real_estate_df),
        discarded_rows=0,
        reason="Exportación dataset inmobiliario limpio"
    )

    log_step(
        phase="SAVE_PROCESSED",
        source="Eurostat HPI",
        input_rows=len(eurostat_df),
        output_rows=len(eurostat_df),
        discarded_rows=0,
        reason="Exportación Eurostat limpio"
    )

    print(
        "Dataset inmobiliario limpio guardado."
    )

    print(
        "Dataset Eurostat HPI guardado."
    )


def main():
    (
        idealista,
        rightmove,
        funda,
        eurostat
    ) = load_raw_data()

    df = merge_real_estate_sources(
        idealista,
        rightmove,
        funda
    )

    df = remove_blank_spaces(df)

    df = remove_duplicates(df)

    df = handle_nulls(df)

    df = validate_types(df)

    df = normalize_dates(df)

    df = normalize_text(df)

    df = validate_ranges(df)

    df = remove_outliers(df)

    df = pseudonymize_data(df)

    df = validate_referential_integrity(df)

    save_processed_data(
        df,
        eurostat
    )

    print(
        "\nLimpieza ETL completada correctamente."
    )


if __name__ == "__main__":
    main()
