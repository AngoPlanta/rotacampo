"""
RotaCampo · AngoPlanta
Comparador de estratégias de rotação de culturas para o Planalto Central de Angola.

Dados esperados (opcional): cache_huambo.csv  (separador ";")
  colunas: validdate, t_max_2m_24h:C, precip_24h:mm, soil_moisture_index_-5cm:idx
  coluna opcional: ndvi  (se existir, é usada no lugar do proxy)
Se o ficheiro não existir, a app usa dados de DEMONSTRAÇÃO e avisa o utilizador.
"""
from pathlib import Path
import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import folium
import streamlit as st
from streamlit.components.v1 import html

try:
    from streamlit_folium import st_folium
    HAS_SF = True
except Exception:
    HAS_SF = False

st.set_page_config(
    page_title="RotaCampo · AngoPlanta",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───────────────────────── PALETA E ESTILO ─────────────────────────
VERDE, VERDE_ESC, FOLHA = "#1f5c3f", "#0f3323", "#3f8f5f"
TERRA, OCRE, CREME, TINTA = "#b5651d", "#e0a526", "#f7f3ea", "#1c2a22"
CORES_EST = [TERRA, VERDE, OCRE]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=DM+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #f7f3ea; color: #1c2a22; }
.block-container { padding-top: 1.4rem; max-width: 1280px; }
h1,h2,h3 { font-family: 'Fraunces', serif !important; color: #0f3323; letter-spacing: -0.01em; }
section[data-testid="stSidebar"] { background: #fffdf8; border-right: 1px solid #e6dfcc; }
section[data-testid="stSidebar"] h3 { font-size: 1.05rem; margin-top: .4rem; }

.hero { background: radial-gradient(circle at 85% 20%, rgba(224,165,38,.30), transparent 40%),
        linear-gradient(135deg, #0f3323 0%, #1f5c3f 70%, #2c7a52 100%);
        border-radius: 22px; padding: 2.2rem 2.4rem; color: #fff; margin-bottom: 1.2rem;
        box-shadow: 0 14px 30px rgba(15,51,35,.22); position: relative; overflow: hidden; }
.hero:after { content:"🌾"; position:absolute; right:28px; bottom:-18px; font-size:7.5rem; opacity:.13; }
.hero .tag { display:inline-block; background: rgba(255,255,255,.16); padding:.3rem .9rem; border-radius:999px;
        font-size:.75rem; font-weight:600; letter-spacing:.06em; margin-bottom:.8rem; }
.hero h1 { color:#fff !important; font-size:2.35rem; margin:0 0 .4rem 0; line-height:1.15; }
.hero p { color:#dcefe3; max-width:760px; margin:0; font-size:1.02rem; line-height:1.55; }

.kpi { background:#fff; border:1px solid #e6dfcc; border-radius:16px; padding:1rem 1.1rem; height:100%; }
.kpi .l { font-size:.72rem; font-weight:700; letter-spacing:.07em; text-transform:uppercase; color:#7a6a45; }
.kpi .v { font-family:'Fraunces',serif; font-size:1.65rem; font-weight:700; color:#0f3323; margin:.15rem 0; }
.kpi .d { font-size:.8rem; color:#4d6354; }

.scard { background:#fff; border:1px solid #e6dfcc; border-radius:20px; padding:1.3rem 1.3rem 1.1rem; height:100%;
        box-shadow:0 6px 18px rgba(60,50,20,.05); }
.scard.best { border:2px solid #1f5c3f; box-shadow:0 10px 26px rgba(31,92,63,.18); }
.scard .role { font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.scard .name { font-family:'Fraunces',serif; font-size:1.2rem; font-weight:700; color:#0f3323; margin:.2rem 0 .6rem; }
.scard .score { font-family:'Fraunces',serif; font-size:3rem; font-weight:700; line-height:1; color:#0f3323; }
.scard .score small { font-size:1rem; color:#7a6a45; font-family:'DM Sans',sans-serif; font-weight:600; }
.bar { height:8px; background:#efe9d8; border-radius:99px; margin:.7rem 0 .5rem; overflow:hidden; }
.bar > div { height:100%; border-radius:99px; }
.muted { font-size:.82rem; color:#5f6f64; }
.star { display:inline-block; background:#1f5c3f; color:#fff; font-size:.72rem; font-weight:700;
        padding:.2rem .65rem; border-radius:99px; margin-bottom:.4rem; }
.chip { display:block; background:#f7f3ea; border-radius:12px; padding:.5rem .7rem; margin-top:.4rem; font-size:.86rem; }
.chip b { color:#0f3323; }
.chip span { color:#7a6a45; font-size:.74rem; display:block; font-weight:600; letter-spacing:.03em; }

.bloco { background:#fff; border:1px solid #e6dfcc; border-radius:16px; padding:1.1rem 1.2rem; height:100%; }
.bloco h4 { margin:0 0 .5rem 0; font-size:1rem; font-family:'DM Sans',sans-serif; font-weight:700; }
.bloco ul { margin:0; padding-left:1.1rem; } .bloco li { font-size:.9rem; line-height:1.5; margin-bottom:.35rem; color:#26372d; }
.b-evid { border-top:5px solid #1f5c3f; } .b-ben { border-top:5px solid #3f8f5f; }
.b-lac { border-top:5px solid #e0a526; } .b-ris { border-top:5px solid #b5651d; }

.nota { background:#fff8e6; border:1px solid #f0dca0; border-radius:12px; padding:.8rem 1rem; font-size:.88rem; color:#5b4a14; }
.explica { background:#fff; border:1px solid #e6dfcc; border-left:4px solid #1f5c3f; border-radius:12px;
        padding:.85rem 1.1rem; font-size:.9rem; line-height:1.55; margin-top:.4rem; }
.conf { display:inline-block; font-weight:700; padding:.2rem .7rem; border-radius:99px; font-size:.8rem; }
.modulo { background:#fff; border:1px solid #e6dfcc; border-radius:16px; padding:1rem 1.1rem; height:100%; }
.modulo .n { font-family:'Fraunces',serif; font-size:1.6rem; color:#b5651d; font-weight:700; }
.modulo b { color:#0f3323; }
div[data-baseweb="tab-list"] { gap: .3rem; }
button[data-baseweb="tab"] { font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ───────────────────────── CONSTANTES AGRONÓMICAS ─────────────────────────
MESES = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}

CICLOS = [
    {"nome": "Ciclo 1", "janela": "Out → Jan", "fase": "Chuvas (arranque)", "meses": [10, 11, 12, 1]},
    {"nome": "Ciclo 2", "janela": "Fev → Mai", "fase": "Chuvas tardias", "meses": [2, 3, 4, 5]},
    {"nome": "Ciclo 3", "janela": "Jun → Set", "fase": "Cacimbo (seca)", "meses": [6, 7, 8, 9]},
]

LOCAIS = {  # coordenadas aproximadas (a confirmar no terreno)
    "Huambo (cidade)": (-12.7761, 15.7392),
    "Caála": (-12.8500, 15.5600),
    "Bailundo": (-12.1900, 15.8400),
}
PONTO_MAPA = "📌 Ponto escolhido no mapa"
DADOS_REF = LOCAIS["Huambo (cidade)"]  # ponto a que se referem os dados em cache

FONTE_PADRAO = "Síntese da equipa a partir de FAO EcoCrop e agronomia geral — A VALIDAR com técnico local"
# Notas 1–5 (5 = melhor para o critério). rega=True → depende de água no cacimbo.
CULTURAS = {
    "milho":       dict(nome="Milho", e="🌽", agua=2, nfix=1, raizes=3, erosao=2, seca=2, calor=3, mercado=4, renda=3, dias=120, rega=False, nota="Gasta muito azoto do solo."),
    "feijao":      dict(nome="Feijão-vulgar", e="🫘", agua=3, nfix=4, raizes=2, erosao=3, seca=2, calor=2, mercado=4, renda=3, dias=75, rega=False, nota="Fixa azoto; ciclo curto."),
    "frade":       dict(nome="Feijão-frade", e="🫛", agua=4, nfix=4, raizes=2, erosao=4, seca=5, calor=5, mercado=3, renda=3, dias=70, rega=False, nota="Muito tolerante à seca."),
    "amendoim":    dict(nome="Amendoim", e="🥜", agua=3, nfix=4, raizes=3, erosao=3, seca=3, calor=3, mercado=4, renda=4, dias=110, rega=False, nota="Fixa azoto e tem boa procura."),
    "consorcio":   dict(nome="Milho + feijão (consórcio)", e="🌽", agua=3, nfix=3, raizes=3, erosao=3, seca=3, calor=3, mercado=4, renda=3, dias=120, rega=False, nota="Base alimentar tradicional."),
    "mandioca":    dict(nome="Mandioca", e="🍠", agua=5, nfix=1, raizes=4, erosao=3, seca=5, calor=4, mercado=4, renda=3, dias=300, rega=False, nota="Ciclo longo; funciona como reserva na terra."),
    "batata_doce": dict(nome="Batata-doce", e="🍠", agua=4, nfix=1, raizes=3, erosao=4, seca=4, calor=4, mercado=3, renda=3, dias=120, rega=False, nota="Cobre o solo; tolerante."),
    "batata_rena": dict(nome="Batata-rena", e="🥔", agua=1, nfix=1, raizes=2, erosao=1, seca=1, calor=1, mercado=5, renda=5, dias=100, rega=False, nota="Alta renda mas exigente em água e solo solto."),
    "horticolas":  dict(nome="Hortícolas (tomate, repolho)", e="🍅", agua=1, nfix=1, raizes=2, erosao=2, seca=1, calor=2, mercado=5, renda=5, dias=90, rega=True, nota="Preço alto na entressafra, mas precisa de rega."),
    "cobertura":   dict(nome="Adubo verde / cobertura", e="🌿", agua=4, nfix=5, raizes=4, erosao=5, seca=4, calor=4, mercado=1, renda=1, dias=90, rega=False, nota="Protege e adubra; sem venda directa."),
    "pousio":      dict(nome="Pousio (solo descoberto)", e="🟫", agua=3, nfix=1, raizes=1, erosao=1, seca=3, calor=3, mercado=1, renda=1, dias=0, rega=False, nota="Sem cultura nem cobertura."),
}
for _c in CULTURAS.values():
    _c["fonte"] = FONTE_PADRAO
    _c["validada"] = False

ESTRATEGIAS = {  # biblioteca de alternativas
    "tradicional": ("Subsistência tradicional", ["consorcio", "batata_doce", "mandioca"]),
    "comercial": ("Renda comercial", ["feijao", "batata_rena", "frade"]),
    "horta": ("Horticultura com rega", ["feijao", "batata_rena", "horticolas"]),
    "solo": ("Recuperação do solo", ["amendoim", "consorcio", "cobertura"]),
    "agua": ("Poupa-água", ["feijao", "batata_doce", "frade"]),
    "encosta": ("Protecção de encostas", ["amendoim", "batata_doce", "cobertura"]),
    "mista": ("Mista: solo + renda", ["amendoim", "batata_rena", "mandioca"]),
    "mercado": ("Mercado local", ["consorcio", "batata_rena", "frade"]),
}
ATUAIS = {  # práticas comuns para o utilizador indicar a sua rotação actual
    "Milho contínuo (milho → milho → pousio)": ["milho", "milho", "pousio"],
    "Uma safra por ano (milho+feijão → pousio → pousio)": ["consorcio", "pousio", "pousio"],
    "Feijão e milho alternados": ["feijao", "milho", "pousio"],
    "Mandioca contínua": ["mandioca", "mandioca", "mandioca"],
    "Batata-rena em sequência": ["batata_rena", "batata_rena", "pousio"],
}

PRIORIDADES = [
    ("agua", "💧 Poupar água", 3),
    ("solo", "🌱 Melhorar o solo", 3),
    ("erosao", "⛰️ Reduzir a erosão", 2),
    ("renda", "💰 Renda extra", 3),
    ("mercado", "🏪 Mercado", 2),
    ("chuvas", "🌧️ Resistir a chuvas irregulares", 2),
    ("calor", "🌡️ Resistir ao calor", 1),
]
NOMES_CRIT = {k: n for k, n, _ in PRIORIDADES}

# ───────────────────────── DADOS ─────────────────────────
def _demo():
    datas = pd.date_range("2025-10-01", periods=12, freq="MS")
    chuva = [130, 190, 210, 230, 210, 220, 140, 20, 2, 1, 5, 40]
    umid = [0.55, 0.85, 1.0, 1.05, 1.0, 1.05, 0.8, 0.3, 0.1, 0.0, 0.0, 0.12]
    tmax = [25, 24, 23, 23, 24, 24, 25, 26, 26, 27, 29, 30]
    return pd.DataFrame({"validdate": datas, "t_max_2m_24h:C": tmax,
                         "precip_24h:mm": chuva, "soil_moisture_index_-5cm:idx": umid})


@st.cache_data
def carregar_dados():
    caminho = Path(__file__).parent / "cache_huambo.csv"
    demo = False
    if caminho.exists():
        df = pd.read_csv(caminho, sep=";")
        if df.shape[1] < 3:
            df = pd.read_csv(caminho, sep=",")
    else:
        df, demo = _demo(), True
    df = df.rename(columns={"t_max_2m_24h:C": "Temp_Max_C", "precip_24h:mm": "Chuva_mm",
                            "soil_moisture_index_-5cm:idx": "Umidade_Solo_Idx"})
    df["validdate"] = pd.to_datetime(df["validdate"])
    df = df.sort_values("validdate").reset_index(drop=True)
    df["mes"] = df["validdate"].dt.month
    df["ano"] = df["validdate"].dt.year
    df["mes_label"] = df.apply(lambda r: f"{MESES[r['mes']]}/{str(r['ano'])[2:]}", axis=1)
    df["Estacao"] = np.where(df["Umidade_Solo_Idx"] < 0.25, "Cacimbo (seca)", "Época das chuvas")

    ndvi_col = next((c for c in df.columns if c.lower() == "ndvi"), None)
    if ndvi_col:
        df["NDVI"], ndvi_real = df[ndvi_col].astype(float), True
    else:  # proxy: vegetação responde à humidade com ~1 mês de atraso
        u = df["Umidade_Solo_Idx"].clip(0, 1.1).rolling(2, min_periods=1).mean().shift(1)
        u.iloc[0] = df["Umidade_Solo_Idx"].clip(0, 1.1).iloc[0]
        df["NDVI"], ndvi_real = 0.18 + 0.55 * (u / 1.1), False
    return df, demo, ndvi_real


def kmeans(X, k, iters=60):
    X = np.asarray(X, float)
    cent = X[np.argsort(X[:, 0])[np.linspace(0, len(X) - 1, k).astype(int)]]
    lab = np.zeros(len(X), int)
    for _ in range(iters):
        lab = ((X[:, None, :] - cent[None]) ** 2).sum(2).argmin(1)
        new = np.array([X[lab == j].mean(0) if (lab == j).any() else cent[j] for j in range(k)])
        if np.allclose(new, cent):
            break
        cent = new
    return lab, cent


def haversine(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))



def grafico(fig):
    """Compatível com versões novas e antigas do Streamlit."""
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def tabela(data, **kw):
    try:
        st.dataframe(data, width="stretch", **kw)
    except TypeError:
        st.dataframe(data, use_container_width=True, **kw)


df, DEMO, NDVI_REAL = carregar_dados()

# ───────────────────────── BARRA LATERAL ─────────────────────────
if "_pendente" in st.session_state:  # aplica clique do mapa antes de criar o widget
    st.session_state["local_sel"] = st.session_state.pop("_pendente")
st.session_state.setdefault("clique", None)

with st.sidebar:
    st.markdown("## 🌱 RotaCampo")
    st.caption("by **AngoPlanta** · Planalto Central, Angola")

    st.markdown("### 1 · Local da lavra")
    opcoes = list(LOCAIS) + ([PONTO_MAPA] if st.session_state["clique"] else [])
    local_sel = st.selectbox("Onde fica a sua machamba?", opcoes, key="local_sel",
                             help="Também pode clicar no mapa, na página principal.")
    if local_sel == PONTO_MAPA and st.session_state["clique"]:
        coord = st.session_state["clique"]
    else:
        coord = LOCAIS.get(local_sel, DADOS_REF)

    st.markdown("### 2 · Rotação actual")
    atual_nome = st.selectbox("Como roda as culturas hoje?", list(ATUAIS))

    st.markdown("### 3 · As suas prioridades")
    st.caption("0 = não importa · 5 = muito importante")
    pesos = {k: st.slider(n, 0, 5, d, key=f"p_{k}") for k, n, d in PRIORIDADES}

    st.markdown("### 4 · Dados da lavra")
    area_ha = st.slider("Área (hectares)", 0.5, 50.0, 2.5, step=0.5)
    declive = st.slider("Declive do terreno (%)", 0, 30, 5,
                        help="Sem modelo de elevação no cache — indique à vista. Mais declive dá mais peso à erosão.")
    irrig = st.checkbox("Tenho rega no cacimbo", value=False)

# ───────────────────────── INDICADORES DO LOCAL ─────────────────────────
por_mes = df.groupby("mes").agg(chuva=("Chuva_mm", "mean"), umid=("Umidade_Solo_Idx", "mean"),
                                tmax=("Temp_Max_C", "mean"))
stats_ciclo = []
for c in CICLOS:
    sub = por_mes.reindex(c["meses"]).dropna()
    stats_ciclo.append(dict(chuva=sub["chuva"].mean() if len(sub) else np.nan,
                            umid=sub["umid"].mean() if len(sub) else np.nan,
                            tmax=sub["tmax"].mean() if len(sub) else np.nan))

cv_chuva = float(df["Chuva_mm"].std() / df["Chuva_mm"].mean()) if df["Chuva_mm"].mean() > 0 else 1.0
meses_quentes = int((df["Temp_Max_C"] >= 30).sum())
meses_secos = int((df["Umidade_Solo_Idx"] < 0.25).sum())
dist_km = haversine(coord, DADOS_REF)
SITE = dict(irrig=irrig, declive=declive, w_chuva=float(np.clip(cv_chuva, 0.3, 0.9)))

# ───────────────────────── MOTOR DE PONTUAÇÃO (transparente) ─────────────────────────
def criterios_cultura(chave, ci):
    """Notas 0–5 de uma cultura num ciclo, já ajustadas ao local."""
    c = CULTURAS[chave]
    f = 1.0
    if ci == 2 and not SITE["irrig"]:  # cacimbo sem rega: renda/mercado reduzem com a baixa tolerância à seca
        f = 0.3 + 0.7 * (c["seca"] - 1) / 4
    w = SITE["w_chuva"]
    return {
        "agua": c["agua"],
        "solo": (c["nfix"] + c["raizes"]) / 2,
        "erosao": c["erosao"],
        "renda": c["renda"] * f,
        "mercado": c["mercado"] * f,
        "chuvas": w * c["seca"] + (1 - w) * c["agua"],
        "calor": c["calor"],
    }


def pesos_efectivos():
    p = {k: float(v) for k, v in pesos.items()}
    p["erosao"] *= 1 + min(SITE["declive"], 20) / 40  # até +50% em declives ≥ 20 %
    if sum(p.values()) == 0:
        p = {k: 1.0 for k in p}
    return p


def avaliar(chaves, p=None):
    p = p or pesos_efectivos()
    por_ciclo = [criterios_cultura(k, i) for i, k in enumerate(chaves)]
    media = {k: float(np.mean([pc[k] for pc in por_ciclo])) for k in NOMES_CRIT}
    soma = sum(p.values())
    contrib = {k: media[k] * p[k] / soma * 20 for k in NOMES_CRIT}  # pontos (0–100 no total)
    return dict(media=media, contrib=contrib, total=sum(contrib.values()))


def estabilidade(rotacoes, n=400, seed=7):
    """% de simulações (pesos ±1) em que cada rotação fica em 1.º lugar."""
    rng = np.random.default_rng(seed)
    base, vitorias = pesos_efectivos(), np.zeros(len(rotacoes))
    for _ in range(n):
        p = {k: max(0.0, v + rng.integers(-1, 2)) for k, v in base.items()}
        if sum(p.values()) == 0:
            p = dict(base)
        sc = [avaliar(r, p)["total"] for r in rotacoes]
        vitorias[int(np.argmax(sc))] += 1
    return vitorias / n * 100


atual = ATUAIS[atual_nome]
rank_lib = sorted(((avaliar(v[1])["total"], k) for k, v in ESTRATEGIAS.items() if v[1] != atual), reverse=True)
alt_keys = [k for _, k in rank_lib[:2]]
OPCOES = [("ATUAL", atual_nome.split(" (")[0], atual)] + \
         [(f"ALTERNATIVA {l}", ESTRATEGIAS[k][0], ESTRATEGIAS[k][1]) for l, k in zip("AB", alt_keys)]
AVAL = [avaliar(o[2]) for o in OPCOES]
ESTAB = estabilidade([o[2] for o in OPCOES])
MELHOR = int(np.argmax([a["total"] for a in AVAL]))


def confianca():
    itens, pts = [], 0
    n = df["mes"].nunique()
    p_clima = 30 * (0.2 if DEMO else min(1, n / 12))
    pts += p_clima
    itens.append(("Clima/solo", p_clima, 30, "dados de demonstração" if DEMO else f"{n} meses distintos no cache"))
    p_loc = 25 * (1 if dist_km <= 15 else 0.6 if dist_km <= 60 else 0.3)
    pts += p_loc
    itens.append(("Local", p_loc, 25, f"a {dist_km:.0f} km do ponto dos dados (Huambo)"))
    p_nd = 20 * (1 if NDVI_REAL else 0.35)
    pts += p_nd
    itens.append(("NDVI", p_nd, 20, "série real" if NDVI_REAL else "apenas proxy a partir da humidade"))
    p_cul = 25 * 0.4
    pts += p_cul
    itens.append(("Tabela de culturas", p_cul, 25, "notas ainda por validar com fontes locais"))
    nivel = "Alta" if pts >= 75 else "Média" if pts >= 50 else "Baixa"
    return pts, nivel, itens


CONF_PTS, CONF_NIVEL, CONF_ITENS = confianca()
CONF_COR = {"Alta": ("#dff3e6", "#1f5c3f"), "Média": ("#fff1cc", "#8a5a00"), "Baixa": ("#fbe3d6", "#9a3d12")}[CONF_NIVEL]

# ───────────────────────── CABEÇALHO ─────────────────────────
st.markdown("""
<div class="hero">
  <div class="tag">🛰️ NASA SPACE APPS · EQUIPA ANGOPLANTA</div>
  <h1>RotaCampo: compare estratégias de rotação para a sua machamba</h1>
  <p>Escolha o local, indique a rotação que já usa e diga o que mais importa. Receba três estratégias
  lado a lado — com dados de satélite, contas à vista e os pontos que ainda precisam de confirmação.</p>
</div>
""", unsafe_allow_html=True)

if DEMO:
    st.markdown('<div class="nota">⚠️ <b>Dados de demonstração.</b> Não foi encontrado <code>cache_huambo.csv</code> '
                'ao lado do <code>app.py</code>. Os números abaixo servem só para ver a app a funcionar.</div>',
                unsafe_allow_html=True)
    st.write("")


def kpi(col, label, valor, desc):
    col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{valor}</div>'
                 f'<div class="d">{desc}</div></div>', unsafe_allow_html=True)


k = st.columns(5)
kpi(k[0], "📍 Local", local_sel.replace(PONTO_MAPA, "Ponto no mapa").split(" (")[0], f"{coord[0]:.3f}°, {coord[1]:.3f}°")
kpi(k[1], "🌧️ Chuva média", f"{df['Chuva_mm'].mean():.0f} mm", f"Variabilidade (CV) {cv_chuva:.2f}")
kpi(k[2], "💧 Meses secos", f"{meses_secos}", "umidade do solo < 0,25")
kpi(k[3], "🌡️ Meses ≥ 30 °C", f"{meses_quentes}", f"Máx. {df['Temp_Max_C'].max():.1f} °C")
k[4].markdown(f'<div class="kpi"><div class="l">🎯 Confiança</div><div class="v">{CONF_NIVEL}</div>'
              f'<div class="d">{CONF_PTS:.0f}/100 · ver detalhe em “Comparar”</div></div>', unsafe_allow_html=True)
st.write("")

# ───────────────────────── MAPA (passo 1) ─────────────────────────
with st.expander("🗺️ Passo 1 · Veja ou escolha o local no mapa", expanded=False):
    m = folium.Map(location=list(coord), zoom_start=10)
    folium.Marker(list(coord), tooltip="Sua lavra", icon=folium.Icon(color="green", icon="leaf")).add_to(m)
    folium.Circle(list(coord), radius=4000, color=VERDE, fill=True, fill_opacity=0.12).add_to(m)
    folium.Marker(list(DADOS_REF), tooltip="Ponto dos dados de satélite",
                  icon=folium.Icon(color="orange", icon="cloud")).add_to(m)
    if HAS_SF:
        st.caption("Clique no mapa para marcar a sua machamba.")
        out = st_folium(m, height=340, width=1100, returned_objects=["last_clicked"])
        lc = out.get("last_clicked") if out else None
        if lc:
            novo = (round(lc["lat"], 4), round(lc["lng"], 4))
            if st.session_state["clique"] != novo:
                st.session_state["clique"] = novo
                st.session_state["_pendente"] = PONTO_MAPA
                st.rerun()
    else:
        html(m._repr_html_(), height=340)
        st.info("Para clicar no mapa instale `streamlit-folium` (já incluído no requirements.txt). "
                "Por agora escolha o local na barra lateral.")

# ───────────────────────── ABAS ─────────────────────────
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "⚖️ Comparar estratégias", "🌦️ Clima & solo", "🛰️ NDVI & IA",
    "🌽 Culturas", "🎓 Formação & impacto", "ℹ️ Método"])

PLOT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
            font=dict(family="DM Sans", color=TINTA), margin=dict(l=10, r=10, t=50, b=10))


def ul(itens):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in itens) + "</ul>"


def blocos(idx):
    chaves, av = OPCOES[idx][2], AVAL[idx]
    cult = [CULTURAS[c] for c in chaves]
    evid, ben, lac, ris = [], [], [], []

    for i, (c, ch) in enumerate(zip(CICLOS, cult)):
        s = stats_ciclo[i]
        if np.isnan(s["chuva"]):
            evid.append(f"<b>{c['janela']} · {ch['nome']}</b>: sem dados no cache para este período.")
        else:
            evid.append(f"<b>{c['janela']} · {ch['nome']}</b>: chuva média {s['chuva']:.0f} mm, "
                        f"umidade do solo {s['umid']:.2f}, máx. {s['tmax']:.0f} °C.")
    evid.append(f"Tabela de culturas: azoto fixado {np.mean([c['nfix'] for c in cult]):.1f}/5 · "
                f"protecção contra erosão {np.mean([c['erosao'] for c in cult]):.1f}/5 · "
                f"tolerância à seca {np.mean([c['seca'] for c in cult]):.1f}/5.")

    top = sorted(NOMES_CRIT, key=lambda k_: av["contrib"][k_], reverse=True)
    for k_ in [t for t in top if pesos[t] > 0][:3]:
        melhor = max(range(3), key=lambda i: criterios_cultura(chaves[i], i)[k_])
        ben.append(f"{NOMES_CRIT[k_]}: nota média {av['media'][k_]:.1f}/5 (peso {pesos[k_]}). "
                   f"Destaque: {cult[melhor]['nome']}.")
    if not ben:
        ben.append("Defina pelo menos uma prioridade para ver os benefícios.")

    lac.append("Sem análise de solo da lavra (pH, matéria orgânica, textura).")
    if not NDVI_REAL:
        lac.append("NDVI real em falta — a série mostrada é um proxy da humidade do solo.")
    if dist_km > 15:
        lac.append(f"Clima de Huambo usado num ponto a {dist_km:.0f} km — pode diferir no seu local.")
    lac.append("Preços de mercado locais e custos de insumos não entram na pontuação.")
    lac.append("Notas das culturas ainda por confirmar com fontes locais (ver aba Culturas).")

    for i, (c, ch) in enumerate(zip(CICLOS, cult)):
        if i == 2 and not irrig and ch["seca"] <= 2 and chaves[i] != "pousio":
            ris.append(f"{ch['nome']} no cacimbo sem rega: tolerância à seca {ch['seca']}/5 — risco alto de perda.")
    if declive >= 8 and np.mean([c["erosao"] for c in cult]) < 3:
        ris.append(f"Declive de {declive}% com protecção contra erosão baixa ({np.mean([c['erosao'] for c in cult]):.1f}/5).")
    if meses_quentes >= 3 and any(c["calor"] <= 2 for c in cult):
        ris.append("Culturas sensíveis ao calor num local com vários meses ≥ 30 °C.")
    if cv_chuva > 0.8 and any(c["seca"] <= 2 for c in cult):
        ris.append(f"Chuva muito irregular (CV {cv_chuva:.2f}) e culturas pouco tolerantes à seca.")
    if len(set(chaves)) < len(chaves) and chaves[0] != "pousio":
        ris.append("Repetição da mesma cultura: aumenta pragas, doenças e desgaste do solo.")
    if sum(c["nfix"] <= 1 for c in cult) >= 2:
        ris.append("Duas ou mais culturas que gastam azoto sem leguminosa de reposição.")
    ris.append("<b>Validar com técnico local (extensionista / IIA) antes de decidir.</b>")
    return evid, ben, lac, ris


with aba1:
    st.markdown("### Três estratégias para a sua lavra")
    st.caption(f"{area_ha} ha · rotação actual: {atual_nome} · {'com' if irrig else 'sem'} rega · declive {declive}%")
    cols = st.columns(3, gap="medium")
    for i, col in enumerate(cols):
        papel, nome, chaves = OPCOES[i]
        sc = AVAL[i]["total"]
        cor = [TERRA, VERDE, OCRE][i]
        chips = "".join(
            f'<div class="chip"><span>{CICLOS[j]["nome"].upper()} · {CICLOS[j]["janela"]}</span>'
            f'{CULTURAS[ch]["e"]} <b>{CULTURAS[ch]["nome"]}</b></div>' for j, ch in enumerate(chaves))
        tag = '<div class="star">★ Melhor para as suas prioridades</div><br>' if i == MELHOR else ""
        col.markdown(
            f'<div class="scard {"best" if i == MELHOR else ""}">{tag}'
            f'<div class="role" style="color:{cor}">{papel}</div><div class="name">{nome}</div>'
            f'<div class="score">{sc:.0f}<small> / 100</small></div>'
            f'<div class="bar"><div style="width:{sc:.0f}%;background:{cor}"></div></div>'
            f'<div class="muted">Fica em 1.º em <b>{ESTAB[i]:.0f}%</b> das simulações com pequenas '
            f'variações nas prioridades.</div>{chips}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="muted" style="margin-top:.7rem">A pontuação mede o <b>ajuste às suas prioridades</b> '
        f'(0–100). Não é uma probabilidade de colheita. Confiança geral: '
        f'<span class="conf" style="background:{CONF_COR[0]};color:{CONF_COR[1]}">{CONF_NIVEL}</span></div>',
        unsafe_allow_html=True)

    st.write("")
    g1, g2 = st.columns(2, gap="large")
    nomes_curto = [f"{o[0].title()}: {o[1]}" for o in OPCOES]
    with g1:
        crit = list(NOMES_CRIT)
        fig = go.Figure()
        for i in range(3):
            v = [AVAL[i]["media"][c] for c in crit]
            fig.add_trace(go.Scatterpolar(r=v + v[:1], theta=[NOMES_CRIT[c] for c in crit] + [NOMES_CRIT[crit[0]]],
                                          name=OPCOES[i][0].title(), fill="toself", opacity=0.55,
                                          line=dict(color=CORES_EST[i], width=2)))
        fig.update_layout(title="Perfil de cada estratégia (nota 0–5)", polar=dict(radialaxis=dict(range=[0, 5])),
                          legend=dict(orientation="h", y=-0.08), height=420, **PLOT)
        grafico(fig)
    with g2:
        fig = go.Figure()
        paleta = [VERDE_ESC, FOLHA, "#8cc29d", OCRE, TERRA, "#6b8fb5", "#c9897a"]
        for c, cor in zip(crit, paleta):
            fig.add_trace(go.Bar(y=[o[0].title() for o in OPCOES][::-1], x=[a["contrib"][c] for a in AVAL][::-1],
                                 name=NOMES_CRIT[c], orientation="h", marker_color=cor,
                                 hovertemplate="%{x:.1f} pontos<extra>" + NOMES_CRIT[c] + "</extra>"))
        fig.update_layout(barmode="stack", title="De onde vem cada pontuação (pontos)",
                          xaxis=dict(range=[0, 100]), legend=dict(orientation="h", y=-0.25), height=420, **PLOT)
        grafico(fig)

    st.markdown("### O que saber de cada estratégia")
    esc = st.radio("Ver detalhe de:", range(3), horizontal=True,
                   format_func=lambda i: f"{OPCOES[i][0].title()} · {OPCOES[i][1]}", label_visibility="collapsed")
    ev, be, la, ri = blocos(esc)
    r1 = st.columns(2, gap="medium")
    r1[0].markdown(f'<div class="bloco b-evid"><h4>📊 Evidência</h4>{ul(ev)}</div>', unsafe_allow_html=True)
    r1[1].markdown(f'<div class="bloco b-ben"><h4>✅ Benefícios</h4>{ul(be)}</div>', unsafe_allow_html=True)
    st.write("")
    r2 = st.columns(2, gap="medium")
    r2[0].markdown(f'<div class="bloco b-lac"><h4>🔍 Lacunas de informação</h4>{ul(la)}</div>', unsafe_allow_html=True)
    r2[1].markdown(f'<div class="bloco b-ris"><h4>⚠️ Riscos — validar com técnico local</h4>{ul(ri)}</div>', unsafe_allow_html=True)

    st.write("")
    with st.expander("🎯 Porque é que a confiança é " + CONF_NIVEL.lower() + "?"):
        for nome_i, got, tot, why in CONF_ITENS:
            st.markdown(f"**{nome_i}** — {got:.0f}/{tot} pontos · {why}")
            st.progress(got / tot)
    with st.expander("🧮 Como a pontuação foi calculada (sem caixa preta)"):
        p = pesos_efectivos()
        linhas = []
        for c in crit:
            linha = {"Critério": NOMES_CRIT[c], "Peso (seu)": pesos[c], "Peso usado": round(p[c], 2)}
            for i in range(3):
                linha[f"Nota {OPCOES[i][0].title()}"] = round(AVAL[i]["media"][c], 2)
                linha[f"Pontos {OPCOES[i][0].title()}"] = round(AVAL[i]["contrib"][c], 1)
            linhas.append(linha)
        tabela(pd.DataFrame(linhas), hide_index=True)
        st.markdown(
            "**Fórmula:** pontos = nota média (0–5) × peso ÷ soma dos pesos × 20. Total = soma dos pontos.  \n"
            f"**Ajustes ao local:** (1) declive de {declive}% aumenta o peso da erosão em "
            f"{min(declive, 20) / 40 * 100:.0f}%; (2) sem rega, no Ciclo 3 renda e mercado são multiplicados por "
            "0,3 + 0,7 × (tolerância à seca − 1) ÷ 4; (3) “resistir a chuvas” mistura tolerância à seca e "
            f"eficiência hídrica com peso {SITE['w_chuva']:.2f} na seca (vem da variabilidade da chuva).")

# ───────────────────────── CLIMA & SOLO ─────────────────────────
with aba2:
    st.markdown("### Clima e solo lidos para decidir")
    st.caption("Dados de satélite agregados por mês e guardados em cache — a demonstração nunca depende de download ao vivo.")
    a, b = st.columns(2, gap="large")
    i_max, i_min = df["Chuva_mm"].idxmax(), df["Umidade_Solo_Idx"].idxmin()
    with a:
        fig = go.Figure(go.Bar(x=df["mes_label"], y=df["Chuva_mm"],
                               marker_color=[VERDE if e == "Época das chuvas" else TERRA for e in df["Estacao"]],
                               text=df["Chuva_mm"].round(1), textposition="outside"))
        fig.add_annotation(x=df.loc[i_max, "mes_label"], y=df.loc[i_max, "Chuva_mm"], showarrow=True, ax=0, ay=-45,
                           text=f"Pico: {df.loc[i_max, 'Chuva_mm']:.0f} mm", bgcolor="#e6f2ea", bordercolor=VERDE)
        fig.update_layout(title="Calendário de chuvas (mm)", yaxis=dict(range=[0, df["Chuva_mm"].max() * 1.3]),
                          showlegend=False, height=400, **PLOT)
        grafico(fig)
        st.markdown('<div class="explica"><b>Como ler:</b> barras <span style="color:#1f5c3f"><b>verdes</b></span> = '
                    'época das chuvas, boa para semear sem rega. Barras <span style="color:#b5651d"><b>castanhas</b></span> = '
                    'cacimbo: sem rega, prefira mandioca, feijão-frade ou cobertura.</div>', unsafe_allow_html=True)
    with b:
        fig = go.Figure()
        fig.add_hrect(y0=0.5, y1=1.2, fillcolor="#e6f2ea", opacity=.6, line_width=0,
                      annotation_text="Zona boa para germinar", annotation_position="top left")
        fig.add_hrect(y0=-0.05, y1=0.25, fillcolor="#fbe3d6", opacity=.6, line_width=0,
                      annotation_text="Solo seco", annotation_position="bottom left")
        fig.add_trace(go.Scatter(x=df["mes_label"], y=df["Umidade_Solo_Idx"], mode="lines+markers", name="Umidade a 5 cm",
                                 line=dict(color=VERDE, width=3)))
        fig.add_trace(go.Scatter(x=df["mes_label"], y=df["Temp_Max_C"] / 30, mode="lines", name="Calor (Tmax ÷ 30 °C)",
                                 line=dict(color=OCRE, width=2, dash="dash")))
        fig.add_annotation(x=df.loc[i_min, "mes_label"], y=df.loc[i_min, "Umidade_Solo_Idx"], showarrow=True, ax=0, ay=-50,
                           text="Mais seco", bgcolor="#fbe3d6", bordercolor=TERRA)
        fig.update_layout(title="Água na raiz vs. calor", yaxis=dict(range=[-0.1, 1.35], title="0 = seco · 1 = húmido"),
                          legend=dict(orientation="h", y=1.12), height=400, **PLOT)
        grafico(fig)
        st.markdown('<div class="explica"><b>Como ler:</b> a linha verde mostra se há água onde a semente germina. '
                    'Quando o calor (tracejado) sobe e o solo está na faixa vermelha, evite semear: espere as primeiras chuvas.</div>',
                    unsafe_allow_html=True)
    with st.expander("📄 Tabela de dados em cache"):
        tabela(df[["validdate", "mes_label", "Estacao", "Temp_Max_C", "Chuva_mm", "Umidade_Solo_Idx"]],
                hide_index=True)

# ───────────────────────── NDVI & IA ─────────────────────────
with aba3:
    st.markdown("### O papel da IA: estação de crescimento e campo vazio")
    if not NDVI_REAL:
        st.markdown('<div class="nota">ℹ️ O cache ainda não tem NDVI de satélite. A curva abaixo é um <b>proxy</b> '
                    '(a vegetação responde à humidade do solo com cerca de um mês de atraso). '
                    'Quando adicionar uma coluna <code>ndvi</code> ao CSV, a app passa a usá-la automaticamente.</div>',
                    unsafe_allow_html=True)
        st.write("")
    nd = df["NDVI"]
    lo, hi = nd.min(), nd.max()
    em_crescimento = nd >= lo + 0.5 * (hi - lo)
    vazio = nd <= lo + 0.25 * (hi - lo)
    c1, c2 = st.columns([1.5, 1], gap="large")
    with c1:
        fig = go.Figure(go.Scatter(x=df["mes_label"], y=nd, mode="lines+markers", fill="tozeroy",
                                   line=dict(color=FOLHA, width=3), fillcolor="rgba(63,143,95,.18)",
                                   name="NDVI" if NDVI_REAL else "NDVI (proxy)"))
        fig.add_hline(y=lo + 0.5 * (hi - lo), line_dash="dot", line_color=VERDE,
                      annotation_text="início/fim da estação de crescimento")
        fig.add_hline(y=lo + 0.25 * (hi - lo), line_dash="dot", line_color=TERRA,
                      annotation_text="campo vazio", annotation_position="bottom right")
        fig.update_layout(title="Ciclo anual de vegetação", yaxis=dict(range=[0, 1], title="NDVI"), height=380, **PLOT)
        grafico(fig)
    with c2:
        X = df[["Umidade_Solo_Idx", "Chuva_mm", "Temp_Max_C"]].to_numpy(float)
        Xz = (X - X.mean(0)) / np.where(X.std(0) == 0, 1, X.std(0))
        lab, cent = kmeans(Xz, 3)
        ordem = np.argsort(cent[:, 0])
        nomes_cl = {ordem[0]: "Seco", ordem[1]: "Transição", ordem[2]: "Chuvoso"}
        df["Grupo"] = [nomes_cl[l] for l in lab]
        cont = df["Grupo"].value_counts().reindex(["Seco", "Transição", "Chuvoso"]).fillna(0)
        fig = go.Figure(go.Bar(x=cont.index, y=cont.values, marker_color=[TERRA, OCRE, VERDE], text=cont.values.astype(int),
                               textposition="outside"))
        fig.update_layout(title="Meses agrupados pelo clima (k-means)", yaxis=dict(range=[0, cont.max() + 2]),
                          height=380, **PLOT)
        grafico(fig)

    ini = df.loc[em_crescimento, "mes_label"]
    st.markdown('<div class="explica"><b>Em palavras simples:</b> '
                f'a estação de crescimento detectada tem <b>{int(em_crescimento.sum())} meses</b>'
                f'{" (de " + ini.iloc[0] + " a " + ini.iloc[-1] + ")" if len(ini) else ""}; '
                f'o campo está “vazio” em <b>{int(vazio.sum())} meses</b>. '
                'O agrupamento junta meses parecidos (humidade, chuva, calor) sem regras manuais.</div>',
                unsafe_allow_html=True)

    anos = df.groupby("ano").agg(chuva=("Chuva_mm", "sum"), n=("mes", "nunique"))
    anos = anos[anos["n"] >= 10]
    if len(anos) >= 4:
        lab_a, cent_a = kmeans(((anos[["chuva"]] - anos["chuva"].mean()) / anos["chuva"].std()).to_numpy(), 2)
        seco = int(np.argmin(cent_a[:, 0]))
        anos["Tipo"] = ["Ano seco" if l == seco else "Ano normal" for l in lab_a]
        st.write("")
        st.markdown("**Anos secos vs. normais**")
        st.dataframe(anos[["chuva", "Tipo"]].round(0))
    else:
        st.caption("O agrupamento de anos secos e normais precisa de 4 ou mais anos completos no cache. "
                   "O código já está pronto: basta alargar o CSV.")

# ───────────────────────── CULTURAS ─────────────────────────
with aba4:
    st.markdown("### Tabela de culturas do projecto")
    st.markdown('<div class="nota">Notas de 1 a 5 (5 = melhor). Foram feitas pela equipa e <b>ainda não estão validadas</b>. '
                'Confirme culturas, épocas de plantio e dados de solo com fontes locais (IIA, extensionistas, produtores).</div>',
                unsafe_allow_html=True)
    st.write("")
    rot = {"agua": "Eficiência hídrica", "nfix": "Fixação de azoto", "raizes": "Raízes/estrutura do solo",
           "erosao": "Protecção contra erosão", "seca": "Tolerância à seca", "calor": "Tolerância ao calor",
           "mercado": "Mercado", "renda": "Renda"}
    tab = pd.DataFrame([{"Cultura": f"{c['e']} {c['nome']}", **{rot[k_]: c[k_] for k_ in rot},
                         "Ciclo (dias)": c["dias"], "Precisa rega": "Sim" if c["rega"] else "Não",
                         "Fonte": c["fonte"], "Validada": "Não"} for c in CULTURAS.values()])
    z = tab[[rot[k_] for k_ in rot]].to_numpy()
    fig = go.Figure(go.Heatmap(z=z, x=list(rot.values()), y=tab["Cultura"], zmin=1, zmax=5, text=z, texttemplate="%{text}",
                               colorscale=[[0, "#fbe3d6"], [0.5, "#fff1cc"], [1, "#3f8f5f"]], showscale=False))
    fig.update_layout(height=470, yaxis=dict(autorange="reversed"), xaxis=dict(side="top"), **PLOT)
    grafico(fig)
    with st.expander("Ver tabela completa com fontes"):
        tabela(tab, hide_index=True)

# ───────────────────────── FORMAÇÃO & IMPACTO ─────────────────────────
with aba5:
    st.markdown("### Mais do que uma app: conhecimento ao alcance do campo")
    st.markdown("O AngoPlanta quer aproximar a ciência e a tecnologia de agricultores, empreendedores e trabalhadores rurais, "
                "com formação simples e prática em cada passo da campanha.")
    st.markdown(f'<div class="kpi" style="margin:.6rem 0 1rem"><div class="l">🎯 Meta 2027–2028</div>'
                f'<div class="v">+1 000 agricultores</div><div class="d">com culturas e actividades diversas a usar '
                f'a plataforma, a cobrir todas as culturas e a resolver problemas reais com tecnologia moderna.</div></div>',
                unsafe_allow_html=True)
    mods = [("01", "Ler o calendário de chuvas", "Quando semear e quando esperar."),
            ("02", "Rotação de culturas", "Porque alternar cereais, leguminosas e tubérculos."),
            ("03", "Proteger o solo", "Cobertura, curvas de nível e menos erosão."),
            ("04", "Água e irrigação", "Regar menos e melhor no cacimbo."),
            ("05", "Pragas: sinais de alerta", "Reconhecer cedo e pedir ajuda técnica."),
            ("06", "Colheita e mercado", "Quando colher e como vender melhor.")]
    cm = st.columns(3, gap="medium")
    for i, (n, t, d) in enumerate(mods):
        cm[i % 3].markdown(f'<div class="modulo"><div class="n">{n}</div><b>{t}</b><br>'
                           f'<span class="muted">{d}</span></div>', unsafe_allow_html=True)
        if i % 3 == 2 and i < 5:
            cm = st.columns(3, gap="medium")
    st.write("")
    st.markdown("**No horizonte do projecto:** monitorizar solo e humidade por satélite, controlo de irrigação, "
                "prevenção de pragas e apoio à colheita. Os módulos acima são o plano de formação; "
                "ainda não estão publicados.")

# ───────────────────────── MÉTODO ─────────────────────────
with aba6:
    st.markdown("### Como o RotaCampo chega aos resultados")
    st.markdown("""
1. **Pipeline de dados:** descarrega uma área pequena, agrega por mês e guarda em cache local (`cache_huambo.csv`).
2. **Indicadores:** chuva e variabilidade, umidade do solo, ciclo anual de NDVI, meses de calor e declive.
3. **Tabela de culturas:** feita pela equipa, com fonte por cultura (por validar).
4. **Motor de pontuação:** cruza os indicadores do local com a tabela, ponderado pelas suas prioridades. Todas as contas são mostradas.
5. **Incerteza:** nível de confiança por componente e estabilidade do ranking em 400 simulações.
6. **IA simples:** proxy/série de NDVI para estação de crescimento e campo vazio; k-means para agrupar meses (e anos, quando houver dados).
7. **Interface:** Streamlit, mapa com folium e gráficos com plotly.
""")
    st.markdown('<div class="nota"><b>Limites:</b> a pontuação é um apoio à decisão, não uma previsão de colheita. '
                'Não substitui análise de solo nem aconselhamento técnico no terreno.</div>', unsafe_allow_html=True)

st.write("")
st.caption("RotaCampo · AngoPlanta · NASA Space Apps Challenge")
