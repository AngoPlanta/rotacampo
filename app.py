"""
RotaCampo · AngoPlanta
Compara estratégias de rotação de culturas para o Planalto Central de Angola (Huambo),
com dados de satélite em cache (NASA / Meteomatics) e as prioridades do agricultor.

Ficheiro de dados (opcional): cache_huambo.csv, separador ";" (ou ","),
colunas: validdate, t_max_2m_24h:C, precip_24h:mm, soil_moisture_index_-5cm:idx
Coluna opcional: qualquer coluna com "ndvi" no nome.
Sem o ficheiro, a app usa dados de DEMONSTRAÇÃO e avisa o utilizador. Nunca falha por falta de dados.
"""
import itertools
import math
from pathlib import Path

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from streamlit_folium import st_folium
    TEM_ST_FOLIUM = True
except Exception:
    TEM_ST_FOLIUM = False

st.set_page_config(
    page_title="RotaCampo · AngoPlanta",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# 1. CONSTANTES
# ============================================================================
REF_LAT, REF_LON = -12.7761, 15.7392  # Huambo: ponto dos dados em cache
MESES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
HERO_IMG = "https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=1600&auto=format&fit=crop"

# Tabela de culturas (valores qualitativos 1–5; 5 = melhor para o critério,
# exceto "exig_n", que é a exigência de azoto: 5 = exige muito).
# ATENÇÃO: valores iniciais da equipa, a confirmar com fontes locais (IIAM, extensionistas).
CULTURAS = {
    "Milho": dict(emoji="🌽", grupo="Cereal", leguminosa=False, agua=2, n=1, exig_n=4, raizes=3, erosao=3,
                  ciclo=120, seca=2, mercado=5, fonte="FAO EcoCrop; IIAM (a confirmar)"),
    "Feijão": dict(emoji="🫘", grupo="Leguminosa", leguminosa=True, agua=3, n=4, exig_n=1, raizes=2, erosao=3,
                   ciclo=90, seca=2, mercado=4, fonte="FAO EcoCrop; IIAM (a confirmar)"),
    "Amendoim": dict(emoji="🥜", grupo="Leguminosa", leguminosa=True, agua=3, n=4, exig_n=1, raizes=3, erosao=4,
                     ciclo=110, seca=3, mercado=4, fonte="FAO EcoCrop; IIAM (a confirmar)"),
    "Mandioca": dict(emoji="🍠", grupo="Raiz", leguminosa=False, agua=4, n=1, exig_n=2, raizes=5, erosao=3,
                     ciclo=300, seca=5, mercado=3, fonte="FAO EcoCrop; IIAM (a confirmar)"),
    "Batata-doce": dict(emoji="🥔", grupo="Raiz", leguminosa=False, agua=3, n=1, exig_n=2, raizes=4, erosao=5,
                        ciclo=120, seca=3, mercado=3, fonte="FAO EcoCrop; IIAM (a confirmar)"),
}
TABELA_CONFIRMADA = False

CRITERIOS = {
    "agua": "Poupar água",
    "solo": "Melhorar o solo",
    "erosao": "Reduzir a erosão",
    "renda": "Renda extra",
    "mercado": "Mercado",
    "clima": "Chuvas e calor",
}

PERFIS = {
    "Personalizado": None,
    "Poupar água": dict(agua=5, solo=2, erosao=2, renda=2, mercado=2, clima=5),
    "Recuperar a terra": dict(agua=2, solo=5, erosao=5, renda=1, mercado=1, clima=3),
    "Vender mais": dict(agua=2, solo=2, erosao=1, renda=5, mercado=5, clima=3),
    "Comida para a família": dict(agua=3, solo=4, erosao=3, renda=2, mercado=2, clima=4),
}

JANELAS = [
    dict(nome="Ciclo 1", periodo="Out–Jan", fase="Época chuvosa", meses=[10, 11, 12, 1], dias=122),
    dict(nome="Ciclo 2", periodo="Fev–Mai", fase="Chuvas tardias", meses=[2, 3, 4, 5], dias=120),
    dict(nome="Ciclo 3", periodo="Jun–Set", fase="Cacimbo (seca)", meses=[6, 7, 8, 9], dias=122),
]

COR_VERDE, COR_TERRA, COR_CINZA = "#21462d", "#9a4a26", "#7a6c5d"

# ============================================================================
# 2. ESTILO (Corrigido para evitar sobreposições e alinhar blocos)
# ============================================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700&family=Public+Sans:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Public Sans', sans-serif; }
h1, h2, h3, h4, .rc-display { font-family: 'Bricolage Grotesque', sans-serif !important; letter-spacing: -0.01em; }
.stApp { background: #f6f3ee; color: #26211c; }
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1280px; }
section[data-testid="stSidebar"] { background: #fffdf9; border-right: 1px solid #e6dccd; }
footer { visibility: hidden; }

/* Cabeçalho */
.rc-hero {
  background: linear-gradient(115deg, rgba(34,22,14,.90) 0%, rgba(33,70,45,.84) 100%), url('__HERO__');
  background-size: cover; background-position: center;
  border-radius: 8px; padding: 2.2rem 2.2rem 1.8rem; color: #fff; margin-bottom: 1.1rem;
}
.rc-hero .origem { color: #e7b894; font-weight: 600; font-size: .9rem; margin-bottom: .5rem; }
.rc-hero h1 { font-size: 2.4rem; margin: 0 0 .5rem 0; color: #fff; line-height: 1.15; }
.rc-hero p { max-width: 780px; margin: 0 0 1rem 0; line-height: 1.55; color: #f1e6d6; font-size: 1.02rem; }
.rc-passos { display: flex; flex-wrap: wrap; gap: .5rem; }
.rc-passos span { background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25);
  border-radius: 999px; padding: .3rem .85rem; font-size: .88rem; color: #fff; }

/* Indicadores */
.rc-stat { border-left: 4px solid #9a4a26; background: #fffdf9; padding: .75rem 1rem;
  border-radius: 0 6px 6px 0; height: 100%; }
.rc-stat .rotulo { display: block; font-size: .82rem; color: #7a6c5d; font-weight: 600; }
.rc-stat b { display: block; font-size: 1.5rem; color: #21462d; font-family: 'Bricolage Grotesque', sans-serif; line-height: 1.25; }
.rc-stat .nota { font-size: .82rem; color: #5b4f43; }

/* Recomendação */
.rc-resumo { background: #21462d; color: #fff; border-radius: 8px; padding: 1.1rem 1.4rem; margin: .4rem 0 1rem; }
.rc-resumo b { color: #ffd9b8; }
.rc-resumo p { margin: 0; line-height: 1.55; font-size: 1.02rem; }

/* Estratégias */
.rc-estrategia { background: #fffdf9; border: 1px solid #e6dccd; border-radius: 8px; padding: 1rem 1.2rem; height: 100%; }
.rc-estrategia.destaque { border: 2px solid #21462d; }
.rc-estrategia h4 { margin: 0 0 .3rem 0; font-size: 1.05rem; }
.rc-nota { font-family: 'Bricolage Grotesque', sans-serif; font-size: 2.5rem; font-weight: 700; color: #21462d; line-height: 1; }
.rc-nota small { font-size: 1rem; color: #7a6c5d; font-weight: 500; }
.rc-seq { font-size: 1rem; margin: .6rem 0; line-height: 1.7; }
.rc-conf { display: inline-block; padding: .15rem .7rem; border-radius: 999px; font-size: .82rem; font-weight: 600; }
.rc-conf.Alta { background: #dcefe0; color: #1b5e2f; }
.rc-conf.Média { background: #fbeccb; color: #7a5200; }
.rc-conf.Baixa { background: #f6d9d2; color: #8a2a14; }

/* Ciclos */
.rc-ciclo { background: #fffdf9; border: 1px solid #e6dccd; border-radius: 8px; padding: .9rem 1.1rem; height: 100%; }
.rc-ciclo .fase { font-size: .86rem; color: #9a4a26; font-weight: 600; }
.rc-ciclo .cultura { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.3rem; font-weight: 700; margin: .1rem 0 .3rem 0; }
.rc-ciclo p { font-size: .9rem; color: #4a3f35; margin: 0; line-height: 1.5; }

/* Quatro blocos - Ajustados para evitar sobreposições */
.rc-bloco { border-radius: 8px; padding: 1rem 1.15rem; height: 100%; font-size: .92rem; line-height: 1.55; color: #26211c; margin-bottom: 0.8rem; }
.rc-bloco h5 { margin: 0 0 .4rem 0; font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.05rem; }
.rc-bloco ul { margin: 0; padding-left: 1.1rem; }
.rc-bloco li { margin-bottom: .3rem; }
.rc-evid { background: #e6efe8; border: 1px solid #cce2d1; } 
.rc-ben { background: #eef3dc; border: 1px solid #dbe6b8; }
.rc-lac { background: #fbf0d6; border: 1px solid #f2dec5; } 
.rc-risc { background: #f6e1da; border: 1px solid #ebc6bc; }

/* Diagnóstico */
.rc-diag { background: #fffdf9; border: 1px solid #e6dccd; border-left: 5px solid #7a6c5d; border-radius: 0 8px 8px 0;
  padding: .7rem 1rem; margin-bottom: .55rem; font-size: .93rem; line-height: 1.5; }
.rc-diag b { display: block; margin-bottom: .1rem; }
.rc-diag.ok { border-left-color: #2e7d46; } .rc-diag.alerta { border-left-color: #c77d2e; }
.rc-diag.perigo { border-left-color: #b3361b; } .rc-diag.info { border-left-color: #4a7a9a; }

/* Explicação dos gráficos */
.rc-explica { background: #fffdf9; border-left: 4px solid #21462d; padding: .75rem 1rem; font-size: .9rem;
  line-height: 1.5; margin-top: .6rem; margin-bottom: 1rem; border-radius: 0 6px 6px 0; }

/* Telemóvel */
@media (max-width: 640px) {
  .block-container { padding: .8rem .7rem 3rem; }
  .rc-hero { padding: 1.3rem 1.1rem; }
  .rc-hero h1 { font-size: 1.65rem; }
  .rc-hero p { font-size: .95rem; }
  .rc-nota { font-size: 2.1rem; }
  .rc-stat b { font-size: 1.25rem; }
  div[data-baseweb="tab-list"] { overflow-x: auto; flex-wrap: nowrap; }
  div[data-baseweb="tab-list"] button { white-space: nowrap; }
}
</style>
""".replace("__HERO__", HERO_IMG)
st.markdown(CSS, unsafe_allow_html=True)


def compact(texto):
    return " ".join(linha.strip() for linha in texto.splitlines() if linha.strip())


def html(texto):
    st.markdown(compact(texto), unsafe_allow_html=True)


def mostrar(fig, altura=None):
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10), paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Public Sans, sans-serif", color="#26211c"))
    if altura:
        fig.update_layout(height=altura)
    try:
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def tabela(dados):
    try:
        st.dataframe(dados, width="stretch", hide_index=True)
    except TypeError:
        st.dataframe(dados, use_container_width=True, hide_index=True)


def fmt(valor, sufixo="", casas=1):
    return "sem dado" if valor is None or pd.isna(valor) else f"{valor:.{casas}f}{sufixo}"


html("""
<div class="rc-hero">
  <div class="origem">AngoPlanta · NASA Space Apps Challenge</div>
  <h1>RotaCampo: que rotação serve melhor a sua machamba?</h1>
  <p>Compare três estratégias de rotação de culturas no Planalto Central de Angola, com dados de satélite
  e as suas prioridades. Cada resultado mostra o que sabemos, o que falta saber e o que deve confirmar com um técnico local.</p>
  <div class="rc-passos"><span>1 · Escolha o local no mapa</span><span>2 · Indique a rotação atual</span>
  <span>3 · Defina as prioridades</span><span>4 · Compare as estratégias</span></div>
</div>
""")


# ============================================================================
# 3. DADOS (Arquitetura Híbrida: API/Rede com Fallback Resiliente para Cache)
# ============================================================================
def _dados_demo():
    """Dados de DEMONSTRAÇÃO (fallback final), só para a app nunca falhar."""
    return pd.DataFrame({
        "validdate": pd.date_range("2025-01-01", periods=12, freq="MS"),
        "Chuva_mm": [200, 190, 220, 120, 10, 0, 0, 3, 40, 110, 190, 210],
        "Umidade_Solo_Idx": [0.90, 0.95, 1.00, 0.85, 0.35, 0.10, 0.05, 0.05, 0.10, 0.50, 0.80, 0.90],
        "Temp_Max_C": [25, 25, 25, 25, 26, 25, 25, 27, 29, 27, 25, 24],
        "ndvi": [0.76, 0.81, 0.83, 0.74, 0.55, 0.38, 0.29, 0.24, 0.27, 0.44, 0.62, 0.72]
    })


def _ler_csv():
    candidatos = [Path("cache_huambo.csv")]
    try:
        candidatos.append(Path(__file__).parent / "cache_huambo.csv")
    except NameError:
        pass
    for caminho in candidatos:
        if caminho.exists():
            for sep in (";", ","):
                try:
                    bruto = pd.read_csv(caminho, sep=sep)
                    if bruto.shape[1] > 1 and len(bruto) > 0:
                        return bruto
                except Exception:
                    continue
    return None


def _normalizar(bruto):
    mapa = {}
    for col in bruto.columns:
        nome = str(col).lower().strip()
        if "t_max" in nome or "temp" in nome:
            mapa[col] = "Temp_Max_C"
        elif "precip" in nome or "chuva" in nome:
            mapa[col] = "Chuva_mm"
        elif "soil" in nome or "umid" in nome or "humid" in nome:
            mapa[col] = "Umidade_Solo_Idx"
        elif "validdate" in nome or "data_validada" in nome or nome in ("date", "data"):
            mapa[col] = "validdate"
        elif "ndvi" in nome:
            mapa[col] = "ndvi"

    df_ = bruto.rename(columns=mapa)
    if not {"validdate", "Temp_Max_C", "Chuva_mm", "Umidade_Solo_Idx"}.issubset(df_.columns):
        return None
    df_ = df_.loc[:, ~df_.columns.duplicated()].copy()
    df_["validdate"] = pd.to_datetime(df_["validdate"], errors="coerce", utc=True).dt.tz_localize(None)
    
    # Garantir conversão numérica mesmo se houver vírgula decimal
    for col in ("Temp_Max_C", "Chuva_mm", "Umidade_Solo_Idx"):
        df_[col] = pd.to_numeric(df_[col].astype(str).str.replace(",", "."), errors="coerce")
        
    if "ndvi" in df_.columns:
        df_["ndvi"] = pd.to_numeric(df_["ndvi"].astype(str).str.replace(",", "."), errors="coerce")

    df_ = df_.dropna(subset=["validdate"]).sort_values("validdate").reset_index(drop=True)
    if len(df_) < 3 or df_[["Temp_Max_C", "Chuva_mm", "Umidade_Solo_Idx"]].isna().all().any():
        return None
    return df_


@st.cache_data(show_spinner=False)
def carregar_dados():
    df_, demo = None, False
    try:
        bruto = _ler_csv()
        df_ = _normalizar(bruto) if bruto is not None else None
    except Exception:
        df_ = None
    if df_ is None:
        df_, demo = _dados_demo(), True
    df_["mes"] = df_["validdate"].dt.month
    df_["ano"] = df_["validdate"].dt.year
    df_["mes_label"] = [f"{MESES_PT[m - 1]}/{str(a)[2:]}" for m, a in zip(df_["mes"], df_["ano"])]
    return df_, demo


def agrupar_estacoes(d):
    X = d[["Chuva_mm", "Umidade_Solo_Idx"]].apply(lambda c: c.fillna(c.median())).to_numpy(dtype=float)
    desvio = X.std(axis=0)
    desvio[desvio == 0] = 1
    Z = (X - X.mean(axis=0)) / desvio
    centros = np.array([Z[Z[:, 0].argmin()], Z[Z[:, 0].argmax()]])
    rot = np.zeros(len(Z), dtype=int)
    for _ in range(30):
        dist = ((Z[:, None, :] - centros[None, :, :]) ** 2).sum(axis=2)
        rot = dist.argmin(axis=1)
        novos = np.array([Z[rot == k].mean(axis=0) if (rot == k).any() else centros[k] for k in range(2)])
        if np.allclose(novos, centros):
            break
        centros = novos
    chuvoso = int(np.argmax(centros[:, 0]))
    return np.where(rot == chuvoso, "Época das chuvas", "Cacimbo (seca)")


df, USA_DEMO = carregar_dados()
df = df.copy()
df["Estacao"] = agrupar_estacoes(df)

# Detetar a coluna NDVI no DataFrame, limpando quaisquer espaços em branco
    COL_NDVI = next((c for c in df.columns if "ndvi" in str(c).lower().strip()), None)
    if COL_NDVI:
        if COL_NDVI != "ndvi":
            df = df.rename(columns={COL_NDVI: "ndvi"})
        COL_NDVI = "ndvi"
        # Substitui a vírgula por ponto para aceitar o formato decimal do CSV
        df[COL_NDVI] = pd.to_numeric(df[COL_NDVI].astype(str).str.replace(",", "."), errors="coerce")
        if df[COL_NDVI].isna().all():
            COL_NDVI = None

clima_mes = df.groupby("mes")[["Chuva_mm", "Umidade_Solo_Idx", "Temp_Max_C"]].mean().reindex(range(1, 13))

if USA_DEMO:
    st.warning("**Dados de demonstração.** Não encontrei um `cache_huambo.csv` válido, por isso os valores de clima abaixo "
               "**não são reais**. Coloque o ficheiro na mesma pasta do `app.py` para ver os dados de satélite.")
else:
    st.toast("🛰️ Dados de satélite (NASA / Meteomatics) e NDVI carregados com sucesso via cache resiliente.", icon="✅")


# ============================================================================
# 4. MOTOR DE PONTUAÇÃO (transparente, sem caixa preta)
# ============================================================================
def distancia_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(a))


def classe_humidade(v):
    if v is None or pd.isna(v):
        return "sem dado"
    return "seco" if v < 0.25 else "moderado" if v < 0.5 else "bom para germinar"


def indicadores_janela(janela, irrigacao):
    sub = clima_mes.loc[janela["meses"]]
    cobertura = float(sub.notna().all(axis=1).mean())
    base = sub if cobertura > 0 else clima_mes
    chuva, umid, tmax = (float(np.nanmean(base[c])) if base[c].notna().any() else 0.5
                         for c in ("Chuva_mm", "Umidade_Solo_Idx", "Temp_Max_C"))
    if irrigacao and umid < 0.6:
        umid = umid + (0.6 - umid) * 0.7
    return dict(chuva=chuva, umid=umid, tmax=tmax, cobertura=cobertura, dias=janela["dias"])


def ajuste_janela(c, j):
    secura = 1 - min(max(j["umid"] / 0.6, 0), 1)
    fit = 1 - secura * (1 - c["seca"] / 5)
    calor = min(max((j["tmax"] - 28) / 4, 0), 1)
    fit -= calor * 0.15 * (1 - c["seca"] / 5)
    if c["ciclo"] > j["dias"]:
        fit *= 0.85
    return max(fit, 0.05)


def criterios_cultura(c, fit):
    return {
        "agua": c["agua"] / 5,
        "solo": (c["n"] + c["raizes"]) / 10,
        "erosao": c["erosao"] / 5,
        "renda": (c["mercado"] + (5 if c["ciclo"] <= 100 else 3 if c["ciclo"] <= 130 else 1)) / 10,
        "mercado": c["mercado"] / 5,
        "clima": 0.5 * c["seca"] / 5 + 0.5 * fit,
    }


def avaliar(seq, janelas, pesos):
    soma = sum(pesos.values()) or 1
    ciclos, medios = [], {k: [] for k in CRITERIOS}
    for i, nome in enumerate(seq):
        c, j = CULTURAS[nome], janelas[i]
        anterior = seq[i - 1]
        fit = ajuste_janela(c, j)
        crit = criterios_cultura(c, fit)
        base = sum(pesos[k] * crit[k] for k in pesos) / soma
        rot, notas = 0.0, []
        if nome == anterior:
            rot -= 0.12
            notas.append("repete a cultura do ciclo anterior")
        elif c["leguminosa"] and not CULTURAS[anterior]["leguminosa"]:
            rot += 0.06
            notas.append(f"leguminosa depois de {anterior}: devolve azoto ao solo")
        for k in CRITERIOS:
            medios[k].append(crit[k])
        ciclos.append(dict(cultura=nome, fit=fit, crit=crit, pontos=base * (0.5 + 0.5 * fit) + rot, notas=notas))
    diversidade = 0.03 * (len(set(seq)) - 1)
    score = float(np.clip((np.mean([c["pontos"] for c in ciclos]) + diversidade) * 100, 0, 100))
    return dict(seq=tuple(seq), score=score, ciclos=ciclos, medios={k: float(np.mean(v)) * 100 for k, v in medios.items()})


def confianca(dist_km, janelas, fits_min, folga):
    cobertura = float(np.mean([j["cobertura"] for j in janelas]))
    n_meses = df[["ano", "mes"]].drop_duplicates().shape[0]
    pts = 0.35 * cobertura + 0.25 * min(n_meses / 12, 1)
    pts += 0.25 * (1 if dist_km <= 50 else 0.6 if dist_km <= 150 else 0.2)
    pts += 0.15 * (1 if COL_NDVI else 0)
    motivos = []
    if USA_DEMO:
        pts = min(pts, 0.3)
        motivos.append("os dados de clima são de demonstração")
    if dist_km > 50:
        motivos.append(f"o local está a {dist_km:.0f} km dos dados de satélite")
    if cobertura < 1:
        motivos.append("faltam meses de dados em algum ciclo")
    if not COL_NDVI:
        motivos.append("sem NDVI para confirmar a estação de crescimento")
    if fits_min < 0.5:
        pts -= 0.10
        motivos.append("uma das culturas está mal adaptada ao clima do seu ciclo")
    if folga < 3:
        pts -= 0.05
        motivos.append("a pontuação é muito próxima da de outra estratégia")
    if not TABELA_CONFIRMADA:
        pts = min(pts, 0.74)
        motivos.append("a tabela de culturas ainda não foi confirmada com fontes locais")
    nivel = "Alta" if pts >= 0.75 else "Média" if pts >= 0.5 else "Baixa"
    return nivel, pts, motivos


def diagnostico_lavra(rot, janelas, irrigacao):
    itens = []
    cs = [CULTURAS[c] for c in rot]
    balanco = sum(c["n"] - c["exig_n"] for c in cs)
    n_leg = sum(c["leguminosa"] for c in cs)
    if balanco <= -3:
        itens.append(("perigo", "Azoto: a terra perde mais do que recebe",
                      f"A rotação ({' → '.join(rot)}) gasta azoto e quase não o devolve (balanço {balanco:+d}). "
                      "Sem adubo, a produtividade tende a cair de ano para ano. Uma leguminosa (feijão ou amendoim) ajuda a repor."))
    elif balanco >= 3:
        itens.append(("ok", "Azoto: a terra é recompensada",
                      f"As leguminosas devolvem azoto ao solo (balanço {balanco:+d}). É bom momento para culturas que exigem mais, como o milho."))
    else:
        itens.append(("info", "Azoto: equilíbrio razoável",
                      f"O que a rotação gasta e devolve de azoto está próximo (balanço {balanco:+d}). Vigie o crescimento do milho, que é o mais exigente."))
    if n_leg == 0:
        itens.append(("alerta", "Sem leguminosas",
                      "Nenhum ciclo tem feijão ou amendoim. Incluir uma leguminosa reduz a necessidade de adubo e quebra ciclos de pragas."))
    repetidas = [(rot[i - 1], rot[i]) for i in range(3) if rot[i] == rot[i - 1]]
    if repetidas:
        itens.append(("perigo", "Cultura repetida em ciclos seguidos",
                      f"{repetidas[0][0]} aparece em ciclos seguidos. Isso favorece pragas e doenças do solo e esgota sempre os mesmos nutrientes."))
    for i, nome in enumerate(rot):
        if nome == "Milho" and CULTURAS[rot[i - 1]]["leguminosa"]:
            itens.append(("ok", "Boa ordem: milho depois de leguminosa",
                          f"O milho no {JANELAS[i]['nome']} aproveita o azoto deixado por {rot[i - 1]}."))
            break
    media_erosao = np.mean([c["erosao"] for c in cs])
    if media_erosao <= 2.7:
        itens.append(("alerta", "Pouca cobertura contra a erosão",
                      "As culturas escolhidas protegem pouco o solo das chuvas fortes. Considere batata-doce ou amendoim, que cobrem melhor a terra."))
    elif media_erosao >= 3.8:
        itens.append(("ok", "Boa proteção contra a erosão",
                      "A rotação mantém o solo bem coberto, o que ajuda a reter terra e água."))
    fit3 = ajuste_janela(cs[2], janelas[2])
    if fit3 < 0.6 and not irrigacao:
        itens.append(("alerta", f"{rot[2]} sofre no cacimbo",
                      f"No ciclo 3 (Jun–Set) o solo tem humidade {janelas[2]['umid']:.2f} ({classe_humidade(janelas[2]['umid'])}). "
                      "Sem rega, escolha uma cultura tolerante à seca, como a mandioca."))
    if len(set(rot)) == 3:
        itens.append(("ok", "Boa diversidade", "Três culturas diferentes espalham o risco de pragas e de mau tempo."))
    elif len(set(rot)) == 1:
        itens.append(("perigo", "Monocultura", "Com uma só cultura o risco de perder a colheita é muito maior."))
    if "Mandioca" in rot:
        itens.append(("info", "A mandioca ocupa a terra por muito tempo",
                      "A mandioca demora cerca de 10 meses e fica na terra mais do que um ciclo. Conte com isso no seu calendário."))
    return itens


# ============================================================================
# 5. PASSO 1 · LOCAL NO MAPA
# ============================================================================
st.session_state.setdefault("lat", REF_LAT)
st.session_state.setdefault("lon", REF_LON)

with st.expander("📍 Passo 1 · Escolha o local da sua machamba (clique no mapa)", expanded=True):
    if TEM_ST_FOLIUM:
        try:
            mapa = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=9, tiles="OpenStreetMap")
            folium.Marker([REF_LAT, REF_LON], tooltip="Ponto dos dados de satélite (Huambo)",
                          icon=folium.Icon(color="darkred", icon="signal")).add_to(mapa)
            folium.Marker([st.session_state.lat, st.session_state.lon], tooltip="A sua machamba",
                          icon=folium.Icon(color="green", icon="leaf")).add_to(mapa)
            try:
                saida = st_folium(mapa, height=340, use_container_width=True, returned_objects=["last_clicked"])
            except TypeError:
                saida = st_folium(mapa, height=340, width=700, returned_objects=["last_clicked"])
            clique = (saida or {}).get("last_clicked")
            if clique and (abs(clique["lat"] - st.session_state.lat) > 1e-6 or abs(clique["lng"] - st.session_state.lon) > 1e-6):
                st.session_state.lat, st.session_state.lon = clique["lat"], clique["lng"]
                st.rerun()
        except Exception:
            st.info("Não consegui mostrar o mapa agora. Escreva as coordenadas abaixo.")
            TEM_ST_FOLIUM = False
    if not TEM_ST_FOLIUM:
        ca, cb = st.columns(2)
        st.session_state.lat = ca.number_input("Latitude", value=float(st.session_state.lat), format="%.4f")
        st.session_state.lon = cb.number_input("Longitude", value=float(st.session_state.lon), format="%.4f")
    if st.button("Voltar ao Huambo"):
        st.session_state.lat, st.session_state.lon = REF_LAT, REF_LON
        st.rerun()

LAT, LON = float(st.session_state.lat), float(st.session_state.lon)
DIST = distancia_km(LAT, LON, REF_LAT, REF_LON)

# ============================================================================
# 6. SIDEBAR · ROTAÇÃO E PRIORIDADES
# ============================================================================
lista_culturas = list(CULTURAS)
for k in CRITERIOS:
    st.session_state.setdefault(f"peso_{k}", 3)


def aplicar_perfil():
    perfil = PERFIS.get(st.session_state.get("perfil"))
    if perfil:
        for chave, valor in perfil.items():
            st.session_state[f"peso_{chave}"] = valor


st.sidebar.markdown("### Passo 2 · A sua rotação atual")
area_ha = st.sidebar.slider("Área cultivada (hectares)", 0.5, 50.0, 2.5, step=0.5)
rot_atual = [
    st.sidebar.selectbox("Ciclo 1 (Out–Jan)", lista_culturas, index=0),
    st.sidebar.selectbox("Ciclo 2 (Fev–Mai)", lista_culturas, index=4),
    st.sidebar.selectbox("Ciclo 3 (Jun–Set)", lista_culturas, index=3),
]
irrigacao = st.sidebar.checkbox("Tenho rega no cacimbo", value=False)

st.sidebar.markdown("### Passo 3 · As suas prioridades")
st.sidebar.selectbox("Perfil rápido", list(PERFIS), key="perfil", on_change=aplicar_perfil)
st.sidebar.caption("0 = não importa · 5 = muito importante")
pesos = {k: st.sidebar.slider(nome, 0, 5, key=f"peso_{k}") for k, nome in CRITERIOS.items()}
if sum(pesos.values()) == 0:
    st.sidebar.warning("Todas as prioridades estão a zero. Usei o mesmo peso para todas.")
    pesos = {k: 1 for k in CRITERIOS}

# ============================================================================
# 7. CÁLCULO DAS 3 ESTRATÉGIAS
# ============================================================================
janelas = [indicadores_janela(j, irrigacao) for j in JANELAS]
atual = avaliar(rot_atual, janelas, pesos)
todas = sorted((avaliar(s, janelas, pesos) for s in itertools.product(lista_culturas, repeat=3)),
               key=lambda r: r["score"], reverse=True)
candidatas = [r for r in todas if r["seq"] != atual["seq"]]
alt1 = candidatas[0]
alt2 = next((r for r in candidatas[1:] if sum(a != b for a, b in zip(r["seq"], alt1["seq"])) >= 2), candidatas[1])
estrategias = [("A sua rotação atual", atual),
               ("Alternativa 1 · melhor para as suas prioridades", alt1),
               ("Alternativa 2 · diversificada", alt2)]
melhor_score = max(e["score"] for _, e in estrategias)
for _, e in estrategias:
    outros = sorted((x["score"] for _, x in estrategias if x is not e), reverse=True)
    e["folga"] = abs(e["score"] - outros[0])
    e["conf"], e["conf_pts"], e["conf_motivos"] = confianca(DIST, janelas, min(c["fit"] for c in e["ciclos"]), e["folga"])

# ============================================================================
# 8. INDICADORES DO LOCAL
# ============================================================================
try:
    mes_calor = MESES_PT[int(clima_mes["Temp_Max_C"].idxmax()) - 1]
    mes_chuva = MESES_PT[int(clima_mes["Chuva_mm"].idxmax()) - 1]
except Exception:
    mes_calor = mes_chuva = "—"
umid_media = df["Umidade_Solo_Idx"].mean()

k1, k2, k3, k4 = st.columns(4)
with k1:
    html(f"""<div class="rc-stat"><span class="rotulo">Local escolhido</span><b>{LAT:.3f}°, {LON:.3f}°</b>
    <span class="nota">A {DIST:.0f} km do ponto com dados de satélite</span></div>""")
with k2:
    html(f"""<div class="rc-stat"><span class="rotulo">Calor máximo</span><b>{fmt(clima_mes['Temp_Max_C'].max(), ' °C')}</b>
    <span class="nota">Mês mais quente: {mes_calor}</span></div>""")
with k3:
    html(f"""<div class="rc-stat"><span class="rotulo">Chuva máxima</span><b>{fmt(clima_mes['Chuva_mm'].max(), ' mm')}</b>
    <span class="nota">Mês mais chuvoso: {mes_chuva}</span></div>""")
with k4:
    html(f"""<div class="rc-stat"><span class="rotulo">Humidade do solo (média)</span><b>{fmt(umid_media, '', 2)}</b>
    <span class="nota">Escala de 0 (seco) a 1 (húmido): {classe_humidade(umid_media)}</span></div>""")
st.caption("Fonte: dados de satélite em cache (NASA / Meteomatics), um valor por mês. "
           f"Área da machamba: {area_ha:g} ha.")

if DIST > 150:
    st.warning(f"A sua machamba está a {DIST:.0f} km do ponto onde temos dados. O clima pode ser bem diferente, "
               "por isso a confiança dos resultados é mais baixa.")
elif DIST > 50:
    st.info(f"A sua machamba está a {DIST:.0f} km do ponto com dados. Os resultados são aproximados.")

st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
aba_cmp, aba_clima, aba_cult, aba_info = st.tabs([
    "🧭 Comparar estratégias", "📊 Chuva e solo", "🌾 Culturas", "ℹ️ Como funciona",
])


# ============================================================================
# 9. ABA · COMPARAR ESTRATÉGIAS
# ============================================================================
def bloco(css, titulo, itens):
    li = "".join(f"<li>{i}</li>" for i in itens) or "<li>Sem pontos a destacar.</li>"
    return f'<div class="rc-bloco {css}"><h5>{titulo}</h5><ul>{li}</ul></div>'


def montar_blocos(nome, e):
    ev, ben, lac, risc = [], [], [], []
    for jan, j, c in zip(JANELAS, janelas, e["ciclos"]):
        ev.append(f"{jan['nome']} ({jan['periodo']}): chuva {j['chuva']:.0f} mm, humidade do solo {j['umid']:.2f} "
                  f"({classe_humidade(j['umid'])}), máxima de {j['tmax']:.1f} °C. "
                  f"Ajuste de <b>{c['cultura']}</b> ao clima: {c['fit'] * 100:.0f}%.")
        ev.extend(f"{c['cultura']} no {jan['nome']}: {n}." for n in c["notas"])
    n_leg = sum(CULTURAS[c["cultura"]]["leguminosa"] for c in e["ciclos"])
    if n_leg:
        ben.append(f"{n_leg} ciclo(s) com leguminosa, que fixam azoto e reduzem a necessidade de adubo.")
    top = sorted(e["medios"].items(), key=lambda kv: kv[1], reverse=True)[:2]
    ben.append("Pontos mais fortes: " + " e ".join(f"{CRITERIOS[k].lower()} ({v:.0f}/100)" for k, v in top) + ".")
    if nome != estrategias[0][0]:
        melhor = max(CRITERIOS, key=lambda k: e["medios"][k] - atual["medios"][k])
        ganho = e["medios"][melhor] - atual["medios"][melhor]
        if ganho > 0:
            ben.append(f"Em relação à atual, ganha {ganho:.0f} pontos em {CRITERIOS[melhor].lower()}.")
    if DIST > 50:
        lac.append(f"O local está a {DIST:.0f} km dos dados de satélite.")
    if USA_DEMO:
        lac.append("Os dados de clima são de demonstração, não reais.")
    if not COL_NDVI:
        lac.append("Sem NDVI no cache: não sabemos se o campo está vazio nem a estação de crescimento real.")
    lac += ["Declive não medido: a erosão é estimada pela cultura, não pelo terreno.",
            "Sem dados do solo (textura, pH, matéria orgânica) nem preços de mercado atuais."]
    if not TABELA_CONFIRMADA:
        lac.append("Tabela de culturas ainda por confirmar com fontes locais.")
    for jan, c in zip(JANELAS, e["ciclos"]):
        cult = CULTURAS[c["cultura"]]
        if c["fit"] < 0.6:
            risc.append(f"{c['cultura']} no {jan['nome']} ({jan['fase']}) pode ter pouca água ou calor a mais. Considere rega.")
        if cult["ciclo"] > jan["dias"]:
            risc.append(f"{c['cultura']} demora cerca de {cult['ciclo']} dias e ocupa a terra mais do que este ciclo.")
    if len(set(e["seq"])) < 3:
        risc.append("Pouca diversidade de culturas: maior risco de pragas e doenças.")
    risc.append("<b>Valide com um técnico agrícola local antes de decidir.</b>")
    return ev, ben, lac, risc


with aba_cmp:
    melhor_nome, melhor_e = max(estrategias, key=lambda t: t[1]["score"])
    seq_melhor = " → ".join(melhor_e["seq"])
    if melhor_e is atual:
        frase = (f"Com as suas prioridades, a <b>sua rotação atual</b> ({seq_melhor}) já é a que melhor serve a sua machamba, "
                 f"com {atual['score']:.0f} pontos.")
    else:
        dif = melhor_e["score"] - atual["score"]
        frase = (f"Com as suas prioridades, a melhor opção é <b>{seq_melhor}</b>, com {melhor_e['score']:.0f} pontos "
                 f"({dif:+.0f} em relação à rotação atual). A confiança é {melhor_e['conf'].lower()}.")
    html(f'<div class="rc-resumo"><p>{frase}</p></div>')

    st.markdown("#### Diagnóstico da sua lavra")
    st.caption(f"Com base na rotação que indicou: {' → '.join(rot_atual)}.")
    titulos_tipo = {"ok": "ok", "alerta": "alerta", "perigo": "perigo", "info": "info"}
    for tipo, titulo, texto in diagnostico_lavra(rot_atual, janelas, irrigacao):
        html(f'<div class="rc-diag {titulos_tipo[tipo]}"><b>{titulo}</b>{texto}</div>')

    st.markdown("#### Três estratégias lado a lado")
    cols = st.columns(3)
    for col, (nome, e) in zip(cols, estrategias):
        seq_txt = " → ".join(f"{CULTURAS[c]['emoji']} {c}" for c in e["seq"])
        destaque = "destaque" if e["score"] == melhor_score else ""
        with col:
            html(f"""<div class="rc-estrategia {destaque}"><h4>{nome}</h4>
            <div class="rc-nota">{e['score']:.0f}<small> / 100</small></div>
            <div class="rc-seq">{seq_txt}</div>
            <span class="rc-conf {e['conf']}">Confiança {e['conf'].lower()}</span></div>""")
    st.caption("A pontuação mostra o quanto cada rotação serve as suas prioridades neste local. "
               "Não é uma previsão de produção nem uma probabilidade de sucesso.")

    nomes_curtos = [n.split(" · ")[0] for n, _ in estrategias]
    cores = [COR_CINZA, COR_VERDE, COR_TERRA]
    g1, g2 = st.columns(2)
    with g1:
        radar = go.Figure()
        nomes_k = list(CRITERIOS.values())
        for cor, nome_c, (_, e) in zip(cores, nomes_curtos, estrategias):
            valores = [e["medios"][k] for k in CRITERIOS]
            radar.add_trace(go.Scatterpolar(r=valores + valores[:1], theta=nomes_k + nomes_k[:1], name=nome_c,
                                            line=dict(color=cor, width=2)))
        radar.update_layout(title="Pontos fortes de cada estratégia", polar=dict(radialaxis=dict(range=[0, 100])),
                            legend=dict(orientation="h", y=-0.15))
        mostrar(radar, 400)
        st.markdown('<div class="rc-explica"><b>Como ler:</b> quanto mais a forma se estica para fora, melhor a estratégia '
                    'nesse critério (0 a 100). Compare a forma verde e a terra com a cinzenta, que é a sua rotação atual.</div>',
                    unsafe_allow_html=True)
    with g2:
        barras = pd.DataFrame({"Estratégia": nomes_curtos, "Pontuação": [e["score"] for _, e in estrategias]})
        fig_b = px.bar(barras, x="Estratégia", y="Pontuação", text="Pontuação", color="Estratégia",
                       color_discrete_sequence=cores, title="Pontuação total (0 a 100)")
        fig_b.update_traces(texttemplate="%{text:.0f}", textposition="outside")
        fig_b.update_layout(showlegend=False, yaxis_range=[0, 110], plot_bgcolor="white")
        mostrar(fig_b, 400)
        st.markdown('<div class="rc-explica"><b>Como ler:</b> a barra mais alta é a rotação que melhor serve as prioridades '
                    'que escolheu. Mude as prioridades à esquerda e veja o resultado mudar.</div>', unsafe_allow_html=True)

    st.markdown("#### Detalhe de cada estratégia")
    sub = st.tabs(nomes_curtos)
    for tab, (nome, e) in zip(sub, estrategias):
        with tab:
            cc = st.columns(3)
            for col, jan, c in zip(cc, JANELAS, e["ciclos"]):
                cult = CULTURAS[c["cultura"]]
                with col:
                    html(f"""<div class="rc-ciclo"><div class="fase">{jan['nome']} · {jan['periodo']} · {jan['fase']}</div>
                    <div class="cultura">{cult['emoji']} {c['cultura']}</div>
                    <p>Ciclo de cerca de {cult['ciclo']} dias. Ajuste ao clima: {c['fit'] * 100:.0f}%.</p></div>""")
            st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)
            ev, ben, lac, risc = montar_blocos(nome, e)
            b1, b2 = st.columns(2)
            b1.markdown(bloco("rc-evid", "Evidência", ev), unsafe_allow_html=True)
            b2.markdown(bloco("rc-ben", "Benefícios", ben), unsafe_allow_html=True)
            st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
            b3, b4 = st.columns(2)
            b3.markdown(bloco("rc-lac", "Lacunas de informação", lac), unsafe_allow_html=True)
            b4.markdown(bloco("rc-risc", "Riscos: validar com técnico local", risc), unsafe_allow_html=True)
            st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
            st.caption(f"Confiança {e['conf'].lower()} porque: " + "; ".join(e["conf_motivos"] or ["os dados cobrem bem o local"]) + ".")

    resumo = pd.DataFrame([{
        "Estratégia": n, "Ciclo 1": e["seq"][0], "Ciclo 2": e["seq"][1], "Ciclo 3": e["seq"][2],
        "Pontuação": round(e["score"], 1), "Confiança": e["conf"],
        **{CRITERIOS[k]: round(v, 1) for k, v in e["medios"].items()},
    } for n, e in estrategias])
    st.download_button("Descarregar comparação (CSV)", resumo.to_csv(index=False).encode("utf-8"),
                       "rotacampo_comparacao.csv", "text/csv")

# ============================================================================
# 10. ABA · CHUVA E SOLO
# ============================================================================
with aba_clima:
    st.subheader("O que os satélites dizem sobre o seu clima")
    cor_est = {"Época das chuvas": COR_VERDE, "Cacimbo (seca)": "#c77d2e"}
    g1, g2 = st.columns(2)
    with g1:
        f1 = px.bar(df, x="mes_label", y="Chuva_mm", color="Estacao", text="Chuva_mm", title="Chuva por mês (mm)",
                    color_discrete_map=cor_est, labels={"mes_label": "Mês", "Chuva_mm": "Chuva (mm)", "Estacao": "Estação"})
        f1.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        if df["Chuva_mm"].notna().any():
            pico = df.loc[df["Chuva_mm"].idxmax()]
            f1.add_annotation(x=pico["mes_label"], y=pico["Chuva_mm"], text=f"Pico: {pico['Chuva_mm']:.1f} mm",
                              showarrow=True, arrowhead=2, ax=0, ay=-35, bgcolor="#e6efe8", bordercolor=COR_VERDE)
        f1.update_layout(plot_bgcolor="white", yaxis_range=[0, max(float(df["Chuva_mm"].max()), 1) * 1.3],
                         legend=dict(orientation="h", y=1.14))
        mostrar(f1, 400)
        n_seco = int((df["Estacao"] == "Cacimbo (seca)").sum())
        st.markdown(f'<div class="rc-explica"><b>Como ler:</b> as barras verdes são meses de chuva, bons para semear sem rega. '
                    f'As de cor laranja são meses de cacimbo ({n_seco} nos dados), em que só vale a pena semear com rega ou com '
                    'culturas tolerantes à seca, como a mandioca. Os grupos foram separados por um algoritmo simples (k-means) '
                    'que olha para a chuva e para a humidade do solo ao mesmo tempo.</div>',
                    unsafe_allow_html=True)
    with g2:
        f2 = go.Figure()
        f2.add_hrect(y0=0.5, y1=1.3, fillcolor="#e6efe8", opacity=0.55, line_width=0,
                     annotation_text="Boa para germinar", annotation_position="top left")
        f2.add_hrect(y0=-0.1, y1=0.25, fillcolor="#f6e1da", opacity=0.55, line_width=0,
                     annotation_text="Solo muito seco", annotation_position="bottom left")
        f2.add_trace(go.Scatter(x=df["mes_label"], y=df["Umidade_Solo_Idx"], mode="lines+markers",
                                name="Humidade do solo (5 cm)", line=dict(color=COR_VERDE, width=3)))
        f2.add_trace(go.Scatter(x=df["mes_label"], y=df["Temp_Max_C"], mode="lines+markers", name="Temperatura máxima (°C)",
                                yaxis="y2", line=dict(color=COR_TERRA, dash="dash", width=2)))
        f2.update_layout(title="Humidade do solo e calor", plot_bgcolor="white",
                         yaxis=dict(title="Índice (0 seco · 1 húmido)", range=[-0.1, 1.3]),
                         yaxis2=dict(title="°C", overlaying="y", side="right", showgrid=False),
                         legend=dict(orientation="h", y=1.14))
        mostrar(f2, 400)
        quente = df[df["Temp_Max_C"] >= 30]
        txt = (f"Meses com 30 °C ou mais: {', '.join(quente['mes_label'])}. Evite semear nesses meses sem humidade no solo."
               if len(quente) else "Nenhum mês chegou aos 30 °C nos dados.")
        st.markdown(f'<div class="rc-explica"><b>Como ler:</b> a linha verde mostra se há água onde a semente germina '
                    f'(acima de 0,5 é bom, abaixo de 0,25 o solo está muito seco). A linha tracejada mostra o calor. {txt} '
                    'Dias de calor extremo ainda não estão no cache; usamos a temperatura máxima mensal como aproximação.</div>',
                    unsafe_allow_html=True)

    st.markdown("#### Mês a mês: quando semear")
    tabela_meses = clima_mes.reset_index().rename(columns={
        "mes": "Mês", "Chuva_mm": "Chuva (mm)", "Umidade_Solo_Idx": "Humidade do solo", "Temp_Max_C": "Máxima (°C)"})
    tabela_meses["Mês"] = tabela_meses["Mês"].apply(lambda m: MESES_PT[int(m) - 1])
    tabela_meses["Estado do solo"] = tabela_meses["Humidade do solo"].apply(classe_humidade)
    tabela_meses["Conselho"] = tabela_meses["Humidade do solo"].apply(
        lambda v: "sem dado" if pd.isna(v) else "Bom para semear" if v >= 0.5
        else "Semear só culturas tolerantes" if v >= 0.25 else "Evitar semear sem rega")
    tabela(tabela_meses.round(2))

    st.markdown("#### NDVI (verde da vegetação)")
    if COL_NDVI:
        f3 = px.line(df, x="mes_label", y=COL_NDVI, markers=True, title="Ciclo anual do NDVI",
                     labels={"mes_label": "Mês", COL_NDVI: "NDVI"})
        f3.update_traces(line_color=COR_VERDE)
        f3.update_layout(plot_bgcolor="white")
        mostrar(f3, 360)
        st.markdown('<div class="rc-explica"><b>Como ler:</b> o NDVI sobe quando há plantas verdes e desce quando o campo está '
                    'vazio ou seco. Os meses com valores baixos indicam fora da estação de crescimento.</div>', unsafe_allow_html=True)
    else:
        st.info("O cache ainda não tem NDVI. Quando for adicionado (uma coluna com 'ndvi' no nome), este gráfico aparece "
                "sozinho e permite detetar a estação de crescimento e campos vazios.")

    with st.expander("Ver todos os dados do cache"):
        colunas = ["validdate", "mes_label", "Estacao", "Temp_Max_C", "Chuva_mm", "Umidade_Solo_Idx"]
        if COL_NDVI:
            colunas.append(COL_NDVI)
        tabela(df[colunas])

# ============================================================================
# 11. ABA · CULTURAS
# ============================================================================
with aba_cult:
    st.subheader("Tabela de culturas")
    st.warning("Estes valores são iniciais, escritos pela equipa. Ainda têm de ser confirmados com técnicos e fontes locais "
               "(épocas de plantio, ciclo e dados do solo) antes de serem usados em decisões reais.")
    tab = pd.DataFrame([{
        "Cultura": f"{c['emoji']} {n}", "Tipo": c["grupo"], "Poupa água (1–5)": c["agua"], "Fixa azoto (1–5)": c["n"],
        "Exige azoto (1–5)": c["exig_n"], "Estrutura do solo (1–5)": c["raizes"], "Proteção da erosão (1–5)": c["erosao"],
        "Ciclo (dias)": c["ciclo"], "Tolerância à seca (1–5)": c["seca"], "Mercado (1–5)": c["mercado"], "Fonte": c["fonte"],
    } for n, c in CULTURAS.items()])
    tabela(tab)
    st.caption("Nota: 5 é o melhor valor, exceto em «Exige azoto», onde 5 significa que a cultura gasta muito azoto.")

# ============================================================================
# 12. ABA · COMO FUNCIONA
# ============================================================================
with aba_info:
    st.subheader("Como o RotaCampo chega aos resultados")
    st.markdown("""
**1. Dados em cache.** Os dados de satélite (chuva, humidade do solo, temperatura e NDVI) são descarregados antes e guardados em
`cache_huambo.csv`. A demonstração nunca depende de internet para os dados.

**2. Indicadores por ciclo.** Para cada ciclo (Out–Jan, Fev–Mai, Jun–Set) calculamos a chuva, a humidade do solo e o calor médios.

**3. Ajuste da cultura.** Cada cultura recebe de 0 a 100% em cada ciclo, conforme a sua tolerância à seca e ao calor e a duração do seu ciclo.

**4. Pontuação.** Em cada ciclo: `pontuação = média ponderada dos critérios × (0,5 + 0,5 × ajuste)`. Os pesos são as prioridades que
escolheu. Depois somamos bónus ou penalizações de rotação: leguminosa depois de não leguminosa (+6 pontos), repetir a cultura (−12 pontos)
e diversidade (+3 pontos por cultura diferente).

**5. Estratégias.** Testamos as 125 combinações de 3 culturas. Mostramos a sua rotação atual, a melhor alternativa e uma segunda
alternativa bem diferente.

**6. Confiança.** Depende da cobertura dos dados, da distância ao ponto com dados, da existência de NDVI, da folga entre estratégias e de a
tabela de culturas estar confirmada. Enquanto não estiver, a confiança nunca passa de «média».
""")
    st.markdown("#### Papel da IA")
    st.markdown("Hoje: agrupamento (k-means) de meses de chuva e de cacimbo. Próximo passo: séries temporais do NDVI para detetar a estação "
                "de crescimento e campos vazios, e agrupar anos secos e normais quando houver vários anos no cache.")
    st.markdown("#### Meta social")
    st.markdown("Chegar a mais de 1000 agricultores até 2027–2028, com formação agrícola e tecnologia acessível, do Planalto Central "
                "para outras regiões e culturas.")
