import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("datos_limpios.csv")

df = load_data()

st.title("Análisis de Tiempo de Habla en Reuniones")

col1, col2, col3 = st.columns(3)

with col1:
    nivel = st.radio("Selecciona el nivel de análisis:", 
                 ["Diputados", "Bloques"])

with col2:
    indicador = st.radio("Selecciona el indicador:", 
                     ["Más minutos hablan", "Menos minutos hablan", "Más se ajustan", "Más se exceden"])

with col3:
    filtrar_reunion = st.checkbox("Filtrar por reunión")

    if filtrar_reunion:
        id_reunion = st.selectbox("Selecciona el ID de la reunión:", df["ID_REUNION"].unique())
        df = df[df["ID_REUNION"] == id_reunion]

    mostrar_todos = st.checkbox("Mostrar todos los valores", value=False)


if nivel == "Diputados":
    col_agrupacion = "DIPUTADO"
    num_filas = len(df['DIPUTADO'].unique().tolist()) if mostrar_todos else 10
else:
    col_agrupacion = "BLOQUE"
    num_filas = len(df['BLOQUE'].unique().tolist()) if mostrar_todos else 10


if indicador == "Más minutos hablan":
    datos = df.groupby(col_agrupacion)["DURACION"].sum().sort_values(ascending=False).head(num_filas)
    y_label = "Minutos hablados"
elif indicador == "Menos minutos hablan":
    datos = df.groupby(col_agrupacion)["DURACION"].sum().sort_values().head(num_filas)
    y_label = "Minutos hablados"
elif indicador == "Más se ajustan":
    datos = df.groupby(col_agrupacion)["DIFERENCIA_ESTIMADO"].mean().abs().sort_values().head(num_filas)
    y_label = "Diferencia promedio en minutos (absoluto)"
elif indicador == "Más se exceden":
    datos = df[df["DIFERENCIA_ESTIMADO"] > 0].groupby(col_agrupacion)["DIFERENCIA_ESTIMADO"].sum().sort_values(ascending=False).head(num_filas)
    y_label = "Minutos excedidos"

datos.index = datos.index.astype(str)

datos = datos.iloc[::-1]  

fig = px.bar(
    y=datos.index, 
    x=datos.values,  
    labels={"y": col_agrupacion, "x": y_label}, 
    text=datos.values,
    title=f"{indicador} - {nivel}",
    orientation="h"
)

fig.update_traces(texttemplate='%{text:.2f}', textposition="outside")
fig.update_layout(
    xaxis_title=y_label, 
    yaxis_title=nivel, 
    showlegend=False,
    yaxis=dict(type="category")
)

st.plotly_chart(fig)

if indicador == "Más se ajustan":
    st.text('La métrica esta calculada en base a la diferencia de duración y tiempo estimado, tomado en valor absoluto.')