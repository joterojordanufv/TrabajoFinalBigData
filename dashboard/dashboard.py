import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Premium Real Estate BI Dashboard",
    page_icon="🏠",
    layout="wide"
)


DB_PATH = Path("data/final/real_estate_dw.db")
FINAL_PATH = Path("data/final")
FIGURES_PATH = Path("outputs/figures")
ARCHITECTURE_PATH = Path("outputs/architecture")


@st.cache_data
def load_data():
    fact = pd.read_csv(FINAL_PATH / "fact_properties.csv")
    dim_city = pd.read_csv(FINAL_PATH / "dim_city.csv")
    dim_neighborhood = pd.read_csv(FINAL_PATH / "dim_neighborhood.csv")
    dim_property_type = pd.read_csv(FINAL_PATH / "dim_property_type.csv")
    dim_source = pd.read_csv(FINAL_PATH / "dim_source.csv")
    dim_time = pd.read_csv(FINAL_PATH / "dim_time.csv")

    df = (
        fact
        .merge(dim_city, on="city_id", how="left")
        .merge(dim_neighborhood, on=["neighborhood_id", "city_id"], how="left")
        .merge(dim_property_type, on="property_type_id", how="left")
        .merge(dim_source, on="source_id", how="left")
        .merge(dim_time, on="time_id", how="left")
    )

    return df


def run_sql_query(query):
    conn = sqlite3.connect(DB_PATH)
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result


df = load_data()


st.sidebar.title("🏠 Real Estate BI")

section = st.sidebar.radio(
    "Navegación",
    [
        "Resumen ejecutivo",
        "Análisis visual",
        "Galería EDA",
        "Explorador de datos",
        "Explorador SQL",
        "Modelo dimensional"
    ]
)


cities = st.sidebar.multiselect(
    "Ciudad",
    options=sorted(df["city"].dropna().unique()),
    default=sorted(df["city"].dropna().unique())
)

property_types = st.sidebar.multiselect(
    "Tipo de propiedad",
    options=sorted(df["property_type"].dropna().unique()),
    default=sorted(df["property_type"].dropna().unique())
)

min_price = int(df["price_eur"].min())
max_price = int(df["price_eur"].max())

