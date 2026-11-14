import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit.components.v1 import html

st.set_page_config(
    page_title="RotaCampo — AngoPlanta | NASA Space Apps",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual moderno (AgTech Clean UI)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background-color: #f6f8f6;
        color: #1b2e22;
    }

    /* Banner Hero */
    .hero-box {
        background: linear-gradient(135deg, #14452f 0%, #1e6b47 60%, #2d8a5b 100%);
        padding: 2rem 2.2rem;
        border-radius: 18px;
        color: #ffffff;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(20, 69, 47, 0.15);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.16);
        padding: 0.3rem 0.85rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        margin-bottom: 0.75rem;
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin: 0 0 0.4rem 0;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 1rem;
        color: #dcf2e6;
        margin: 0;
    }

    /* Cards de métricas */
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e1ebe4;
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #5b7264;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 700;
        color: #14452f;
        margin: 0.25rem 0;
    }
    .kpi-delta {
        font-size: 0.82rem;
        color: #2d8a5b;
        font-weight: 500;
    }

    /* Cards dos ciclos de rotação */
    .cycle-card {
        background: #ffffff;
        border-left: 5px solid #2d8a5b;
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    }
    .cycle-tag {
        font-size: 0.78rem;
        font-weight: 700;
        color: #2d8a5b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .cycle-crop {
        font-size: 1.25rem;
        font-weight: 700;
        color: #14452f;
        margin: 0.2rem 0 0.5rem 0;
    }
    .cycle-desc {
        font-size: 0.94rem;
        color: #3d5245;
        line-height: 1.5;
        margin: 0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e1ebe4;
    }
</style>
""", unsafe_allow_html=True)

# Hero Header
st.markdown("""
<div class="hero-box">
    <div class="hero-badge">🛰️ NASA SPACE APPS CHALLENGE • EQUIPE ANGOPLANTA</div>
    <h1 class="hero-title">🌱 RotaCampo — Inteligência Agrícola no Planalto Central</h1>
    <p class="hero-sub">Planejamento de rotação de culturas orientado por dados climáticos e de umidade do solo (NASA & Meteomatics) para o Huambo, Angola.</p>
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
st.sidebar.markdown("### 🚜 Configurar Talhão")
st.sidebar.caption("Ajuste os parâmetros da lavra para simular a melhor rotação.")
area_ha = st.sidebar.slider("Área cultivável (hectares)", 0.5, 50.0, 2.5, step=0.5)
cultura_anterior = st.sidebar.selectbox(
    "Última cultura colhida:",
    ["Milho (Cereal - consome muito nitrogênio)",
     "Feijão-vulgar (Leguminosa - fixa nitrogênio)",
     "Batata-rena (Tubérculo - exige solo solto)",
     "Solo em pousio / Primeira lavra"]
)
prioridade = st.sidebar.radio(
    "Objetivo principal para os próximos 3 ciclos:",
    [
        "💰 Maximizar retorno financeiro rápido",
        "🌿 Recuperar fertilidade e umidade do solo",
        "🌽 Segurança alimentar e resiliência à seca"
    ]
)
irrigacao = st.sidebar.checkbox("Possui irrigação suplementar no cacimbo?", value=False)

# KPIs modernos
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-label">📍 Região Monitorada</div>
        <div class="kpi-value">Huambo</div>
        <div class="kpi-delta">-12.78° S, 15.74° E • Planalto Central</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">🌡️ Pico Térmico</div>
        <div class="kpi-value">{df['Temp_Max_C'].max():.1f} °C</div>
        <div class="kpi-delta">Setembro • Alerta de evaporação</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">🌧️ Máxima de Chuva</div>
        <div class="kpi-value">{df['Chuva_mm'].max():.1f} mm</div>
        <div class="kpi-delta">Outubro • Abertura da época chuvosa</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">💧 Umidade Solo (-5cm)</div>
        <div class="kpi-value">{df['Umidade_Solo_Idx'].mean():.2f} idx</div>
        <div class="kpi-delta">Média anual • Satélite Meteomatics</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

aba1, aba2, aba3 = st.tabs([
    "🧭 Plano de Rotação (3 Ciclos)",
    "📊 Clima & Umidade do Solo",
    "🗺️ Mapa da Estação Virtual"
])

