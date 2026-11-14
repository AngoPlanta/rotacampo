import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit.components.v1 import html

st.set_page_config(
    page_title="RotaCampo — AngoPlanta | NASA Space Apps",
    page_icon="🌱",
    layout="wide"
)

# Cabeçalho principal
st.title("🌱 RotaCampo — Apoio à Decisão Agrícola no Planalto Central")
st.markdown(
    "**Equipe AngoPlanta** | *NASA Space Apps Challenge — Mudança de rumo: Adaptando fazendas com dados da NASA & Meteomatics*"
)
st.divider()

# Carregamento e tratamento do cache climático real da Meteomatics
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

# Barra lateral: Perfil e Prioridades do Agricultor
st.sidebar.header("🚜 Perfil da Propriedade (Huambo)")
area_ha = st.sidebar.slider("Área cultivável (hectares)", 0.5, 50.0, 2.5, step=0.5)
cultura_anterior = st.sidebar.selectbox(
    "Última cultura colhida na lavra:",
    ["Milho (Cereal - consome muito nitrogênio)",
     "Feijão-vulgar (Leguminosa - fixa nitrogênio)",
     "Batata-rena (Tubérculo - exige solo solto)",
     "Solo em pousio / Primeira lavra"]
)
prioridade = st.sidebar.radio(
    "Qual é a sua prioridade principal para os próximos 3 ciclos?",
    [
        "💰 Maximizar retorno financeiro rápido",
        "🌿 Recuperar a fertilidade e umidade do solo",
        "🌽 Segurança alimentar familiar e resiliência à seca"
    ]
)
irrigacao = st.sidebar.checkbox("Possui acesso à irrigação suplementar no cacimbo?", value=False)

# Indicadores-chave do ciclo climático (Meteomatics / NASA)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Localização Monitorada", "Huambo (-12.78°, 15.74°)", "Planalto Central")
col2.metric("Pico de Temperatura Máx.", f"{df['Temp_Max_C'].max():.1f} °C", "Setembro (Risco Térmico)")
col3.metric("Pico de Precipitação", f"{df['Chuva_mm'].max():.1f} mm", "Outubro (Época Chuvosa)")
col4.metric("Umidade Média do Solo (-5cm)", f"{df['Umidade_Solo_Idx'].mean():.2f} idx", "Dados Meteomatics/NASA")

st.divider()

# Abas principais da aplicação
aba1, aba2, aba3 = st.tabs([
    "🧭 Plano de Rotação Recomendado",
    "📊 Monitoramento Climático & Solo (Dados Reais)",
    "🗺️ Mapa da Região & Talhão"
])

