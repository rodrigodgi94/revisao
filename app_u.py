import streamlit as st
import pandas as pd

# Configuração da página do aplicativo
st.set_page_config(page_title="Painel de Análise Eleitoral", layout="wide")

st.title("📊 Painel de Análise Eleitoral - Gráficos Interativos")
st.markdown("Analise a votação de forma gráfica, filtrando por estado, município e candidatos.")

@st.cache_data
def carregar_dados():
    df = pd.read_parquet("dados_eleitorais_otimizados.parquet")
    return df

with st.spinner("Carregando os dados eleitorais..."):
    df = carregar_dados()

# Barra lateral (Sidebar) para os filtros e opções do gráfico
st.sidebar.header("🔍 Painel de Controle e Filtros")

# Opção de visualização do gráfico principal
tipo_visao = st.sidebar.radio(
    "Escolha a Visão Principal:",
    ["Panorama Nacional (Por UF)", "Comparativo de Candidatos", "Detalhamento por Município"]
)

# Filtro de Candidato
candidatos = sorted(df['NM_VOTAVEL'].unique())
candidato_selecionado = st.sidebar.selectbox("Selecione o Candidato / Opção:", candidatos)

# Filtro de UF para o detalhamento
ufs = sorted(df['SG_UF'].unique())
uf_selecionada = st.sidebar.selectbox("Selecione o Estado (UF):", ufs)

st.markdown("---")

# ==========================================
# VISÃO 1: PANORAMA NACIONAL (POR UF)
# ==========================================
if tipo_visao == "Panorama Nacional (Por UF)":
    st.header(f"🇧🇷 Panorama Nacional por Estado: {candidato_selecionado}")
    
    df_candidato_geral = df[df['NM_VOTAVEL'] == candidato_selecionado]
    votos_por_uf = df_candidato_geral.groupby('SG_UF')['QT_VOTOS'].sum().reset_index()
    votos_por_uf = votos_por_uf.sort_values(by='QT_VOTOS', ascending=False)
    
    total_geral = votos_por_uf['QT_VOTOS'].sum()
    st.metric(label="Total de Votos no Brasil para esta Opção", value=f"{total_geral:,}")
    
    col_grafico, col_tabela = st.columns([1.5, 0.5])
    
    with col_grafico:
        st.subheader("Gráfico de Votos por Estado (UF)")
        # Gráfico de barras configurável nativo do Streamlit
        st.bar_chart(votos_por_uf.set_index('SG_UF')['QT_VOTOS'], use_container_width=True, height=500)
        
    with col_tabela:
        st.subheader("Ranking por UF")
        st.dataframe(votos_por_uf, use_container_width=True, height=500)

# ==========================================
# VISÃO 2: COMPARATIVO DE CANDIDATOS NA UF
# ==========================================
elif tipo_visao == "Comparativo de Candidatos":
    st.header(f"⚖️ Comparativo de Candidatos em: {uf_selecionada}")
    
    df_uf = df[df['SG_UF'] == uf_selecionada]
    votos_candidatos_uf = df_uf.groupby('NM_VOTAVEL')['QT_VOTOS'].sum().reset_index()
    votos_candidatos_uf = votos_candidatos_uf.sort_values(by='QT_VOTOS', ascending=False)
    
    st.subheader(label=f"Total de Votos Registrados em {uf_selecionada}")
    
    # Gráfico de barras comparativo entre todos os candidatos da UF
    st.bar_chart(votos_candidatos_uf.set_index('NM_VOTAVEL')['QT_VOTOS'], use_container_width=True, height=450)
    
    st.subheader("Tabela Detalhada de Votação")
    st.dataframe(votos_candidatos_uf, use_container_width=True)

# ==========================================
# VISÃO 3: DETALHAMENTO POR MUNICÍPIO
# ==========================================
elif tipo_visao == "Detalhamento por Município":
    st.header(f"📍 Detalhamento por Município em {uf_selecionada}: {candidato_selecionado}")
    
    df_filtrado = df[(df['SG_UF'] == uf_selecionada) & (df['NM_VOTAVEL'] == candidato_selecionado)]
    
    total_votos_uf = df_filtrado['QT_VOTOS'].sum()
    st.metric(label=f"Total de Votos na UF", value=f"{total_votos_uf:,}")
    
    top_n = st.sidebar.slider("Quantos municípios exibir no gráfico?", min_value=5, max_value=30, value=15)
    
    top_mun = df_filtrado.groupby('NM_MUNICIPIO')['QT_VOTOS'].sum().reset_index()
    top_mun = top_mun.sort_values(by='QT_VOTOS', ascending=False)
    
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.subheader(f"Top {top_n} Municípios")
        top_grafico = top_mun.head(top_n).set_index('NM_MUNICIPIO')
        st.bar_chart(top_grafico['QT_VOTOS'], use_container_width=True, height=450)
        
    with col2:
        st.subheader("Tabela de Municípios")
        st.dataframe(top_mun, use_container_width=True, height=450)