with aba1:
    if "Milho" in cultura_anterior:
        st.warning("⚠️ **Diagnóstico do Solo:** O milho consumiu bastante nitrogênio superficial. Comece com uma leguminosa fixadora antes de repetir culturas exigentes.")
    elif "Feijão" in cultura_anterior:
        st.success("✅ **Diagnóstico do Solo:** O feijão enriqueceu o solo com nitrogênio orgânico. Momento ideal para milho ou batata-rena.")
    elif "Batata" in cultura_anterior:
        st.info("ℹ️ **Diagnóstico do Solo:** Solo mobilizado pela colheita da batata. Priorize cobertura vegetal para evitar erosão nas chuvas.")
    else:
        st.success("🌱 **Diagnóstico do Solo:** Solo em repouso, pronto para abertura com cultura rústica e incorporação de matéria orgânica.")

    if "financeiro" in prioridade:
        ciclos = [
            ("Ciclo 1 • Out–Jan (Chuvas)", "Feijão-vulgar (Variedade precoce)", "Aproveita o início das chuvas (68.7 mm) e umidade ideal do solo (0.95 idx), recuperando nitrogênio e gerando caixa em 75 dias."),
            ("Ciclo 2 • Fev–Mai (Chuvas Tardias)", "Batata-rena", "Usa o nitrogênio fixado pelo feijão e o pico de umidade do solo em abril (1.11 idx), entregando alto valor comercial no mercado do Huambo."),
            ("Ciclo 3 • Jun–Set (Cacimbo)", "Hortícolas (Repolho/Tomate)" if irrigacao else "Feijão-frade / Sorgo tolerante à seca", "Com umidade do solo caindo a 0.00 idx no cacimbo, " + ("a irrigação garante venda na entressafra." if irrigacao else "evita perda de safra sem depender de chuva."))
        ]
        impacto = f"📈 Impacto estimado: +38% de margem líquida em {area_ha} ha"
    elif "fertilidade" in prioridade:
        ciclos = [
            ("Ciclo 1 • Out–Jan (Chuvas)", "Soja ou Amendoim + Cobertura", "Fixação biológica intensa de nitrogênio e proteção contra escoamento superficial nas chuvas de outubro a janeiro."),
            ("Ciclo 2 • Fev–Mai (Chuvas Tardias)", "Milho consorciado com Mucuna-preta", "Aproveita a umidade elevada de fevereiro a abril (0.99–1.11 idx) para gerar biomassa e palhada protetora."),
            ("Ciclo 3 • Jun–Set (Cacimbo)", "Pousio coberto com palhada / Aveia-preta", "Mantém o solo protegido quando a temperatura chega a 30.0 °C em setembro, reduzindo a evaporação.")
        ]
        impacto = f"🌿 Impacto estimado: +45% de retenção de umidade e matéria orgânica em {area_ha} ha"
    else:
        ciclos = [
            ("Ciclo 1 • Out–Jan (Chuvas)", "Milho + Feijão (Consórcio otimizado)", "Garante base calórica e proteica aproveitando a janela chuvosa estável (23–25 °C)."),
            ("Ciclo 2 • Fev–Mai (Chuvas Tardias)", "Batata-doce de polpa alaranjada", "Excelente adaptação ao Planalto Central e alta resistência a variações de umidade no fim das chuvas."),
            ("Ciclo 3 • Jun–Set (Cacimbo)", "Mandioca (colheita escalonada) / Feijão-frade", "Segurança alimentar garantida durante os 4 meses de precipitação zero (0.0 mm) no cacimbo.")
        ]
        impacto = f"🌽 Impacto estimado: Abastecimento alimentar contínuo por 12 meses em {area_ha} ha"

    st.markdown(f"**{impacto}**")
    for tag, cultura, desc in ciclos:
        st.markdown(f"""
        <div class="cycle-card">
            <div class="cycle-tag">{tag}</div>
            <div class="cycle-crop">{cultura}</div>
            <p class="cycle-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

with aba2:
    g1, g2 = st.columns(2)
    with g1:
        fig_chuva = px.bar(
            df, x="data", y="Chuva_mm",
            title="Precipitação Mensal (mm) — Huambo",
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
            line=dict(color="#2d8a5b", width=3)
        ))
        fig_solo.add_trace(go.Scatter(
            x=df["data"], y=df["Temp_Max_C"] / 30.0,
            mode="lines+markers", name="Estresse Térmico (Temp/30°C)",
            line=dict(color="#d97706", dash="dash", width=2)
        ))
        fig_solo.update_layout(
            title="Umidade do Solo (-5cm) vs. Estresse Térmico",
            plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig_solo, use_container_width=True)

    with st.expander("📄 Ver dados brutos da API Meteomatics (cache_huambo.csv)"):
        st.dataframe(df, use_container_width=True)

with aba3:
    st.markdown("#### 📍 Ponto de Monitoramento Agroclimático — Huambo (-12.7761, 15.7392)")
    mapa = folium.Map(location=[-12.7761, 15.7392], zoom_start=11)
    folium.Marker(
        [-12.7761, 15.7392],
        popup="Estação Virtual Meteomatics / NASA — Huambo",
        tooltip="Huambo (-12.7761, 15.7392)",
        icon=folium.Icon(color="green", icon="leaf")
    ).add_to(mapa)
    html(mapa._repr_html_(), height=430)