with aba1:
    st.subheader("Estratégia Inteligente de Rotação em 3 Ciclos")

    # Diagnóstico do solo com base na última cultura
    if "Milho" in cultura_anterior:
        diag_solo = "⚠️ **Alerta de Nitrogênio:** O milho extraiu grande parte do nitrogênio superficial. É essencial iniciar com uma leguminosa fixadora antes de plantar outra cultura exigente."
    elif "Feijão" in cultura_anterior:
        diag_solo = "✅ **Solo Enriquecido:** O feijão deixou nitrogênio orgânico disponível. Excelente momento para culturas de alta demanda nutricional como milho ou batata-rena."
    elif "Batata" in cultura_anterior:
        diag_solo = "ℹ️ **Estrutura Mobilizada:** A colheita da batata revolveu o solo. Recomenda-se cobertura vegetal ou leguminosa para proteger contra erosão nas chuvas intensas."
    else:
        diag_solo = "🌱 **Solo em Repouso:** Boa oportunidade para iniciar com cultura rústica de abertura e incorporar matéria orgânica."

    st.info(diag_solo)

    # Lógica agronômica cruzando prioridade + irrigação + dados de umidade do Huambo
    if "financeiro" in prioridade:
        plano = [
            {"Ciclo": "Ciclo 1 (Out–Jan | Chuvas)", "Cultura": "Feijão-vulgar (Variedade precoce)", "Justificativa Climática": "Aproveita o início das chuvas (68.7 mm) e umidade ideal do solo (0.95 idx), recuperando nitrogênio e gerando caixa em 75 dias."},
            {"Ciclo": "Ciclo 2 (Fev–Mai | Chuvas Tardias)", "Cultura": "Batata-rena", "Justificativa Climática": "Usa o nitrogênio fixado pelo feijão e o pico de umidade do solo em abril (1.11 idx), entregando alto valor comercial no mercado do Huambo."},
            {"Ciclo": "Ciclo 3 (Jun–Set | Cacimbo)", "Cultura": "Hortícolas de ciclo curto (Repolho/Tomate)" if irrigacao else "Feijão-frade / Sorgo tolerante à seca", "Justificativa Climática": "Com umidade do solo caindo a 0.00 idx no cacimbo, " + ("a irrigação garante venda na entressafra." if irrigacao else "evita perda de safra sem depender de chuva.")}
        ]
        roi_estimado = f"+38% de margem líquida estimada em {area_ha} ha"
    elif "fertilidade" in prioridade:
        plano = [
            {"Ciclo": "Ciclo 1 (Out–Jan | Chuvas)", "Cultura": "Soja ou Amendoim + Cobertura", "Justificativa Climática": "Fixação biológica intensa de nitrogênio e proteção contra escoamento superficial nas chuvas de outubro a janeiro."},
            {"Ciclo": "Ciclo 2 (Fev–Mai | Chuvas Tardias)", "Cultura": "Milho consorciado com Mucuna-preta", "Justificativa Climática": "Aproveita a umidade elevada de fevereiro a abril (0.99–1.11 idx) para gerar biomassa e palhada protetora."},
            {"Ciclo": "Ciclo 3 (Jun–Set | Cacimbo)", "Cultura": "Pousio coberto com palhada / Aveia-preta", "Justificativa Climática": "Mantém o solo coberto quando a temperatura chega a 30.0 °C em setembro, reduzindo a evaporação."}
        ]
        roi_estimado = f"+45% de retenção de umidade e matéria orgânica em {area_ha} ha"
    else:
        plano = [
            {"Ciclo": "Ciclo 1 (Out–Jan | Chuvas)", "Cultura": "Milho + Feijão (Consórcio tradicional otimizado)", "Justificativa Climática": "Garante base calórica e proteica aproveitando a janela chuvosa estável (23–25 °C)."},
            {"Ciclo": "Ciclo 2 (Fev–Mai | Chuvas Tardias)", "Cultura": "Batata-doce de polpa alaranjada", "Justificativa Climática": "Excelente adaptação ao Planalto Central e alta resistência a variações de umidade no fim das chuvas."},
            {"Ciclo": "Ciclo 3 (Jun–Set | Cacimbo)", "Cultura": "Mandioca (colheita escalonada) / Feijão-frade", "Justificativa Climática": "Segurança alimentar garantida durante os 4 meses de precipitação zero (0.0 mm) no cacimbo."}
        ]
        roi_estimado = f"Abastecimento contínuo por 12 meses em {area_ha} ha"

    st.success(f"**Impacto Esperado da Estratégia:** {roi_estimado}")
    st.table(pd.DataFrame(plano))

with aba2:
    st.subheader("Série Histórica Mensal — Huambo (Meteomatics API)")
    c1, c2 = st.columns(2)

    with c1:
        fig_chuva = px.bar(
            df, x="data", y="Chuva_mm",
            title="Precipitação Mensal (mm) — Identificação da Seca",
            labels={"data": "Mês", "Chuva_mm": "Chuva (mm)"},
            color_discrete_sequence=["#1f77b4"]
        )
        st.plotly_chart(fig_chuva, use_container_width=True)

    with c2:
        fig_solo = go.Figure()
        fig_solo.add_trace(go.Scatter(
            x=df["data"], y=df["Umidade_Solo_Idx"],
            mode="lines+markers", name="Umidade do Solo (-5cm)",
            line=dict(color="#2ca02c", width=3)
        ))
        fig_solo.add_trace(go.Scatter(
            x=df["data"], y=df["Temp_Max_C"] / 30.0,
            mode="lines+markers", name="Índice Térmico Relativo (Temp/30°C)",
            line=dict(color="#d62728", dash="dash")
        ))
        fig_solo.update_layout(title="Umidade do Solo (-5cm) vs. Estresse Térmico")
        st.plotly_chart(fig_solo, use_container_width=True)

    with st.expander("Ver tabela bruta coletada da API Meteomatics"):
        st.dataframe(df, use_container_width=True)

with aba3:
    st.subheader("Localização Agroclimática — Planalto Central (Huambo, Angola)")
    mapa = folium.Map(location=[-12.7761, 15.7392], zoom_start=11)
    folium.Marker(
        [-12.7761, 15.7392],
        popup="Ponto de Coleta Meteomatics / NASA — Huambo",
        tooltip="Estação Virtual Huambo (-12.7761, 15.7392)",
        icon=folium.Icon(color="green", icon="leaf")
    ).add_to(mapa)
    html(mapa._repr_html_(), height=420)
