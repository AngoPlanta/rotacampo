import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit.components.v1 import html

st.set_page_config(
    page_title="RotaCampo — Agricultura Inteligente em Angola",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual moderno AgroTech com identidade acolhedora
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background-color: #f4f7f4;
        color: #1b2e22;
    }

    /* Banner Hero com Imagem de Fundo Real */
    .hero-banner {
        background: linear-gradient(180deg, rgba(16, 53, 35, 0.85) 0%, rgba(26, 82, 53, 0.92) 100%), 
                    url('https://images.unsplash.com/photo-1595974482597-4f8c7cf1c7c1?q=80&w=1600&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        padding: 2.8rem 2.5rem;
        border-radius: 20px;
        color: #ffffff;
        margin-bottom: 1.8rem;
        box-shadow: 0 12px 30px rgba(16, 53, 35, 0.2);
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.35rem 0.95rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        margin-bottom: 0.8rem;
        backdrop-filter: blur(4px);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        line-height: 1.2;
    }
    .hero-sub {
        font-size: 1.05rem;
        color: #e2f2e8;
        margin: 0;
        max-width: 800px;
        line-height: 1.5;
    }

    /* Cartões de Métricas */
    .metric-box {
        background: #ffffff;
        border: 1px solid #dcebe2;
        border-radius: 16px;
        padding: 1.2rem 1.3rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.03);
    }
    .metric-title {
        font-size: 0.78rem;
        color: #4a6b55;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-val {
        font-size: 1.6rem;
        font-weight: 700;
        color: #14452f;
        margin: 0.3rem 0;
    }
    .metric-desc {
        font-size: 0.82rem;
        color: #2e7d32;
        font-weight: 600;
    }

    /* Cartões de Ciclos de Rotação com Estilo Limpo */
    .cycle-card-modern {
        background: #ffffff;
        border-radius: 16px;
        border-left: 6px solid #2e7d32;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        display: flex;
        flex-direction: column;
        gap: 0.3rem;
    }
    .cycle-phase {
        font-size: 0.78rem;
        font-weight: 700;
        color: #2e7d32;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .cycle-name {
        font-size: 1.3rem;
        font-weight: 700;
        color: #103523;
    }
    .cycle-text {
        font-size: 0.95rem;
        color: #3b5243;
        line-height: 1.5;
        margin: 0;
    }

    /* Estilização da Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #dcebe2;
    }
</style>
""", unsafe_allow_html=True)

# Banner Principal com Identidade Visual RotaCampo
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">🛰️ NASA SPACE APPS CHALLENGE • EQUIPE ANGOPLANTA</div>
    <h1 class="hero-title">🌱 RotaCampo: O Futuro da Lavra no Planalto Central</h1>
    <p class="hero-sub">Sistema inteligente adaptado para agricultores locais do Huambo, cruzando dados de satélite da NASA e Meteomatics com a sabedoria da terra para garantir colheitas fartas, solo fértil e renda o ano todo.</p>
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

# Sidebar Personalizada
st.sidebar.markdown("### 🚜 Configuração da Lavra")
st.sidebar.caption("Personalize com os dados reais da sua propriedade no Huambo.")
area_ha = st.sidebar.slider("Área cultivável (hectares)", 0.5, 50.0, 2.5, step=0.5)

cultura_anterior = st.sidebar.selectbox(
    "Última colheita realizada:",
    ["Milho (Cereal - consome muito nitrogênio)",
     "Feijão-vulgar (Leguminosa - fixa nitrogênio)",
     "Batata-rena (Tubérculo - exige solo solto)",
     "Solo em pousio / Primeira abertura de lavra"]
)

prioridade = st.sidebar.radio(
    "Principal objetivo para os próximos ciclos:",
    [
        "💰 Maximizar lucro e retorno rápido",
        "🌿 Recuperar a fertilidade e umidade do solo",
        "🌽 Segurança alimentar familiar contínua"
    ]
)

irrigacao = st.sidebar.checkbox("Possui sistema de irrigação no cacimbo?", value=False)

# Cartões de Métricas Principais (KPIs com imagens de fundo temáticas na mente do produtor)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("""
    <div class="metric-box">
        <div class="metric-title">📍 Localização</div>
        <div class="metric-val">Huambo</div>
        <div class="metric-desc">Planalto Central (-12.78°, 15.74°)</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">🌡️ Pico Térmico</div>
        <div class="metric-val">{df['Temp_Max_C'].max():.1f} °C</div>
        <div class="metric-desc">Setembro (Alerta de Seca)</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">🌧️ Pico de Chuva</div>
        <div class="metric-val">{df['Chuva_mm'].max():.1f} mm</div>
        <div class="metric-desc">Outubro (Abertura das Chuvas)</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">💧 Umidade do Solo</div>
        <div class="metric-val">{df['Umidade_Solo_Idx'].mean():.2f} idx</div>
        <div class="metric-desc">Média Satélite Meteomatics</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Abas do Aplicativo
aba1, aba2, aba3 = st.tabs([
    "🧭 Plano de Rotação Personalizado",
    "📊 Clima & Umidade do Solo (NASA)",
    "🗺️ Mapa da Lavra no Huambo"
])

with aba1:
    # Seção com imagem ilustrativa agrícola local
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        st.image(
            "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?q=80&w=800&auto=format&fit=crop",
            caption="Planalto Central de Angola — Terra fértil e produtiva",
            use_container_width=True
        )
    with col_txt:
        st.subheader("Recomendação Especial para o seu Solo")
        if "Milho" in cultura_anterior:
            st.warning("⚠️ **Aviso Agronômico:** O milho esgotou parte do nitrogênio da terra. O plano abaixo inicia com uma leguminosa para devolver vida ao solo.")
        elif "Feijão" in cultura_anterior:
            st.success("✅ **Solo Enriquecido:** O cultivo anterior de feijão deixou o terreno cheio de nutrientes naturais. Excelente base para os próximos ciclos.")
        elif "Batata" in cultura_anterior:
            st.info("ℹ️ **Manejo de Solo:** A colheita da batata mobilizou o solo. Recomendamos proteção e cobertura vegetal.")
        else:
            st.success("🌱 **Nova Lavra:** Terreno pronto para receber o primeiro ciclo produtivo adaptado às chuvas do Huambo.")

        if "lucro" in prioridade:
            resumo_estrategia = f"Estratégia comercial focada em alta rentabilidade e retorno rápido em {area_ha} hectares."
        elif "fertilidade" in prioridade:
            resumo_estrategia = f"Estratégia focada em biologia do solo, retenção de umidade e adubação verde em {area_ha} hectares."
        else:
            resumo_estrategia = f"Estratégia focada em resiliência alimentar e colheita garantida o ano todo em {area_ha} hectares."
        st.write(resumo_estrategia)

    st.markdown("---")
    st.markdown("### 🗓️ Seus Próximos 3 Ciclos de Cultivo")

    if "lucro" in prioridade:
        ciclos = [
            ("Ciclo 1 • Outubro a Janeiro (Época Chuvosa)", "Feijão-vulgar (Variedade Precoce)", "Aproveita o início das chuvas (68.7 mm) e umidade ideal do solo (0.95 idx), recuperando nitrogênio e gerando caixa em 75 dias."),
            ("Ciclo 2 • Fevereiro a Maio (Chuvas Tardias)", "Batata-rena de Alta Qualidade", "Usa o nitrogênio fixado pelo feijão e o pico de umidade do solo em abril (1.11 idx), entregando alto valor comercial no mercado."),
            ("Ciclo 3 • Junho a Setembro (Cacimbo / Seca)", "Hortícolas de Entressafra (Repolho/Tomate)" if irrigacao else "Feijão-frade / Sorgo Resistente à Seca", "Com umidade do solo zerada no cacimbo, " + ("a irrigação suplementar garante lucros altos na entressafra." if irrigacao else "evita perdas sem depender de chuvas."))
        ]
    elif "fertilidade" in prioridade:
        ciclos = [
            ("Ciclo 1 • Outubro a Janeiro (Época Chuvosa)", "Soja ou Amendoim + Adubação Verde", "Fixação biológica intensa de nitrogênio e proteção contra erosão nas fortes chuvas de abertura."),
            ("Ciclo 2 • Fevereiro a Maio (Chuvas Tardias)", "Milho consorciado com Mucuna-preta", "Aproveita a umidade elevada de fevereiro a abril para gerar biomassa orgânica rica e proteger o solo."),
            ("Ciclo 3 • Junho a Setembro (Cacimbo / Seca)", "Pousio Coberto com Palhada / Aveia", "Mantém o terreno coberto quando a temperatura chega a 30°C em setembro, evitando ressecamento e erosão eólica.")
        ]
    else:
        ciclos = [
            ("Ciclo 1 • Outubro a Janeiro (Época Chuvosa)", "Milho + Feijão em Consórcio Tradicional", "Garante base calórica e proteica essencial para a família aproveitando a janela chuvosa estável."),
            ("Ciclo 2 • Fevereiro a Maio (Chuvas Tardias)", "Batata-doce de Polpa Alaranjada", "Excelente adaptação ao Planalto Central, alta produtividade e resistência natural a variações climáticas."),
            ("Ciclo 3 • Junho a Setembro (Cacimbo / Seca)", "Mandioca (Colheita Escalonada) / Feijão-frade", "Garante alimento seguro e nutritivo durante os 4 meses de seca rigorosa e precipitação zero no cacimbo.")
        ]

    for fase, cultura, desc in ciclos:
        st.markdown(f"""
        <div class="cycle-card-modern">
            <div class="cycle-phase">{fase}</div>
            <div class="cycle-name">{cultura}</div>
            <p class="cycle-text">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

with aba2:
    st.subheader("Comportamento do Clima e Umidade do Solo no Huambo")
    st.caption("Dados oficiais processados em tempo quase real através da integração com a API Meteomatics e modelos globais.")

    g1, g2 = st.columns(2)
    with g1:
        fig_chuva = px.bar(
            df, x="data", y="Chuva_mm",
            title="Precipitação Acumulada Mensal (mm)",
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
            mode="lines+markers", name="Índice de Estresse Térmico",
            line=dict(color="#d97706", dash="dash", width=2)
        ))
        fig_solo.update_layout(
            title="Umidade Superficial vs. Pressão Térmica",
            plot_bgcolor="white", paper_bgcolor="white"
        )
        st.plotly_chart(fig_solo, use_container_width=True)

    with st.expander("📄 Visualizar Tabela de Dados Brutos (Meteomatics Cache)"):
        st.dataframe(df, use_container_width=True)

with aba3:
    st.subheader("Mapeamento da Estação Agrícola Virtual")
    st.markdown("Visualização geoespacial do ponto monitorado no **Planalto Central (Huambo)** para cruzamento de variáveis agroclimáticas.")
    
    mapa = folium.Map(location=[-12.7761, 15.7392], zoom_start=11)
    folium.Marker(
        [-12.7761, 15.7392],
        popup="Estação Agrícola Huambo (-12.7761, 15.7392)",
        tooltip="Talhão Monitorado — RotaCampo",
        icon=folium.Icon(color="green", icon="leaf")
    ).add_to(mapa)
    html(mapa._repr_html_(), height=450)
