import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit.components.v1 import html

st.set_page_config(
    page_title="RotaCampo — Agricultura Inteligente no Huambo",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

IMAGENS_CULTURAS = {
    "hero": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop",
    "milho": "https://images.unsplash.com/photo-1551754655-cd27e38d2076?q=80&w=900&auto=format&fit=crop",
    "feijao": "https://images.unsplash.com/photo-1551462147-ff29053bfc14?q=80&w=900&auto=format&fit=crop",
    "batata_rena": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?q=80&w=900&auto=format&fit=crop",
    "batata_doce": "https://images.unsplash.com/photo-1596097635121-14b63b7a0c19?q=80&w=900&auto=format&fit=crop",
    "mandioca": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?q=80&w=900&auto=format&fit=crop",
    "soja_amendoim": "https://images.unsplash.com/photo-1567892320421-1c657571ea4a?q=80&w=900&auto=format&fit=crop",
    "horticolas": "https://images.unsplash.com/photo-1592419044706-39796d40f98c?q=80&w=900&auto=format&fit=crop",
    "cobertura": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?q=80&w=900&auto=format&fit=crop",
}

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .stApp {{
        background-color: #f4f7f4;
        color: #1b2e22;
    }}
    .hero-banner {{
        background: linear-gradient(135deg, rgba(15, 56, 36, 0.88) 0%, rgba(28, 92, 58, 0.86) 100%),
                    url('{IMAGENS_CULTURAS["hero"]}');
        background-size: cover;
        background-position: center;
        padding: 2.5rem 2.3rem;
        border-radius: 20px;
        color: #ffffff;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 28px rgba(16, 53, 35, 0.18);
    }}
    .hero-badge {{
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.35rem 0.95rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        margin-bottom: 0.75rem;
    }}
    .hero-title {{
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0 0 0.45rem 0;
        line-height: 1.2;
    }}
    .hero-sub {{
        font-size: 1.02rem;
        color: #e4f3ea;
        margin: 0;
        max-width: 820px;
        line-height: 1.5;
    }}
    .metric-box {{
        background: #ffffff;
        border: 1px solid #dcebe2;
        border-radius: 16px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }}
    .metric-title {{
        font-size: 0.76rem;
        color: #4a6b55;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .metric-val {{
        font-size: 1.55rem;
        font-weight: 700;
        color: #14452f;
        margin: 0.25rem 0;
    }}
    .metric-desc {{
        font-size: 0.8rem;
        color: #2e7d32;
        font-weight: 600;
    }}
    .cycle-card-modern {{
        background: #ffffff;
        border-radius: 16px;
        border-left: 6px solid #2e7d32;
        padding: 1.35rem 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        height: 100%;
    }}
    .cycle-phase {{
        font-size: 0.78rem;
        font-weight: 700;
        color: #2e7d32;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}
    .cycle-name {{
        font-size: 1.3rem;
        font-weight: 700;
        color: #103523;
        margin: 0.25rem 0 0.5rem 0;
    }}
    .cycle-text {{
        font-size: 0.95rem;
        color: #3b5243;
        line-height: 1.55;
        margin: 0;
    }}
    section[data-testid="stSidebar"] {{
        background-color: #ffffff;
        border-right: 1px solid #dcebe2;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">🛰️ NASA SPACE APPS CHALLENGE • EQUIPE ANGOPLANTA</div>
    <h1 class="hero-title">🌱 RotaCampo: Inteligência Agrícola para o Huambo</h1>
    <p class="hero-sub">Planejamento visual de rotação de culturas adaptado aos agricultores do Planalto Central de Angola — unindo milho, feijão, batata-rena e mandioca aos dados reais de satélite da NASA & Meteomatics.</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    df = pd.read_csv("cache_huambo.csv", sep=";")
    df["data"] = pd.to_datetime(df["validdate"]).dt.strftime("%Y-%m")
    df = df.rename(columns={
        "t_max_2m_24h:C": "Temp_Max_C",
        "precip_24h:mm": "Chuva_mm",
        "soil_moisture_index_-5cm:idx": "Umidade_Solo_Idx"
    })
    return df

df = carregar_dados()

st.sidebar.markdown("### 🚜 Perfil da Sua Lavra")
st.sidebar.caption("Escolha as características da sua terra no Huambo.")
area_ha = st.sidebar.slider("Área cultivável (hectares)", 0.5, 50.0, 2.5, step=0.5)

cultura_anterior = st.sidebar.selectbox(
    "O que colheu por último nesta lavra?",
    ["Milho (Cereal - consome muito nitrogênio)",
     "Feijão-vulgar (Leguminosa - fixa nitrogênio)",
     "Batata-rena (Tubérculo - exige solo solto)",
     "Solo em pousio / Primeira abertura"]
)

prioridade = st.sidebar.radio(
    "Qual é a sua prioridade agora?",
    [
        "💰 Maximizar lucro e venda rápida",
        "🌿 Recuperar a força e umidade da terra",
        "🌽 Garantir comida na mesa o ano todo"
    ]
)

irrigacao = st.sidebar.checkbox("Tem acesso a rega/irrigação no cacimbo?", value=False)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("""
    <div class="metric-box">
        <div class="metric-title">📍 Província</div>
        <div class="metric-val">Huambo</div>
        <div class="metric-desc">Planalto Central (-12.78°, 15.74
