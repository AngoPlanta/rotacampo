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

# Banco de imagens reais das culturas locais do Planalto Central (Huambo)
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

    /* Banner Hero com lavoura verde */
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

    /* KPIs */
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

    /* Card de texto do ciclo */
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

# Hero Header
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

# Sidebar
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

# KPIs
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("""
    <div class="metric-box">
        <div class="metric-title">📍 Província</div>
        <div class="metric-val">Huambo</div>
        <div class="metric-desc">Planalto Central (-12.78°, 15.74°)</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">🌡️ Calor Máximo</div>
        <div class="metric-val">{df['Temp_Max_C'].max():.1f} °C</div>
        <div class="metric-desc">Setembro (Pico de evaporação)</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">🌧️ Chuva Máxima</div>
        <div class="metric-val">{df['Chuva_mm'].max():.1f} mm</div>
        <div class="metric-desc">Outubro (Início das chuvas)</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">💧 Umidade Solo</div>
        <div class="metric-val">{df['Umidade_Solo_Idx'].mean():.2f} idx</div>
        <div class="metric-desc">Média Satélite Meteomatics</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

aba1, aba2, aba3 = st.tabs([
    "🧭 Plano de Rotação com Culturas Locais",
    "📊 Dados de Chuva & Solo (NASA)",
    "🗺️ Mapa da Região do Huambo"
])

with aba1:
    # Vitrine das principais culturas locais do Huambo
    st.markdown("### 🌾 Principais Culturas Monitoradas no Planalto Central")
    v1, v2, v3, v4 = st.columns(4)
    with v1:
        st.image(IMAGENS_CULTURAS["milho"], caption="Milho (Base energética)", use_container_width=True)
    with v2:
        st.image(IMAGENS_CULTURAS["feijao"], caption="Feijão (Fixador de nitrogênio)", use_container_width=True)
    with v3:
        st.image(IMAGENS_CULTURAS["batata_rena"], caption="Batata-rena (Alta rentabilidade)", use_container_width=True)
    with v4:
        st.image(IMAGENS_CULTURAS["mandioca"], caption="Mandioca (Resistente ao cacimbo)", use_container_width=True)

    st.markdown("---")

    # Diagnóstico do solo
    if "Milho" in cultura_anterior:
        st.warning("⚠️ **Diagnóstico da Terra:** O milho puxou muito nitrogênio do solo. Por isso, começamos a rotação com leguminosas para devolver fertilidade natural.")
    elif "Feijão" in cultura_anterior:
        st.success("✅ **Diagnóstico da Terra:** O feijão deixou o solo rico em nitrogênio natural — momento excelente para culturas exigentes como batata-rena ou milho.")
    elif "Batata" in cultura_anterior:
        st.info("ℹ️ **Diagnóstico da Terra:** A colheita da batata-rena mexeu bastante na terra. Recomendamos culturas que protejam o solo contra a erosão das chuvas.")
    else:
        st.success("🌱 **Diagnóstico da Terra:** Terra descansada e pronta para iniciar um ciclo produtivo adaptado ao clima do Huambo.")

    st.markdown(f"### 🗓️ Plano Visual de 3 Ciclos para a sua Lavra ({area_ha} ha)")

    if "lucro" in prioridade:
        ciclos = [
            ("Ciclo 1 • Outubro a Janeiro (Época Chuvosa)", "Feijão-vulgar (Colheita Rápida)",
             "Aproveita o arranque das chuvas (68.7 mm) e a umidade ideal do solo (0.95 idx), recuperando nitrogênio e gerando dinheiro rápido em 75 dias.",
             IMAGENS_CULTURAS["feijao"], "Feijão-vulgar"),
            ("Ciclo 2 • Fevereiro a Maio (Chuvas Tardias)", "Batata-rena Comercial",
             "Usa o nitrogênio deixado pelo feijão e a umidade elevada de abril (1.11 idx), garantindo tubérculos graúdos e alta procura nos mercados do Huambo.",
             IMAGENS_CULTURAS["batata_rena"], "Batata-rena"),
            ("Ciclo 3 • Junho a Setembro (Cacimbo / Seca)",
             "Hortícolas (Repolho e Tomate)" if irrigacao else "Feijão-frade / Milho Verde Irrigado" if irrigacao else "Feijão-frade Tolerante à Seca",
             "No cacimbo a umidade superficial cai a zero; " + ("com irrigação você vende hortícolas na entressafra com preço alto." if irrigacao else "o feijão-frade resiste bem sem chuva e evita prejuízo."),
             IMAGENS_CULTURAS["horticolas"] if irrigacao else IMAGENS_CULTURAS["feijao"],
             "Hortícolas" if irrigacao else "Feijão-frade")
        ]
    elif "força" in prioridade:
        ciclos = [
            ("Ciclo 1 • Outubro a Janeiro (Época Chuvosa)", "Soja ou Amendoim (Adubação Natural)",
             "Fixa grande quantidade de nitrogênio nas raízes e cobre o terreno contra a erosão das primeiras chuvas fortes.",
             IMAGENS_CULTURAS["soja_amendoim"], "Soja e Amendoim"),
            ("Ciclo 2 • Fevereiro a Maio (Chuvas Tardias)", "Milho Consorciado com Leguminosas",
             "Aproveita a boa umidade de fevereiro a abril (0.99–1.11 idx) para produzir grãos e bastante palhada orgânica.",
             IMAGENS_CULTURAS["milho"], "Milho no Planalto"),
            ("Ciclo 3 • Junho a Setembro (Cacimbo / Seca)", "Cobertura Morta / Pousio Protegido",
             "Mantém a terra coberta quando o calor chega a 30°C em setembro, segurando a umidade profunda e protegendo a vida do solo.",
             IMAGENS_CULTURAS["cobertura"], "Solo Coberto")
        ]
    else:
        ciclos = [
            ("Ciclo 1 • Outubro a Janeiro (Época Chuvosa)", "Milho + Feijão (Consórcio Tradicional)",
             "Garante a fuba e o feijão da família aproveitando a melhor janela de chuvas e temperatura amena (23–25°C).",
             IMAGENS_CULTURAS["milho"], "Milho e Feijão"),
            ("Ciclo 2 • Fevereiro a Maio (Chuvas Tardias)", "Batata-doce de Polpa Alaranjada",
             "Rica em vitaminas, muito bem adaptada ao Planalto Central e resistente às oscilações do fim das chuvas.",
             IMAGENS_CULTURAS["batata_doce"], "Batata-doce"),
            ("Ciclo 3 • Junho a Setembro (Cacimbo / Seca)", "Mandioca (Reserva Alimentar na Terra)",
             "Funciona como uma despensa viva debaixo da terra durante os 4 meses de chuva zero no cacimbo.",
             IMAGENS_CULTURAS["mandioca"], "Mandioca")
        ]

    # Renderiza cada ciclo com imagem da cultura à esquerda e recomendação à direita
    for fase, cultura, desc, img_url, legenda in ciclos:
        col_foto, col_info = st.columns([1, 2.3])
        with col_foto:
            st.image(img_url, caption=legenda, use_container_width=True)
        with col_info:
            st.markdown(f"""
            <div class="cycle-card-modern">
                <div class="cycle-phase">{fase}</div>
                <div class="cycle-name">{cultura}</div>
                <p class="cycle-text">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 0.6rem;'></div>", unsafe_allow_html=True)

with aba2:
    st.subheader("Clima e Umidade do Solo no Huambo (Dados Satélite)")
    st.caption("Leitura mensal coletada via API Meteomatics para orientar o calendário agrícola.")

    g1, g2 = st.columns(2)
    with g1:
        fig_chuva = px.bar(
            df, x="data", y="Chuva_mm",
            title="Chuva Mensal no Huambo (mm)",
            labels={"data": "Mês", "Chuva_mm": "Chuva (mm)"},
            color_discrete_sequence=["#1e6b47"]
        )
        fig_chuva.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_chuva, use_container_width=True)

    with g2:
        fig_solo = go.Figure()
        fig_solo.add_trace(go.Scatter(
            x=df["data"], y=df["Umidade_Solo_Idx"],
            mode="lines+markers", name="Umidade do Solo (-5cm)",
            line=dict(color="#2e7d32", width=3)
        ))
        fig_solo.add_trace(go.Scatter(
            x=df["data"], y=df["Temp_Max_C"] / 30.0,
            mode="lines+markers", name="Calor Relativo (Temp/30°C)",
            line=dict(color="#d97706", dash="dash", width=2)
        ))
        fig_solo.update_layout(
            title="Umidade na Raiz (-5cm) vs. Calor",
            plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig_solo, use_container_width=True)

    with st.expander("📄 Ver tabela completa de dados climáticos"):
        st.dataframe(df, use_container_width=True)

with aba3:
    st.subheader("Localização Agroclimática — Huambo, Planalto Central")
    st.markdown("Coordenadas monitoradas: **-12.7761° S, 15.7392° E**")
    mapa = folium.Map(location=[-12.7761, 15.7392], zoom_start=11)
    folium.Marker(
        [-12.7761, 15.7392],
        popup="Estação Agrícola Virtual — Huambo",
        tooltip="Planalto Central — RotaCampo",
        icon=folium.Icon(color="green", icon="leaf")
    ).add_to(mapa)
    html(mapa._repr_html_(), height=440)
