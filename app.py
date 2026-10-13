import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Configuração da página do aplicativo
st.set_page_config(page_title="Painel de Análise Eleitoral", layout="wide")

st.title("📊 Painel de Análise Eleitoral - Visão Nacional e Regional")
st.markdown("Explore a votação por Estado, Município e Candidato com mapas interativos.")

@st.cache_data
def carregar_dados():
    # Carrega a base otimizada em formato parquet
    df = pd.read_parquet("dados_eleitorais_otimizados.parquet")
    return df

with st.spinner("Carregando os dados eleitorais..."):
    df = carregar_dados()

# Barra lateral (Sidebar) para os filtros
st.sidebar.header("🔍 Filtros de Pesquisa")

# Seleção de Candidato global ou por UF
candidatos = sorted(df['NM_VOTAVEL'].unique())
candidato_selecionado = st.sidebar.selectbox("Selecione o Candidato / Opção:", candidatos)

ufs = sorted(df['SG_UF'].unique())
uf_selecionada = st.sidebar.selectbox("Selecione o Estado (UF) para detalhamento:", ufs)

# Tile URL pública sem exigência de API Key (Esri WorldTopoMap)
TILE_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}'
TILE_ATTR = 'Esri WorldTopoMap'

# ==========================================
# 1. VISÃO GERAL DO PAÍS
# ==========================================
st.header(f"🇧🇷 Panorama Nacional: {candidato_selecionado}")

df_candidato_geral = df[df['NM_VOTAVEL'] == candidato_selecionado]
votos_por_uf = df_candidato_geral.groupby('SG_UF')['QT_VOTOS'].sum().reset_index()

col_mapa_br, col_ranking_br = st.columns([1.2, 0.8])

with col_mapa_br:
    st.subheader("Mapa Geral do Brasil")
    mapa_brasil = folium.Map(
        location=[-15.788497, -47.879738], 
        zoom_start=4, 
        tiles=TILE_URL,
        attr=TILE_ATTR
    )
    st_folium(mapa_brasil, width=600, height=400)

with col_ranking_br:
    st.subheader("Votos Totais por UF")
    votos_por_uf_ordenado = votos_por_uf.sort_values(by='QT_VOTOS', ascending=False)
    st.dataframe(votos_por_uf_ordenado, use_container_width=True, height=350)

st.markdown("---")

# ==========================================
# 2. VISÃO DETALHADA POR ESTADO E MUNICÍPIO
# ==========================================
st.header(f"📍 Detalhamento Regional: {uf_selecionada}")

df_filtrado = df[(df['SG_UF'] == uf_selecionada) & (df['NM_VOTAVEL'] == candidato_selecionado)]

total_votos_uf = df_filtrado['QT_VOTOS'].sum()
st.metric(label=f"Total de Votos para {candidato_selecionado} em {uf_selecionada}", value=f"{total_votos_uf:,}")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"Top Municípios - {uf_selecionada}")
    if not df_filtrado.empty:
        top_mun = df_filtrado.groupby('NM_MUNICIPIO')['QT_VOTOS'].sum().reset_index()
        top_mun = top_mun.sort_values(by='QT_VOTOS', ascending=False)
        st.dataframe(top_mun.head(15), use_container_width=True)
    else:
        st.warning("Nenhum registro encontrado para os filtros selecionados.")

with col2:
    st.subheader("🗺️ Mapa Regional")
    mapa_regional = folium.Map(
        location=[-15.788497, -47.879738], 
        zoom_start=6, 
        tiles=TILE_URL,
        attr=TILE_ATTR
    )
    st_folium(mapa_regional, width=600, height=400)
