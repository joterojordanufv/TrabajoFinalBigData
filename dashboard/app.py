import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path


st.set_page_config(
    page_title="Premium Real Estate Dashboard",
    page_icon="🏠",
    layout="wide"
)


DATA_PATH = Path("data/final")


@st.cache_data
def load_data():
    fact = pd.read_csv(DATA_PATH / "fact_properties.csv")
    dim_city = pd.read_csv(DATA_PATH / "dim_city.csv")
    dim_neighborhood = pd.read_csv(DATA_PATH / "dim_neighborhood.csv")
    dim_property_type = pd.read_csv(DATA_PATH / "dim_property_type.csv")
    dim_source = pd.read_csv(DATA_PATH / "dim_source.csv")
    dim_time = pd.read_csv(DATA_PATH / "dim_time.csv")

    df = (
        fact
        .merge(dim_city, on="city_id", how="left")
        .merge(dim_neighborhood, on="neighborhood_id", how="left")
        .merge(dim_property_type, on="property_type_id", how="left")
        .merge(dim_source, on="source_id", how="left")
        .merge(dim_time, on="time_id", how="left")
    )

    return df


df = load_data()


st.title("🏠 European Premium Real Estate Dashboard")
st.markdown(
    """
    Dashboard interactivo para analizar el mercado inmobiliario premium europeo.
    Permite comparar precios, barrios, tipos de propiedad y métricas clave del modelo dimensional.
    """
)

st.sidebar.header("Filtros")

cities = st.sidebar.multiselect(
    "Ciudad",
    options=sorted(df["city"].unique()),
    default=sorted(df["city"].unique())
)

property_types = st.sidebar.multiselect(
    "Tipo de propiedad",
    options=sorted(df["property_type"].unique()),
    default=sorted(df["property_type"].unique())
)

filtered_df = df[
    (df["city"].isin(cities)) &
    (df["property_type"].isin(property_types))
]


st.subheader("Indicadores principales")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Propiedades",
    f"{len(filtered_df):,}"
)

col2.metric(
    "Precio medio",
    f"€{filtered_df['price_eur'].mean():,.0f}"
)

col3.metric(
    "Precio medio/m²",
    f"€{filtered_df['price_per_m2'].mean():,.0f}"
)

col4.metric(
    "Superficie media",
    f"{filtered_df['area_m2'].mean():.1f} m²"
)


st.divider()


left, right = st.columns(2)

with left:
    st.subheader("Precio medio por ciudad")

    city_chart = (
        filtered_df
        .groupby("city", as_index=False)["price_eur"]
        .mean()
        .sort_values("price_eur", ascending=False)
    )

    fig = px.bar(
        city_chart,
        x="city",
        y="price_eur",
        text_auto=".2s",
        title="Precio medio por ciudad"
    )

    st.plotly_chart(fig, use_container_width=True)


with right:
    st.subheader("Precio por m² por ciudad")

    fig = px.box(
        filtered_df,
        x="city",
        y="price_per_m2",
        points="all",
        title="Distribución del precio por m²"
    )

    st.plotly_chart(fig, use_container_width=True)


left, right = st.columns(2)

with left:
    st.subheader("Relación superficie-precio")

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
        title="Superficie vs precio"
    )

    st.plotly_chart(fig, use_container_width=True)


with right:
    st.subheader("Ranking de barrios por precio/m²")

    neighborhood_chart = (
        filtered_df
        .groupby(["city", "neighborhood"], as_index=False)["price_per_m2"]
        .mean()
        .sort_values("price_per_m2", ascending=False)
        .head(10)
    )

    fig = px.bar(
        neighborhood_chart,
        x="price_per_m2",
        y="neighborhood",
        color="city",
        orientation="h",
        title="Top 10 barrios por precio/m²"
    )

    st.plotly_chart(fig, use_container_width=True)


st.subheader("Distribución por tipo de propiedad")

property_chart = (
    filtered_df
    .groupby("property_type", as_index=False)
    .size()
)

fig = px.pie(
    property_chart,
    names="property_type",
    values="size",
    title="Distribución de tipos de propiedad"
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("Tabla de datos enriquecida")

st.dataframe(
    filtered_df[
        [
            "fact_id",
            "city",
            "country",
            "neighborhood",
            "property_type",
            "source",
            "price_eur",
            "area_m2",
            "bedrooms",
            "bathrooms",
            "price_per_m2",
            "scraping_date"
        ]
    ],
    use_container_width=True
)


st.download_button(
    label="Descargar datos filtrados en CSV",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_real_estate_data.csv",
    mime="text/csv"
)
