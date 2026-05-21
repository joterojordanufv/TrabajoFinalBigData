import subprocess
import sys


def run_step(description, command):
    print("\n" + "=" * 80)
    print(description)
    print("=" * 80)

    result = subprocess.run(
        command,
        shell=True
    )

    if result.returncode != 0:
        print(f"\nError ejecutando: {description}")
        sys.exit(1)

    print(f"\nCompletado: {description}")


def main():
    run_step(
        "FASE 1 — Extracción de datos",
        "python3 src/extract.py"
    )

    run_step(
        "FASE 2 — Limpieza ETL",
        "python3 src/clean.py"
    )

    run_step(
        "FASE 3 — Modelo dimensional",
        "python3 src/transform.py"
    )

    run_step(
        "FASE 4 — Carga SQL",
        "python3 src/load.py"
    )

    run_step(
        "FASE 5 — Generación de visualizaciones EDA",
        "python3 src/generate_eda_figures.py"
    )

    print("\nPipeline completo ejecutado correctamente.")


if __name__ == "__main__":
    main()
