import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="European Luxury Real Estate BI Dashboard",
    page_icon="🏠",
    layout="wide"
)


DB_PATH = Path("data/final/real_estate_dw.db")
FINAL_PATH = Path("data/final")
FIGURES_PATH = Path("outputs/figures")
ARCHITECTURE_PATH = Path("outputs/architecture")
ASSETS_PATH = Path("dashboard/assets")


@st.cache_data
def load_data():
    fact = pd.read_csv(FINAL_PATH / "fact_properties.csv")
    dim_city = pd.read_csv(FINAL_PATH / "dim_city.csv")
    dim_neighborhood = pd.read_csv(FINAL_PATH / "dim_neighborhood.csv")
    dim_property_type = pd.read_csv(FINAL_PATH / "dim_property_type.csv")
    dim_source = pd.read_csv(FINAL_PATH / "dim_source.csv")
    dim_time = pd.read_csv(FINAL_PATH / "dim_time.csv")
    dim_luxury_segment = pd.read_csv(FINAL_PATH / "dim_luxury_segment.csv")

    df = (
        fact
        .merge(dim_city, on="city_id", how="left")
        .merge(dim_neighborhood, on=["neighborhood_id", "city_id"], how="left")
        .merge(dim_property_type, on="property_type_id", how="left")
        .merge(dim_source, on="source_id", how="left")
        .merge(dim_time, on="time_id", how="left")
        .merge(dim_luxury_segment, on="luxury_segment_id", how="left")
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
        "Arquitectura ETL",
        "Modelo dimensional",
        "Explorador de datos",
        "Explorador SQL"
    ]
)


countries = st.sidebar.multiselect(
    "País",
    options=sorted(df["country"].dropna().unique()),
    default=sorted(df["country"].dropna().unique())
)

filtered_country_df = df[df["country"].isin(countries)]

cities = st.sidebar.multiselect(
    "Ciudad",
    options=sorted(filtered_country_df["city"].dropna().unique()),
    default=sorted(filtered_country_df["city"].dropna().unique())
)

property_types = st.sidebar.multiselect(
    "Tipo de propiedad",
    options=sorted(df["property_type"].dropna().unique()),
    default=sorted(df["property_type"].dropna().unique())
)

luxury_labels = st.sidebar.multiselect(
    "Segmento",
    options=sorted(df["luxury_label"].dropna().unique()),
    default=sorted(df["luxury_label"].dropna().unique())
)

min_price = int(df["price_eur"].min())
max_price = int(df["price_eur"].quantile(0.99))

