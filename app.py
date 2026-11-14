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
    .chart-explain {{
        background: #ffffff;
        border: 1px solid #dcebe2;
        border-left: 4px solid #1e6b47;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-top: 0.6rem;
        font-size: 0.92rem;
        color: #243b2d;
        line-height: 1.5;
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
    meses_pt = {
        "01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr",
        "05": "Mai", "06": "Jun", "07": "Jul", "08": "Ago",
        "09": "Set", "10": "Out", "11": "Nov", "12": "Dez"
    }
    df["mes_label"] = df["data"].apply(lambda x: f"{meses_pt[x.split('-')[1]]}/{x.split('-')[0][2:]}")
    df = df.rename(columns={
        "t_max_2m_24h:C": "Temp_Max_C",
        "precip_24h:mm": "Chuva_mm",
        "soil_moisture_index_-5cm:idx": "Umidade_Solo_Idx"
    })
    df["Estacao"] = df["Umidade_Solo_Idx"].apply(
        lambda u: "Cacimbo (Seca)" if u < 0.25 else "Época das Chuvas"
    )
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
             "Hortícolas (Tomate e Repolho)" if irrigacao else "Feijão-frade Tolerante à Seca",
             "No cacimbo a umidade superficial cai a zero; " + ("com irrigação você vende hortícolas na entressafra com preço alto." if irrigacao else "o feijão-frade resiste bem sem chuva e evita prejuízo."),
             IMAGENS_CULTURAS["horticolas"] if irrigacao else IMAGENS_CULTURAS["feijao"],
             "Hortícolas (Tomate)" if irrigacao else "Feijão-frade")
        ]
    elif "força" in prioridade:
        ciclos = [
            ("Ciclo 1 • Outubro a Janeiro (Época Chuvosa)", "Amendoim ou Soja (Adubação Natural)",
             "Fixa grande quantidade de nitrogênio nas raízes e cobre o terreno contra a erosão das primeiras chuvas fortes.",
             IMAGENS_CULTURAS["soja_amendoim"], "Amendoim / Leguminosas"),
            ("Ciclo 2 • Fevereiro a Maio (Chuvas Tardias)", "Milho Consorciado com Leguminosas",
             "Aproveita a boa umidade de fevereiro a abril (0.99–1.11 idx) para produzir grãos e bastante palhada orgânica.",
             IMAGENS_CULTURAS["milho"], "Milho no Planalto"),
            ("Ciclo 3 • Junho a Setembro (Cacimbo / Seca)", "Cobertura Morta / Pousio Protegido",
             "Mantém a terra coberta quando o calor chega a 30°C em setembro, segurando a umidade profunda e protegendo a vida do solo.",
             IMAGENS_CULTURAS["cobertura"], "Solo Protegido")
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
    st.subheader("Leitura Explicativa do Clima e Solo no Huambo")
    st.markdown("Estes gráficos traduzem os dados de satélite da **NASA / Meteomatics** em decisões práticas de plantio para o agricultor.")

    g1, g2 = st.columns(2)
    with g1:
        fig_chuva = px.bar(
            df, x="mes_label", y="Chuva_mm", color="Estacao",
            text="Chuva_mm",
            title="1. Calendário de Chuvas no Huambo (mm)",
            labels={"mes_label": "Mês", "Chuva_mm": "Chuva (mm)", "Estacao": "Estação"},
            color_discrete_map={
                "Época das Chuvas": "#1e6b47",
                "Cacimbo (Seca)": "#d97706"
            }
        )
        fig_chuva.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_chuva.add_annotation(
            x="Out/26", y=68.7,
            text="Pico de chuva (68.7 mm)<br>Melhor arranque de plantio",
            showarrow=True, arrowhead=2, ax=-45, ay=-30,
            bgcolor="#e8f5e9", bordercolor="#1e6b47"
        )
        fig_chuva.add_annotation(
            x="Jul/26", y=2,
            text="Cacimbo seco (0 mm)<br>Plantar só com rega ou mandioca",
            showarrow=True, arrowhead=2, ax=0, ay=-55,
            bgcolor="#fff8e1", bordercolor="#d97706"
        )
        fig_chuva.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis_range=[0, 85], legend=dict(orientation="h", y=1.12)
        )
        st.plotly_chart(fig_chuva, use_container_width=True)
        st.markdown("""
        <div class="chart-explain">
            <strong>📖 Como ler este gráfico:</strong><br>
            • <strong>Barras Verdes (Out a Abr):</strong> Época chuvosa segura para semear <em>milho, feijão e batata-rena</em> sem depender de irrigação.<br>
            • <strong>Meses Zerados (Mai a Ago):</strong> Período de <strong>Cacimbo</strong> sem chuva. Sem rega artificial, recomenda-se manter <em>mandioca, feijão-frade</em> ou cobertura morta no solo.
        </div>
        """, unsafe_allow_html=True)

    with g2:
        fig_solo = go.Figure()
        fig_solo.add_hrect(
            y0=0.5, y1=1.2, fillcolor="#e8f5e9", opacity=0.45, line_width=0,
            annotation_text="Zona Ideal de Germinação", annotation_position="top left"
        )
        fig_solo.add_hrect(
            y0=0.0, y1=0.25, fillcolor="#ffebee", opacity=0.45, line_width=0,
            annotation_text="Zona Crítica de Solo Seco", annotation_position="bottom left"
        )
        fig_solo.add_trace(go.Scatter(
            x=df["mes_label"], y=df["Umidade_Solo_Idx"],
            mode="lines+markers+text", name="Umidade na Raiz (-5cm)",
            text=df["Umidade_Solo_Idx"].round(2), textposition="top center",
            line=dict(color="#1e6b47", width=3)
        ))
        fig_solo.add_trace(go.Scatter(
            x=df["mes_label"], y=df["Temp_Max_C"] / 30.0,
            mode="lines+markers", name="Pressão de Calor (Temp/30°C)",
            line=dict(color="#d97706", dash="dash", width=2)
        ))
        fig_solo.add_annotation(
            x="Set/26", y=1.0,
            text="Setembro: 30°C + Solo seco<br>Alto risco de perda da semente",
            showarrow=True, arrowhead=2, ax=-50, ay=-25,
            bgcolor="#ffebee", bordercolor="#c62828"
        )
        fig_solo.update_layout(
            title="2. Água na Raiz (-5cm) vs. Calor Máximo",
            yaxis_title="Índice (0 = Seco | 1 = Úmido)",
            yaxis_range=[-0.08, 1.3],
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=1.12)
        )
        st.plotly_chart(fig_solo, use_container_width=True)
        st.markdown("""
        <div class="chart-explain">
            <strong>📖 Como ler este gráfico:</strong><br>
            • <strong>Linha Verde (Umidade a 5 cm):</strong> Mostra se há água onde a semente germina. Entre <strong>Fev e Abr (0.67 a 1.11)</strong> o solo tem umidade excelente.<br>
            • <strong>Alerta de Setembro (Faixa Vermelha):</strong> O calor sobe para <strong>30.0 °C</strong> enquanto o solo ainda está seco (0.00). Evite semear antes das primeiras chuvas de outubro.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📄 Ver tabela completa de dados climáticos coletados (Meteomatics / NASA)"):
        st.dataframe(df[["validdate", "mes_label", "Estacao", "Temp_Max_C", "Chuva_mm", "Umidade_Solo_Idx"]], use_container_width=True)

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
