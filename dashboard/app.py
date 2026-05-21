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


@st.cache_data
def load_dimensional_data():
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


def query_sql(sql):
    conn = sqlite3.connect(DB_PATH)
    result = pd.read_sql_query(sql, conn)
    conn.close()
    return result


df = load_dimensional_data()


st.sidebar.title("🏠 Real Estate BI")

page = st.sidebar.radio(
    "Navegación",
    [
        "Resumen ejecutivo",
        "Análisis visual",
        "Explorador de datos",
        "Explorador SQL",
        "Modelo dimensional"
    ]
)


if page == "Resumen ejecutivo":
    st.title("🏠 Premium Real Estate BI Dashboard")

    st.markdown(
        """
        Panel ejecutivo para analizar el mercado inmobiliario premium europeo.
        El dashboard consume el modelo dimensional generado por el pipeline ETL.
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Propiedades", f"{len(df):,}")
    col2.metric("Precio medio", f"€{df['price_eur'].mean():,.0f}")
    col3.metric("Precio medio/m²", f"€{df['price_per_m2'].mean():,.0f}")
    col4.metric("Superficie media", f"{df['area_m2'].mean():.1f} m²")

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        city_avg = (
            df.groupby("city", as_index=False)["price_eur"]
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

    with c2:
        fig = px.box(
            df,
            x="city",
            y="price_per_m2",
            points="all",
            title="Distribución precio/m² por ciudad"
        )

        st.plotly_chart(fig, use_container_width=True)


elif page == "Análisis visual":
    st.title("📊 Análisis visual interactivo")

    cities = st.sidebar.multiselect(
        "Ciudad",
        sorted(df["city"].unique()),
        default=sorted(df["city"].unique())
    )

    property_types = st.sidebar.multiselect(
        "Tipo de propiedad",
        sorted(df["property_type"].unique()),
        default=sorted(df["property_type"].unique())
    )

    filtered_df = df[
        (df["city"].isin(cities)) &
        (df["property_type"].isin(property_types))
    ]

    st.subheader("Datos filtrados")
    st.write(f"Registros seleccionados: {len(filtered_df)}")

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

    neighborhood_rank = (
        filtered_df
        .groupby(["city", "neighborhood"], as_index=False)["price_per_m2"]
        .mean()
        .sort_values("price_per_m2", ascending=False)
        .head(10)
    )

    fig = px.bar(
        neighborhood_rank,
        x="price_per_m2",
        y="neighborhood",
        color="city",
        orientation="h",
        title="Top 10 barrios por precio/m²"
    )

    st.plotly_chart(fig, use_container_width=True)

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


elif page == "Explorador de datos":
    st.title("🧾 Explorador de datos enriquecidos")

    st.dataframe(
        df,
        use_container_width=True
    )

    st.download_button(
        label="Descargar dataset enriquecido",
        data=df.to_csv(index=False),
        file_name="real_estate_enriched_dataset.csv",
        mime="text/csv"
    )


elif page == "Explorador SQL":
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

    sql = st.text_area(
        "Consulta SQL",
        value=default_query,
        height=250
    )

    if st.button("Ejecutar consulta"):
        try:
            result = query_sql(sql)
            st.success("Consulta ejecutada correctamente.")
            st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"Error ejecutando la consulta: {e}")


elif page == "Modelo dimensional":
    st.title("⭐ Modelo dimensional en estrella")

    st.markdown(
        """
        El modelo dimensional está formado por una tabla de hechos central y cinco dimensiones.

        **Tabla de hechos:**
        - fact_properties

        **Dimensiones:**
        - dim_city
        - dim_neighborhood
        - dim_property_type
        - dim_source
        - dim_time
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
        "Selecciona una tabla",
        list(tables.keys())
    )

    st.dataframe(
        query_sql(tables[selected_table]),
        use_container_width=True
    )
