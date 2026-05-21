import pandas as pd
from pathlib import Path
from tracker import log_step


PROCESSED_PATH = Path("data/processed")
FINAL_PATH = Path("data/final")

FINAL_PATH.mkdir(parents=True, exist_ok=True)


def load_clean_dataset():
    df = pd.read_csv(PROCESSED_PATH / "properties_clean.csv")

    print("Dataset limpio cargado correctamente.")

    return df


def create_dim_city(df):
    dim_city = (
        df[["city", "country"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_city["city_id"] = dim_city.index + 1

    dim_city = dim_city[
        [
            "city_id",
            "city",
            "country"
        ]
    ]

    dim_city.to_csv(
        FINAL_PATH / "dim_city.csv",
        index=False
    )

    log_step(
        phase="DIMENSION",
        source="DIM_CITY",
        input_rows=len(df),
        output_rows=len(dim_city),
        discarded_rows=0,
        reason="Creación de dimensión ciudad"
    )

    return dim_city


def create_dim_neighborhood(df, dim_city):
    dim_neighborhood = (
        df[["neighborhood", "city"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_neighborhood = dim_neighborhood.merge(
        dim_city[["city_id", "city"]],
        on="city",
        how="left"
    )

    dim_neighborhood["neighborhood_id"] = dim_neighborhood.index + 1

    dim_neighborhood = dim_neighborhood[
        [
            "neighborhood_id",
            "neighborhood",
            "city_id"
        ]
    ]

    dim_neighborhood.to_csv(
        FINAL_PATH / "dim_neighborhood.csv",
        index=False
    )

    log_step(
        phase="DIMENSION",
        source="DIM_NEIGHBORHOOD",
        input_rows=len(df),
        output_rows=len(dim_neighborhood),
        discarded_rows=0,
        reason="Creación de dimensión barrio"
    )

    return dim_neighborhood


def create_dim_property_type(df):
    dim_property_type = (
        df[["property_type"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_property_type["property_type_id"] = dim_property_type.index + 1

    dim_property_type = dim_property_type[
        [
            "property_type_id",
            "property_type"
        ]
    ]

    dim_property_type.to_csv(
        FINAL_PATH / "dim_property_type.csv",
        index=False
    )

    log_step(
        phase="DIMENSION",
        source="DIM_PROPERTY_TYPE",
        input_rows=len(df),
        output_rows=len(dim_property_type),
        discarded_rows=0,
        reason="Creación de dimensión tipo de propiedad"
    )

    return dim_property_type


def create_dim_source(df):
    dim_source = (
        df[["source"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_source["source_id"] = dim_source.index + 1

    dim_source = dim_source[
        [
            "source_id",
            "source"
        ]
    ]

    dim_source.to_csv(
        FINAL_PATH / "dim_source.csv",
        index=False
    )

    log_step(
        phase="DIMENSION",
        source="DIM_SOURCE",
        input_rows=len(df),
        output_rows=len(dim_source),
        discarded_rows=0,
        reason="Creación de dimensión fuente"
    )

    return dim_source


def create_dim_time(df):
    df = df.copy()

    df["scraping_date"] = pd.to_datetime(
        df["scraping_date"],
        errors="coerce"
    )

    dim_time = (
        df[["scraping_date"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    dim_time["time_id"] = dim_time.index + 1

    dim_time["year"] = dim_time["scraping_date"].dt.year
    dim_time["quarter"] = dim_time["scraping_date"].dt.quarter
    dim_time["month"] = dim_time["scraping_date"].dt.month
    dim_time["day"] = dim_time["scraping_date"].dt.day
    dim_time["day_name"] = dim_time["scraping_date"].dt.day_name()
    dim_time["is_weekend"] = dim_time["day_name"].isin(["Saturday", "Sunday"])

    dim_time = dim_time[
        [
            "time_id",
            "scraping_date",
            "year",
            "quarter",
            "month",
            "day",
            "day_name",
            "is_weekend"
        ]
    ]

    dim_time.to_csv(
        FINAL_PATH / "dim_time.csv",
        index=False
    )

    log_step(
        phase="DIMENSION",
        source="DIM_TIME",
        input_rows=len(df),
        output_rows=len(dim_time),
        discarded_rows=0,
        reason="Creación de dimensión temporal"
    )

    return dim_time


def create_fact_properties(
    df,
    dim_city,
    dim_neighborhood,
    dim_property_type,
    dim_source,
    dim_time
):
    fact = df.copy()

    fact["scraping_date"] = pd.to_datetime(
        fact["scraping_date"],
        errors="coerce"
    )

    dim_time = dim_time.copy()

    dim_time["scraping_date"] = pd.to_datetime(
        dim_time["scraping_date"],
        errors="coerce"
    )

    fact = fact.merge(
        dim_city,
        on=["city", "country"],
        how="left"
    )

    fact = fact.merge(
        dim_neighborhood,
        on=["neighborhood", "city_id"],
        how="left"
    )

    fact = fact.merge(
        dim_property_type,
        on="property_type",
        how="left"
    )

    fact = fact.merge(
        dim_source,
        on="source",
        how="left"
    )

    fact = fact.merge(
        dim_time[["time_id", "scraping_date"]],
        on="scraping_date",
        how="left"
    )

    fact["fact_id"] = fact.index + 1

    fact["source_record_id"] = (
        fact["source"].astype(str)
        + "_"
        + fact["property_id"].astype(str)
    )

    fact["load_timestamp"] = pd.Timestamp.now()

    fact = fact[
        [
            "fact_id",
            "city_id",
            "neighborhood_id",
            "property_type_id",
            "source_id",
            "time_id",
            "source_record_id",
            "load_timestamp",
            "price_eur",
            "area_m2",
            "bedrooms",
            "bathrooms",
            "price_per_m2"
        ]
    ]

    fact.to_csv(
        FINAL_PATH / "fact_properties.csv",
        index=False
    )

    log_step(
        phase="FACT",
        source="FACT_PROPERTIES",
        input_rows=len(df),
        output_rows=len(fact),
        discarded_rows=0,
        reason="Creación de tabla de hechos fact_properties con trazabilidad source_record_id y load_timestamp"
    )

    return fact


def main():
    df = load_clean_dataset()

    dim_city = create_dim_city(df)
    dim_neighborhood = create_dim_neighborhood(df, dim_city)
    dim_property_type = create_dim_property_type(df)
    dim_source = create_dim_source(df)
    dim_time = create_dim_time(df)

    create_fact_properties(
        df,
        dim_city,
        dim_neighborhood,
        dim_property_type,
        dim_source,
        dim_time
    )

    print("\nModelo dimensional generado correctamente.")
    print("Archivos exportados en data/final/")


if __name__ == "__main__":
    main()