price_range = st.sidebar.slider(
    "Rango de precio (€)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

bedrooms = st.sidebar.multiselect(
    "Habitaciones",
    options=sorted(df["bedrooms"].dropna().unique()),
    default=sorted(df["bedrooms"].dropna().unique())
)


filtered_df = df[
    (df["city"].isin(cities)) &
    (df["property_type"].isin(property_types)) &
    (df["price_eur"].between(price_range[0], price_range[1])) &
    (df["bedrooms"].isin(bedrooms))
]


if section == "Resumen ejecutivo":
    st.title("🏠 Premium European Real Estate BI Dashboard")

    st.markdown(
        """
        Dashboard interactivo para analizar el mercado inmobiliario premium europeo.
        Integra datos de Madrid, Londres y Ámsterdam con un modelo dimensional en estrella,
        base de datos SQL y visualizaciones de negocio.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Propiedades", f"{len(filtered_df):,}")
    col2.metric("Precio medio", f"€{filtered_df['price_eur'].mean():,.0f}")
    col3.metric("Precio medio/m²", f"€{filtered_df['price_per_m2'].mean():,.0f}")
    col4.metric("Superficie media", f"{filtered_df['area_m2'].mean():.1f} m²")

    st.divider()

    left, right = st.columns(2)

    with left:
        city_avg = (
            filtered_df
            .groupby("city", as_index=False)["price_eur"]
            .mean()
            .sort_values("price_eur", ascending=False)
        )

        fig = px.bar(
            city_avg,
            x="city",
            y="price_eur",
            text_auto=".2s",
            title="Precio medio por ciudad"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.box(
            filtered_df,
            x="city",
            y="price_per_m2",
            points="all",
            title="Distribución del precio por m² por ciudad"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Ranking de barrios premium")

    neighborhood_rank = (
        filtered_df
        .groupby(["city", "neighborhood"], as_index=False)["price_per_m2"]
        .mean()
        .sort_values("price_per_m2", ascending=False)
        .head(15)
    )

    fig = px.bar(
        neighborhood_rank,
        x="price_per_m2",
        y="neighborhood",
        color="city",
        orientation="h",
        title="Top 15 barrios por precio/m²"
    )

    st.plotly_chart(fig, use_container_width=True)


elif section == "Análisis visual":
    st.title("📊 Análisis visual interactivo")

    left, right = st.columns(2)

    with left:
        fig = px.histogram(
            filtered_df,
            x="price_eur",
            color="city",
            nbins=40,
            title="Distribución de precios por ciudad"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.scatter(
            filtered_df,
            x="area_m2",
            y="price_eur",
            color="city",
            size="bedrooms",
            hover_data=[
                "neighborhood",
                "property_type",
                "price_per_m2"
            ],
            title="Relación superficie-precio"
        )

        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        property_count = (
            filtered_df
            .groupby("property_type", as_index=False)
            .size()
        )

        fig = px.pie(
            property_count,
            names="property_type",
            values="size",
            title="Distribución por tipo de propiedad"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        source_count = (
            filtered_df
            .groupby("source", as_index=False)
            .size()
        )

        fig = px.bar(
            source_count,
            x="source",
            y="size",
            text_auto=True,
            title="Registros por fuente"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Correlación entre variables numéricas")

    numeric_cols = [
        "price_eur",
        "area_m2",
        "bedrooms",
        "bathrooms",
        "price_per_m2"
    ]

    corr = filtered_df[numeric_cols].corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        title="Heatmap de correlaciones"
    )

    st.plotly_chart(fig, use_container_width=True)


elif section == "Galería EDA":
    st.title("🖼️ Galería de gráficos EDA")

    st.markdown(
        """
        Esta sección muestra las visualizaciones generadas durante el análisis exploratorio
        y exportadas automáticamente desde los notebooks/scripts del proyecto.
        """
    )

    eda_images = [
        ("Distribución de precios", "01_distribucion_precios.png"),
        ("Precio por m² por ciudad", "02_precio_m2_ciudad.png"),
        ("Relación superficie-precio", "03_superficie_precio.png"),
        ("Frecuencia de barrios", "04_frecuencia_barrios.png"),
        ("Heatmap de correlaciones", "05_heatmap_correlaciones.png"),
        ("Tipos de propiedad", "06_tipos_propiedad.png"),
        ("Precio medio por ciudad", "07_precio_medio_ciudad.png"),
        ("Habitaciones y precio", "08_habitaciones_precio.png"),
        ("Funnel de tracking del pipeline", "09_funnel_tracking_pipeline.png"),
        ("Serie temporal de registros", "10_serie_temporal_registros.png"),
        ("Pairplot de variables continuas", "11_pairplot_variables_continuas.png"),
        ("Heatmap de nulos", "eda01_01_heatmap_nulos.png"),
    ]

    for title, file_name in eda_images:
        image_path = FIGURES_PATH / file_name

        if image_path.exists():
            st.subheader(title)
            st.image(str(image_path), use_container_width=True)
        else:
            st.warning(f"No se encontró la imagen: {file_name}")


elif section == "Explorador de datos":
    st.title("🧾 Explorador de datos enriquecidos")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    st.download_button(
        label="Descargar datos filtrados en CSV",
        data=filtered_df.to_csv(index=False),
        file_name="real_estate_filtered_dataset.csv",
        mime="text/csv"
    )


elif section == "Explorador SQL":
    st.title("🗄️ Explorador SQL")

    st.markdown(
        """
        Ejecuta consultas SQL directamente sobre la base de datos SQLite generada por el pipeline.
        """
    )

    default_query = """
SELECT
    c.city,
    AVG(f.price_eur) AS avg_price,
    AVG(f.price_per_m2) AS avg_price_m2,
    COUNT(*) AS total_properties
FROM fact_properties f
JOIN dim_city c
    ON f.city_id = c.city_id
GROUP BY c.city
ORDER BY avg_price DESC;
"""

    sql_query = st.text_area(
        "Consulta SQL",
        value=default_query,
        height=250
    )

    if st.button("Ejecutar consulta"):
        try:
            result = run_sql_query(sql_query)
            st.success("Consulta ejecutada correctamente.")
            st.dataframe(result, use_container_width=True)
        except Exception as error:
            st.error(f"Error ejecutando la consulta: {error}")


elif section == "Modelo dimensional":
    st.title("⭐ Modelo dimensional en estrella")

    st.markdown(
        """
        El Data Warehouse del proyecto sigue un modelo dimensional en estrella.
        La tabla central es `fact_properties`, que contiene las métricas principales del negocio
        inmobiliario, y está conectada con cinco dimensiones descriptivas.
        """
    )

    st.subheader("Diagrama del modelo dimensional")

    star_schema_image = ARCHITECTURE_PATH / "star_schema_real_estate_dw.png"

    if star_schema_image.exists():
        st.image(str(star_schema_image), use_container_width=True)
    else:
        st.info(
            """
            Todavía no se ha añadido la imagen final del diagrama.
            Cuando esté creada, guárdala en:

            outputs/architecture/star_schema_real_estate_dw.png
            """
        )

        st.graphviz_chart(
            """
            digraph {
                graph [rankdir=LR]
                node [shape=record, style=filled, fontname="Arial"]

                fact [label="{FACT_PROPERTIES|PK fact_id\\lFK city_id\\lFK neighborhood_id\\lFK property_type_id\\lFK source_id\\lFK time_id\\lsource_record_id\\lload_timestamp\\lprice_eur\\larea_m2\\lbedrooms\\lbathrooms\\lprice_per_m2\\l}", fillcolor="#dbeafe"]

                city [label="{DIM_CITY|PK city_id\\lcity\\lcountry\\l}", fillcolor="#dcfce7"]
                neighborhood [label="{DIM_NEIGHBORHOOD|PK neighborhood_id\\lneighborhood\\lcity_id\\l}", fillcolor="#ffedd5"]
                property_type [label="{DIM_PROPERTY_TYPE|PK property_type_id\\lproperty_type\\l}", fillcolor="#f3e8ff"]
                source [label="{DIM_SOURCE|PK source_id\\lsource\\l}", fillcolor="#fee2e2"]
                time [label="{DIM_TIME|PK time_id\\lscraping_date\\lyear\\lquarter\\lmonth\\lday\\lday_name\\lis_weekend\\l}", fillcolor="#fef3c7"]

                city -> fact
                neighborhood -> fact
                property_type -> fact
                source -> fact
                time -> fact
            }
            """
        )

    st.divider()

    st.subheader("Descripción del modelo")

    st.markdown(
        """
        **Tabla de hechos**
        - `fact_properties`

        **Dimensiones**
        - `dim_city`
        - `dim_neighborhood`
        - `dim_property_type`
        - `dim_source`
        - `dim_time`

        **Granularidad**
        - Una fila de `fact_properties` representa una propiedad premium extraída de una fuente inmobiliaria.

        **Medidas principales**
        - `price_eur`
        - `area_m2`
        - `bedrooms`
        - `bathrooms`
        - `price_per_m2`

        **Trazabilidad**
        - `source_record_id`
        - `load_timestamp`
        """
    )

    tables = {
        "fact_properties": "SELECT * FROM fact_properties",
        "dim_city": "SELECT * FROM dim_city",
        "dim_neighborhood": "SELECT * FROM dim_neighborhood",
        "dim_property_type": "SELECT * FROM dim_property_type",
        "dim_source": "SELECT * FROM dim_source",
        "dim_time": "SELECT * FROM dim_time"
    }

    selected_table = st.selectbox(
        "Selecciona una tabla del modelo",
        list(tables.keys())
    )

    table_df = run_sql_query(
        tables[selected_table]
    )

    st.dataframe(
        table_df,
        use_container_width=True
    )
