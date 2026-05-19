# Proyecto Final Big Data — Mercado Inmobiliario Premium Europeo

## Tema del proyecto

El proyecto analiza el ascenso de Madrid dentro del mercado inmobiliario premium europeo mediante una comparación de precios de vivienda de lujo entre Madrid, Londres, París y Ámsterdam.

El objetivo principal es construir un pipeline ETL completo que permita extraer datos inmobiliarios de distintas fuentes, limpiarlos, transformarlos, modelarlos en un esquema dimensional, cargarlos en una base de datos SQL y analizarlos posteriormente mediante PySpark en Google Colab.

## Objetivo general

Construir un pipeline de ingeniería de datos reproducible y documentado que transforme datos brutos procedentes de portales inmobiliarios y fuentes oficiales en un modelo dimensional preparado para análisis de negocio.

## Fuentes de datos previstas

- Idealista — Madrid
- Rightmove — Londres
- Funda — Ámsterdam
- Eurostat House Price Index

## Estructura del repositorio

```text
proyecto_bigdata_inmobiliario/
├── data/
│   ├── raw/
│   ├── processed/
│   └── final/
├── src/
│   ├── extract.py
│   ├── clean.py
│   ├── transform.py
│   ├── load.py
│   ├── tracker.py
│   ├── utils.py
│   └── main.py
├── notebooks/
├── logs/
│   └── pipeline_tracking.json
├── sql/
│   └── schema.sql
├── informe/
├── outputs/
│   └── figures/
├── README.md
├── requirements.txt
└── .gitignore
