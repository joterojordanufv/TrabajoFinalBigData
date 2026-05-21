import random
from pathlib import Path

import numpy as np
import pandas as pd

from tracker import log_step


RAW_PATH = Path("data/raw")
RAW_PATH.mkdir(parents=True, exist_ok=True)

random.seed(42)
np.random.seed(42)


def random_scraping_date():
    start = pd.Timestamp("2025-01-01")
    end = pd.Timestamp("2026-05-21")
    random_date = start + pd.to_timedelta(
        random.randint(0, (end - start).days),
        unit="D"
    )
    return random_date.strftime("%Y-%m-%d")


def generate_property_data(
    source,
    city,
    country,
    neighborhoods,
    property_types,
    min_price,
    max_price,
    min_area,
    max_area,
    total_records
):
    rows = []

    for i in range(total_records):
        neighborhood = random.choice(neighborhoods)
        property_type = random.choice(property_types)

        bedrooms = random.randint(1, 8)
        bathrooms = random.randint(1, 6)
        floor = random.randint(0, 15)

        area_m2 = round(random.uniform(min_area, max_area), 2)

        base_price_m2 = {
            "Madrid": random.uniform(7000, 18000),
            "London": random.uniform(12000, 28000),
            "Amsterdam": random.uniform(8000, 20000)
        }[city]

        price_per_m2 = round(base_price_m2, 2)
        price_eur = round(area_m2 * price_per_m2, 2)

        price_eur = min(max(price_eur, min_price), max_price)
        price_per_m2 = round(price_eur / area_m2, 2)

        rows.append(
            {
                "property_id": f"{source[:3].upper()}_{city[:3].upper()}_{i + 1}",
                "source": source,
                "country": country,
                "city": city,
                "neighborhood": neighborhood,
                "property_type": property_type,
                "price_eur": price_eur,
                "area_m2": area_m2,
                "price_per_m2": price_per_m2,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "floor": floor,
                "scraping_date": random_scraping_date()
            }
        )

    return pd.DataFrame(rows)


def generate_idealista_data():
    df = generate_property_data(
        source="Idealista",
        city="Madrid",
        country="Spain",
        neighborhoods=[
            "Salamanca",
            "Chamberi",
            "Retiro",
            "Chamartin",
            "Centro"
        ],
        property_types=[
            "Penthouse",
            "Luxury Apartment",
            "Villa",
            "Duplex",
            "Loft"
        ],
        min_price=500000,
        max_price=15000000,
        min_area=40,
        max_area=900,
        total_records=400
    )

    df.to_csv(RAW_PATH / "idealista_madrid_raw.csv", index=False)

    log_step(
        phase="EXTRACT",
        source="Idealista Madrid",
        input_rows=400,
        output_rows=len(df),
        discarded_rows=0,
        reason="Extracción masiva simulada de Idealista Madrid"
    )

    print("Idealista Madrid generado.")

    return df


def generate_rightmove_data():
    df = generate_property_data(
        source="Rightmove",
        city="London",
        country="United Kingdom",
        neighborhoods=[
            "Kensington",
            "Chelsea",
            "Westminster",
            "Camden",
            "Canary Wharf"
        ],
        property_types=[
            "Luxury Flat",
            "Penthouse",
            "Townhouse",
            "Detached House",
            "Duplex"
        ],
        min_price=800000,
        max_price=25000000,
        min_area=45,
        max_area=1200,
        total_records=400
    )

    df.to_csv(RAW_PATH / "rightmove_london_raw.csv", index=False)

    log_step(
        phase="EXTRACT",
        source="Rightmove London",
        input_rows=400,
        output_rows=len(df),
        discarded_rows=0,
        reason="Extracción masiva simulada de Rightmove Londres"
    )

    print("Rightmove London generado.")

    return df


def generate_funda_data():
    df = generate_property_data(
        source="Funda",
        city="Amsterdam",
        country="Netherlands",
        neighborhoods=[
            "Centrum",
            "Jordaan",
            "De Pijp",
            "Oud Zuid",
            "Zuidas"
        ],
        property_types=[
            "Canal House",
            "Luxury Apartment",
            "Penthouse",
            "Villa",
            "Loft"
        ],
        min_price=400000,
        max_price=10000000,
        min_area=35,
        max_area=700,
        total_records=250
    )

    df.to_csv(RAW_PATH / "funda_amsterdam_raw.csv", index=False)

    log_step(
        phase="EXTRACT",
        source="Funda Amsterdam",
        input_rows=250,
        output_rows=len(df),
        discarded_rows=0,
        reason="Extracción masiva simulada de Funda Amsterdam"
    )

    print("Funda Amsterdam generado.")

    return df


def generate_eurostat_hpi():
    countries = [
        "Spain",
        "United Kingdom",
        "Netherlands"
    ]

    rows = []
    years = list(range(2010, 2025))
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    for country in countries:
        base = random.uniform(80, 120)

        for year in years:
            for quarter in quarters:
                growth = random.uniform(0.5, 4)
                base = base * (1 + growth / 100)

                rows.append(
                    {
                        "country": country,
                        "year": year,
                        "quarter": quarter,
                        "house_price_index": round(base, 2)
                    }
                )

    df = pd.DataFrame(rows)

    df.to_csv(RAW_PATH / "eurostat_hpi.csv", index=False)

    log_step(
        phase="EXTRACT",
        source="Eurostat HPI",
        input_rows=len(df),
        output_rows=len(df),
        discarded_rows=0,
        reason="Descarga simulada de Eurostat House Price Index"
    )

    print("Eurostat HPI generado.")

    return df


def main():
    generate_idealista_data()
    generate_rightmove_data()
    generate_funda_data()
    generate_eurostat_hpi()

    print("\nExtracción masiva completada correctamente.")


if __name__ == "__main__":
    main()
