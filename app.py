import streamlit as st
import pandas as pd
import numpy as np
from dataclasses import dataclass
from plotly import express as px

@dataclass
class ControlFlags:
    show_scatter: bool
    show_histo: bool

@st.cache_data
def data_prep(path: str = "vehicles_us.csv") -> pd.DataFrame:
    """Load .csv file and process as per EDA. Cached so checkboxes
    run without latency."""
    df = pd.read_csv('vehicles_us.csv')

    # dtype conversion
    df['model_year'] = pd.to_numeric(
        df['model_year'],
        errors='coerce'
        ).astype('Int64')

    df['cylinders'] = pd.to_numeric(
        df['cylinders'],
        errors='coerce'
        ).astype('Int64')

    df['odometer'] = pd.to_numeric(
        df['odometer'],
        errors='coerce'
        ).astype('Int64')

    df['date_posted'] = pd.to_datetime(
        df['date_posted'],
        format='%Y-%m-%d'
        )

    # data enrichment
    words = df['model'].str.split(" ")
    df['brand'] = words.str[0]

    df['log_price'] = np.log10(df['price']+1)
    df['log_odometer'] = np.log10(df['odometer']+1)

    df['age'] = 2020 - df['model_year']

    df = df.query('price > 1')

    return df


def gen_plots(df,control: ControlFlags):
    scatter = None
    histo = None

    if control.show_scatter:
        scatter = px.scatter(df,
                             x='odometer',
                             y='price',
                             log_y=True,
                             labels={'odometer':'Odómetro','price':'log(Precio [USD])'},
                             color='brand',
                             title='Odómetro vs Precio (escala log)',
                             subtitle='Segregado por marca. Valores ficticios (p. ej. $1.00) excluidos'
                             )
    if control.show_histo:
        histo = px.histogram(df,
                             x='price',
                             labels={'price':'Precio [USD]'},
                             nbins=60,
                             color='condition',
                             title='Distribución de precios',
                             subtitle='Segregado por condición. Valores ficticios (p. ej. $1.00) excluidos'
                             )

    return (scatter, histo)

st.title("Sprint 7: Proyecto")
st.write("Desarrollo de app en streamlit, despliege en Render.")
st.write("Tema: Análisis de mercado: vehículos usados.")

show_scatter = st.checkbox("Generar gráfico de dispersión")
show_histo = st.checkbox("Generar histograma")

dataset = data_prep()
flags = ControlFlags(show_scatter, show_histo)

scatter_fig, histo_fig = gen_plots(df=dataset, control=flags)

if scatter_fig is not None:
    st.plotly_chart(scatter_fig)
if histo_fig is not None:
    st.plotly_chart(histo_fig)