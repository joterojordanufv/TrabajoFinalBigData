import pandas as pd
from datetime import datetime
from pathlib import Path
from tracker import log_step


RAW_PATH = Path("data/raw")


def create_directories():
    RAW_PATH.mkdir(parents=True, exist_ok=True)


def extract_idealista():
    """
    Simulación inicial de extracción de Idealista Madrid.
    Más adelante se sustituirá por scraping real.
    """

    data = {
        "property_id": [1, 2, 3, 4, 5],
        "city": ["Madrid"] * 5,
        "country": ["Spain"] * 5,
        "neighborhood": [
            "Salamanca",
            "Chamberí",
            "Salamanca",
            "Chamartín",
            "Retiro"
        ],
        "property_type": [
            "Apartment",
            "Penthouse",
            "Apartment",
            "Duplex",
            "Apartment"
        ],
        "price_eur": [
            1250000,
            2400000,
            1800000,
            3200000,
            950000
        ],
        "area_m2": [
            120,
            210,
            150,
            300,
            95
        ],
        "bedrooms": [
            3,
            5,
            4,
            6,
            2
        ],
        "bathrooms": [
            2,
            4,
            3,
            5,
            2
        ],
        "listing_url": [
            "idealista_1",
            "idealista_2",
            "idealista_3",
            "idealista_4",
            "idealista_5"
        ],
        "scraping_date": [datetime.now()] * 5
    }

    df = pd.DataFrame(data)

    df["price_per_m2"] = (
        df["price_eur"] / df["area_m2"]
    ).round(2)

    output_file = RAW_PATH / "idealista_madrid_raw.csv"

    df.to_csv(output_file, index=False)

    log_step(
        phase="EXTRACT",
        source="Idealista Madrid",
        input_rows=5,
        output_rows=len(df),
        discarded_rows=0,
        reason="Extracción inicial simulada",
        details={
            "output_file": str(output_file)
        }
    )

    print(f"Archivo guardado en: {output_file}")


def extract_rightmove():
    """
    Simulación inicial de extracción de Rightmove Londres.
    """

    data = {
        "property_id": [101, 102, 103, 104, 105],
        "city": ["London"] * 5,
        "country": ["United Kingdom"] * 5,
        "neighborhood": [
            "Kensington",
            "Chelsea",
            "Mayfair",
            "Notting Hill",
            "Westminster"
        ],
        "property_type": [
            "Apartment",
            "Townhouse",
            "Penthouse",
            "Apartment",
            "Duplex"
        ],
        "price_eur": [
            4200000,
            5100000,
            8900000,
            3400000,
            6200000
        ],
        "area_m2": [
            180,
            240,
            420,
            160,
            310
        ],
        "bedrooms": [
            4,
            5,
            7,
            3,
            5
        ],
        "bathrooms": [
            3,
            5,
            7,
            2,
            5
        ],
        "listing_url": [
            "rightmove_1",
            "rightmove_2",
            "rightmove_3",
            "rightmove_4",
            "rightmove_5"
        ],
        "scraping_date": [datetime.now()] * 5
    }

    df = pd.DataFrame(data)

    df["price_per_m2"] = (
        df["price_eur"] / df["area_m2"]
    ).round(2)

    output_file = RAW_PATH / "rightmove_london_raw.csv"

    df.to_csv(output_file, index=False)

    log_step(
        phase="EXTRACT",
        source="Rightmove London",
        input_rows=5,
        output_rows=len(df),
        discarded_rows=0,
        reason="Extracción inicial simulada",
        details={
            "output_file": str(output_file)
        }
    )

    print(f"Archivo guardado en: {output_file}")


def main():
    create_directories()

    extract_idealista()

    extract_rightmove()

    print("\nExtracción completada correctamente.")


if __name__ == "__main__":
    main()
