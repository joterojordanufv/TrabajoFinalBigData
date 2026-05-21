import sqlite3
import pandas as pd
from pathlib import Path
from tracker import log_step


DB_PATH = Path("data/final/real_estate_dw.db")
FINAL_PATH = Path("data/final")
SCHEMA_PATH = Path("sql/schema.sql")


def create_connection():
    return sqlite3.connect(DB_PATH)


def create_schema(connection):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        schema_sql = file.read()

    connection.executescript(schema_sql)
    connection.commit()

    print("Esquema SQL creado correctamente.")


def load_table(connection, csv_file, table_name):
    df = pd.read_csv(FINAL_PATH / csv_file)

    df.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False
    )

    log_step(
        phase="LOAD_SQL",
        source=table_name,
        input_rows=len(df),
        output_rows=len(df),
        discarded_rows=0,
        reason=f"Carga de {csv_file} en tabla SQL {table_name}"
    )

    print(f"Tabla cargada: {table_name} ({len(df)} registros)")


def verify_counts(connection):
    tables = [
        "dim_city",
        "dim_neighborhood",
        "dim_property_type",
        "dim_source",
        "dim_time",
        "fact_properties"
    ]

    print("\nVerificación de registros cargados:")

    for table in tables:
        query = f"SELECT COUNT(*) AS total FROM {table}"
        result = pd.read_sql_query(query, connection)
        print(f"{table}: {result['total'].iloc[0]} registros")


def main():
    connection = create_connection()

    create_schema(connection)

    load_table(connection, "dim_city.csv", "dim_city")
    load_table(connection, "dim_neighborhood.csv", "dim_neighborhood")
    load_table(connection, "dim_property_type.csv", "dim_property_type")
    load_table(connection, "dim_source.csv", "dim_source")
    load_table(connection, "dim_time.csv", "dim_time")
    load_table(connection, "fact_properties.csv", "fact_properties")

    verify_counts(connection)

    connection.close()

    print("\nCarga SQL completada correctamente.")


if __name__ == "__main__":
    main()
