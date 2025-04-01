import streamlit as st
import pandas as pd


# --- PREPARANDO LA PAGINA ---

st.set_page_config(page_title="Dashboard de Ventas", page_icon="📊")
st.title("Dashboard de Ventas")

# --- RETIRANDO LA MARCHA DE AGUA ---

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# --- CREANDO UNA FUNCION QUE CARGA LOS DATOS Y LOS GUARDA EN EL CACHÉ  ---

@st.cache_data
def load_data(csv):
    return pd.read_csv(csv)

data = load_data("Ventas Regionales Japón.csv")


# --- NUEVAMENTE CALCULANDO LAS GANANCIAS TOTALES POR CIUDAD CON PORCENTAJE DE CAMBIO---
YEAR = 2023
city_revenues = (
    # agrupando los datos por año y ciudad 
    data.groupby(["city", "year"])["sales_amount"]
    # calculando ventas totales por grupo
    .sum()
    # re organizando la tabla para que sea mas agradable visualmente
    .unstack()
    # calculando el porcentaje de cambio entre 2022 y 2023
    .assign(change=lambda x: x.pct_change(axis=1)[YEAR] * 100)
    )


# --- CREANDO CARTAS CON METRICAS ---

CITIES = ["Tokyo", "Yokohama", "Osaka"]

columns = st.columns(3)

for i, col in enumerate(columns):
    with col:
        st.metric(
            label = CITIES[i],
            value = f"${city_revenues.loc[CITIES[i], YEAR]:,.2f}",
            delta = f"{city_revenues.loc[CITIES[i], 'change']:.2f}% vs. Año Pasado",
            )
        
# --- CAMPOS DE SELECCIÓN --

# Seleccion de ciudad y de año
city = st.selectbox("Elige una ciudad:", CITIES)
show_pre_year = st.toggle("Mostrar Año Pasado")
if show_pre_year:
    viz_year = YEAR - 1
else:
    viz_year = YEAR
st.write(f"**Ventas en {viz_year}**")

# --- ESTABLECIENDO PESTAÑAS DE TIPO DE ANALISIS ---

tab_month, tab_cat = st.tabs(["Análisis Mensual", "Análisis Por Categorías"])

# --- ASIGNANDO FILTROS Y VISUALIZACIONES---

with tab_month:
    filtered_data = (
    data.query("city == @city & year == @viz_year")
    .groupby("month", dropna=False, as_index=False)["sales_amount"]
    .sum()
    )
    st.bar_chart(
        data= filtered_data.set_index("month")["sales_amount"],
    )

with tab_cat:
    filtered_data = (
    data.query("city == @city & year == @viz_year")
    .groupby("product_category", dropna=False, as_index=False)["sales_amount"]
    .sum()
    )
    st.bar_chart(
        data= filtered_data.set_index("product_category")["sales_amount"],
    )