price_range = st.sidebar.slider(
    "Rango de precio (€)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)


filtered_df = df[
    (df["country"].isin(countries)) &
    (df["city"].isin(cities)) &
    (df["property_type"].isin(property_types)) &
    (df["luxury_label"].isin(luxury_labels)) &
    (df["price_eur"].between(price_range[0], price_range[1]))
]


plot_df = (
    filtered_df[
        filtered_df["price_eur"] <= filtered_df["price_eur"].quantile(0.99)
    ]
    if len(filtered_df) > 0
    else filtered_df
)


if section == "Resumen ejecutivo":
    st.title("🏠 European Luxury Real Estate BI Dashboard")

    st.markdown(
        """
        Dashboard interactivo para analizar el mercado inmobiliario europeo utilizando datos reales
        de España, Reino Unido y Países Bajos. El proyecto integra ETL, modelo dimensional,
        base de datos SQL, visualización BI, PySpark, OLAP y segmentación Luxury mediante
        percentil 90 por país.
        """
    )

    if len(filtered_df) == 0:
        st.warning("No hay datos para los filtros seleccionados.")
        st.stop()

    luxury_count = filtered_df[filtered_df["luxury_label"] == "Luxury"].shape[0]
    luxury_pct = luxury_count / len(filtered_df) * 100

    most_expensive_country = (
        filtered_df
        .groupby("country")["price_eur"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Propiedades", f"{len(filtered_df):,}")
    col2.metric("Precio medio", f"€{filtered_df['price_eur'].mean():,.0f}")
    col3.metric("Precio medio/m²", f"€{filtered_df['price_per_m2'].mean():,.0f}")
    col4.metric("Luxury", f"{luxury_pct:.1f}%")
    col5.metric("País más caro", most_expensive_country)

    st.divider()

    left, right = st.columns(2)

    with left:
        country_avg = (
            plot_df
            .groupby("country", as_index=False)["price_eur"]
            .mean()
            .sort_values("price_eur", ascending=False)
        )

        fig = px.bar(
            country_avg,
            x="country",
            y="price_eur",
            text_auto=".2s",
            title="Precio medio por país"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.box(
            plot_df,
            x="country",
            y="price_per_m2",
            color="luxury_label",
            points=False,
            title="Distribución del precio/m² por país y segmento"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 15 ciudades por precio medio")

    city_rank = (
        plot_df
        .groupby(["country", "city"], as_index=False)["price_eur"]
        .mean()
        .sort_values("price_eur", ascending=False)
        .head(15)
    )

    fig = px.bar(
        city_rank,
        x="price_eur",
        y="city",
        color="country",
        orientation="h",
        title="Top 15 ciudades por precio medio"
    )

    st.plotly_chart(fig, use_container_width=True)


elif section == "Análisis visual":
    st.title("📊 Análisis visual interactivo")

    if len(filtered_df) == 0:
        st.warning("No hay datos para los filtros seleccionados.")
        st.stop()

    left, right = st.columns(2)

    with left:
        fig = px.histogram(
            plot_df,
            x="price_eur",
            color="country",
            nbins=60,
            title="Distribución de precios por país"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        fig = px.scatter(
            plot_df,
            x="area_m2",
            y="price_eur",
            color="country",
            symbol="luxury_label",
            hover_data=[
                "city",
                "neighborhood",
                "property_type",
                "price_per_m2",
                "luxury_label"
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
            .sort_values("size", ascending=False)
        )

        fig = px.bar(
            property_count,
            x="property_type",
            y="size",
            text_auto=True,
            title="Distribución por tipo de propiedad"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        luxury_by_country = (
            filtered_df
            .groupby(["country", "luxury_label"], as_index=False)
            .size()
        )

        fig = px.bar(
            luxury_by_country,
            x="country",
            y="size",
            color="luxury_label",
            text_auto=True,
            title="Distribución Luxury / Standard por país"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Correlación entre variables numéricas")

    numeric_cols = [
        "price_eur",
        "area_m2",
        "bedrooms",
        "bathrooms",
        "price_per_m2",
        "luxury_threshold_country"
    ]

    corr = plot_df[numeric_cols].corr()

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
        Esta sección muestra las visualizaciones generadas automáticamente durante el análisis
        exploratorio de datos. Las imágenes proceden de `outputs/figures/`.
        """
    )

    eda_images = [
        ("Distribución de precios", "01_distribucion_precios.png"),
        ("Precio por m² por país y segmento", "02_precio_m2_ciudad.png"),
        ("Relación superficie-precio", "03_superficie_precio.png"),
        ("Top ciudades por precio medio", "04_frecuencia_barrios.png"),
        ("Heatmap de correlaciones", "05_heatmap_correlaciones.png"),
        ("Tipos de propiedad", "06_tipos_propiedad.png"),
        ("Precio medio por país", "07_precio_medio_ciudad.png"),
        ("Habitaciones y precio", "08_habitaciones_precio.png"),
        ("Funnel de tracking del pipeline", "09_funnel_tracking_pipeline.png"),
        ("Serie temporal de registros", "10_serie_temporal_registros.png"),
        ("Pairplot de variables continuas", "11_pairplot_variables_continuas.png"),
        ("Distribución Luxury / Standard", "12_luxury_distribution.png"),
        ("Mapa de valores nulos", "eda01_01_heatmap_nulos.png"),
    ]

    for title, file_name in eda_images:
        image_path = FIGURES_PATH / file_name

        if image_path.exists():
            st.subheader(title)
            st.image(str(image_path), use_container_width=True)
        else:
            st.warning(f"No se encontró la imagen: {file_name}")


elif section == "Arquitectura ETL":
    st.title("🧩 Arquitectura ETL del Proyecto")

    st.markdown(
        """
        Esta sección documenta la arquitectura completa del pipeline ETL del proyecto:
        extracción, análisis de calidad, limpieza, EDA, modelo dimensional, carga SQL,
        PySpark, OLAP, dashboard BI y despliegue con Docker.
        """
    )

    st.subheader("Pipeline ETL interactivo")

    html_path = ASSETS_PATH / "etl_pipeline.html"

    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        components.html(
            html_content,
            height=2300,
            scrolling=True
        )
    else:
        st.warning("No se encontró dashboard/assets/etl_pipeline.html")

    st.divider()

    st.subheader("Imagen del Pipeline ETL")

    pipeline_image = ASSETS_PATH / "etl_pipeline.png"

    if pipeline_image.exists():
        st.image(str(pipeline_image), use_container_width=True)
    else:
        st.info("Guarda la imagen del pipeline como dashboard/assets/etl_pipeline.png")

    st.divider()

    st.subheader("Documento PDF del Pipeline")

    pdf_path = ASSETS_PATH / "etl_pipeline.pdf"

    if pdf_path.exists():
        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        st.download_button(
            label="📥 Descargar Pipeline ETL en PDF",
            data=pdf_bytes,
            file_name="etl_pipeline.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Guarda el PDF como dashboard/assets/etl_pipeline.pdf")


elif section == "Modelo dimensional":
    st.title("⭐ Modelo dimensional en estrella")

    st.markdown(
        """
        El Data Warehouse sigue un modelo dimensional en estrella. La tabla central es
        `fact_properties`, conectada con dimensiones descriptivas de ciudad, barrio/zona,
        tipo de propiedad, fuente, tiempo y segmento luxury.
        """
    )

    st.subheader("Diagrama Star Schema")

    star_schema_asset = ASSETS_PATH / "star_schema.png"
    star_schema_output = ARCHITECTURE_PATH / "star_schema_real_estate_dw.png"

    if star_schema_asset.exists():
        st.image(str(star_schema_asset), use_container_width=True)
    elif star_schema_output.exists():
        st.image(str(star_schema_output), use_container_width=True)
    else:
        st.info(
            """
            No se ha encontrado imagen del modelo dimensional.

            Guarda una de estas rutas:
            - dashboard/assets/star_schema.png
            - outputs/architecture/star_schema_real_estate_dw.png
            """
        )

        st.graphviz_chart(
            """
            digraph {
                graph [rankdir=LR]
                node [shape=record, style=filled, fontname="Arial"]

                fact [label="{FACT_PROPERTIES|PK fact_id\\lFK city_id\\lFK neighborhood_id\\lFK property_type_id\\lFK source_id\\lFK time_id\\lFK luxury_segment_id\\lsource_record_id\\lload_timestamp\\lprice_eur\\larea_m2\\lbedrooms\\lbathrooms\\lprice_per_m2\\lluxury_threshold_country\\l}", fillcolor="#dbeafe"]

                city [label="{DIM_CITY|PK city_id\\lcity\\lcountry\\l}", fillcolor="#dcfce7"]
                neighborhood [label="{DIM_NEIGHBORHOOD|PK neighborhood_id\\lneighborhood\\lcity_id\\l}", fillcolor="#ffedd5"]
                property_type [label="{DIM_PROPERTY_TYPE|PK property_type_id\\lproperty_type\\l}", fillcolor="#f3e8ff"]
                source [label="{DIM_SOURCE|PK source_id\\lsource\\l}", fillcolor="#fee2e2"]
                time [label="{DIM_TIME|PK time_id\\lscraping_date\\lyear\\lquarter\\lmonth\\lday\\lday_name\\lis_weekend\\l}", fillcolor="#fef3c7"]
                luxury [label="{DIM_LUXURY_SEGMENT|PK luxury_segment_id\\lluxury_label\\l}", fillcolor="#e0e7ff"]

                city -> fact
                neighborhood -> fact
                property_type -> fact
                source -> fact
                time -> fact
                luxury -> fact
            }
            """
        )

    st.divider()

    tables = {
        "fact_properties": "SELECT * FROM fact_properties LIMIT 1000",
        "dim_city": "SELECT * FROM dim_city",
        "dim_neighborhood": "SELECT * FROM dim_neighborhood LIMIT 1000",
        "dim_property_type": "SELECT * FROM dim_property_type",
        "dim_source": "SELECT * FROM dim_source",
        "dim_time": "SELECT * FROM dim_time",
        "dim_luxury_segment": "SELECT * FROM dim_luxury_segment"
    }

    selected_table = st.selectbox(
        "Selecciona una tabla del modelo",
        list(tables.keys())
    )

    table_df = run_sql_query(tables[selected_table])

    st.dataframe(
        table_df,
        use_container_width=True
    )


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
        Ejecuta consultas SQL directamente sobre el Data Warehouse SQLite generado por el pipeline.
        """
    )

    default_query = """
SELECT
    c.country,
    l.luxury_label,
    AVG(f.price_eur) AS avg_price,
    AVG(f.price_per_m2) AS avg_price_m2,
    COUNT(*) AS total_properties
FROM fact_properties f
JOIN dim_city c
    ON f.city_id = c.city_id
JOIN dim_luxury_segment l
    ON f.luxury_segment_id = l.luxury_segment_id
GROUP BY c.country, l.luxury_label
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
