"""
================================================================================
  DASHBOARD FINANCEIRO BPO - SISTEMA DE DIÁRIAS E OPERAÇÕES
  Engenheiro: Desenvolvido com Python + Streamlit + Google Gemini AI
  Versão: 1.0.0
================================================================================

Instruções de instalação:
--------------------------
  pip install streamlit pandas google-generativeai plotly tabulate openpyxl

Como rodar:
-----------
  streamlit run dashboard_financeiro.py

Variáveis de Ambiente (opcional, mas recomendado):
---------------------------------------------------
  Crie um arquivo .env ou defina via terminal:
  export GEMINI_API_KEY="SUA_CHAVE_AQUI"

  Ou insira diretamente na sidebar do app durante a execução.
================================================================================
"""

import os
import io
import warnings
import traceback
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Suprime warnings desnecessários
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# 1. CONFIGURAÇÃO GLOBAL DA PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard BPO Financeiro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Dashboard BPO Financeiro — Powered by Streamlit & Google Gemini",
    },
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. CSS PERSONALIZADO — VISUAL PREMIUM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Fundo geral ── */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #e8e8f0;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid #30363d;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        color: #8b949e;
        font-size: 0.82rem;
    }

    /* ── Cabeçalho principal ── */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }
    .sub-header {
        color: #8b949e;
        font-size: 0.95rem;
        margin-top: -8px;
        margin-bottom: 24px;
    }

    /* ── Cards de KPI ── */
    .kpi-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 24px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 12px;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    .kpi-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #8b949e;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #f0f6fc;
        line-height: 1.1;
    }
    .kpi-delta-pos { color: #3fb950; font-size: 0.82rem; }
    .kpi-delta-neg { color: #f85149; font-size: 0.82rem; }

    /* ── Divisor com gradient ── */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, #764ba2, transparent);
        border: none;
        margin: 24px 0;
        border-radius: 2px;
    }

    /* ── Seção de chat ── */
    .chat-header {
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .chat-sub {
        color: #8b949e;
        font-size: 0.82rem;
        margin-bottom: 16px;
    }

    /* ── Métricas nativas do Streamlit ── */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        backdrop-filter: blur(10px) !important;
    }
    [data-testid="metric-container"]:hover {
        border-color: rgba(102, 126, 234, 0.4) !important;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15) !important;
    }
    [data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 0.82rem !important; }
    [data-testid="stMetricValue"] { color: #f0f6fc !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"] svg { display: none !important; }

    /* ── Botões ── */
    .stButton>button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }

    /* ── Input de texto ── */
    .stTextInput input, .stChatInput textarea {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #f0f6fc !important;
        border-radius: 12px !important;
    }

    /* ── Tabela ── */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* ── Status badges ── */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .badge-pago    { background: rgba(63,185,80,0.2);  color: #3fb950; border: 1px solid #3fb950; }
    .badge-pendente { background: rgba(210,153,34,0.2); color: #d2a322; border: 1px solid #d2a322; }
    .badge-atraso  { background: rgba(248,81,73,0.2);  color: #f85149; border: 1px solid #f85149; }

    /* ── Scrollbar customizada ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
    ::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.4); border-radius: 3px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# 3. DADOS FICTÍCIOS DE FALLBACK (robustos e realistas)
# ─────────────────────────────────────────────────────────────────────────────
def _gerar_dados_ficticios() -> pd.DataFrame:
    """
    Gera um DataFrame de fallback com dados financeiros mensais realistas
    para demonstração do dashboard quando o Google Sheets não estiver disponível.
    """
    import random
    random.seed(42)

    meses = pd.date_range("2025-01-01", periods=12, freq="MS")

    registros = []
    for mes in meses:
        # Faturamento de serviços BPO — cresce ao longo do ano
        base_fat = 85_000 + (mes.month - 1) * 3_200
        faturamento = round(base_fat + random.uniform(-5000, 8000), 2)

        # Folha de pagamento (custo fixo + pequena variação)
        folha = round(32_000 + random.uniform(-800, 2_000), 2)

        # Encargos Trabalhistas (~30% da folha)
        encargos = round(folha * random.uniform(0.28, 0.32), 2)

        # Impostos sobre serviços (~14% do faturamento)
        impostos = round(faturamento * random.uniform(0.12, 0.16), 2)

        # Infraestrutura & TI
        infra = round(4_500 + random.uniform(-300, 800), 2)

        # Despesas Administrativas
        admin = round(6_000 + random.uniform(-500, 1_500), 2)

        # Saneamento de contas (recuperação de inadimplência)
        saneamento = round(random.uniform(500, 4_200), 2)

        # Resultado líquido
        custos_totais = folha + encargos + impostos + infra + admin
        resultado = round(faturamento - custos_totais, 2)

        # Append por categoria
        for categoria, valor, status in [
            ("Faturamento de Serviços",  faturamento, "Pago"),
            ("Folha de Pagamento",       -folha,      "Pago"),
            ("Encargos Trabalhistas",    -encargos,   random.choice(["Pago", "Pago", "Pendente"])),
            ("Impostos e Tributos",      -impostos,   random.choice(["Pago", "Pago", "Em Atraso"])),
            ("Infraestrutura & TI",      -infra,      "Pago"),
            ("Despesas Administrativas", -admin,      random.choice(["Pago", "Pendente"])),
            ("Saneamento de Contas",      saneamento, "Pago"),
        ]:
            registros.append({
                "Data":       mes,
                "Mês":        mes.strftime("%b/%Y"),
                "Categoria":  categoria,
                "Valor":      valor,
                "Status":     status,
            })

    df = pd.DataFrame(registros)
    df["Data"] = pd.to_datetime(df["Data"])
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 4. CARREGAMENTO DE DADOS (Google Sheets + fallback)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def carregar_dados(sheets_url: str = "") -> tuple[pd.DataFrame, str]:
    """
    Tenta carregar dados de um Google Sheets público.
    Caso falhe, retorna os dados fictícios de fallback.

    Args:
        sheets_url: URL pública do Google Sheets no formato /edit?usp=sharing

    Returns:
        tuple: (DataFrame com os dados, str indicando a fonte: 'sheets' ou 'fallback')
    """
    # ── Tenta ler do Google Sheets ──
    if sheets_url and "docs.google.com" in sheets_url:
        try:
            # Converte URL de visualização para URL de exportação CSV
            csv_url = sheets_url.replace(
                "/edit?usp=sharing", "/export?format=csv"
            ).replace(
                "/edit#gid=", "/export?format=csv&gid="
            )
            df = pd.read_csv(csv_url)

            # Normaliza colunas obrigatórias
            df.columns = [c.strip() for c in df.columns]
            if "Data" in df.columns:
                df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
            if "Valor" in df.columns:
                df["Valor"] = pd.to_numeric(
                    df["Valor"].astype(str).str.replace(",", ".").str.replace("R$", "").str.strip(),
                    errors="coerce",
                )
            df.dropna(subset=["Valor"], inplace=True)

            # Garante coluna Mês
            if "Mês" not in df.columns and "Data" in df.columns:
                df["Mês"] = df["Data"].dt.strftime("%b/%Y")

            return df, "sheets"
        except Exception as exc:
            # Falha silenciosa — vai para o fallback
            st.sidebar.warning(f"⚠️ Não foi possível ler o Sheets: {exc}")

    # ── Fallback: dados fictícios ──
    return _gerar_dados_ficticios(), "fallback"


# ─────────────────────────────────────────────────────────────────────────────
# 5. CÁLCULO DE KPIs
# ─────────────────────────────────────────────────────────────────────────────
def calcular_kpis(df: pd.DataFrame) -> dict:
    """
    Extrai os principais KPIs financeiros do DataFrame.

    Args:
        df: DataFrame com colunas Categoria, Valor, Data, Status

    Returns:
        dict com todos os KPIs calculados
    """
    # Separa período atual (últimos 30 dias) e período anterior (31-60 dias)
    if "Data" in df.columns:
        hoje = df["Data"].max()
        ini_atual   = hoje - pd.Timedelta(days=30)
        ini_anterior = hoje - pd.Timedelta(days=60)
        df_atual    = df[df["Data"] >= ini_atual]
        df_anterior = df[(df["Data"] >= ini_anterior) & (df["Data"] < ini_atual)]
    else:
        df_atual = df_anterior = df

    def soma(frame, positivo=True):
        vals = frame["Valor"]
        return vals[vals > 0].sum() if positivo else abs(vals[vals < 0].sum())

    # ── KPIs Globais (todo o período) ──
    fat_total    = df[df["Valor"] > 0]["Valor"].sum()
    custo_total  = abs(df[df["Valor"] < 0]["Valor"].sum())
    resultado    = fat_total - custo_total
    margem       = (resultado / fat_total * 100) if fat_total > 0 else 0

    # ── KPIs por Categoria (últimos 12 meses) ──
    cat_impostos  = abs(df[df["Categoria"].str.contains("Imposto|Tributo", case=False, na=False)]["Valor"].sum())
    cat_folha     = abs(df[df["Categoria"].str.contains("Folha|Encargo", case=False, na=False)]["Valor"].sum())
    cat_saneamento = df[df["Categoria"].str.contains("Saneamento", case=False, na=False)]["Valor"].sum()

    # ── Deltas (vs. período anterior) ──
    fat_ant  = soma(df_anterior, positivo=True)
    fat_atu  = soma(df_atual,    positivo=True)
    delta_fat = ((fat_atu - fat_ant) / fat_ant * 100) if fat_ant > 0 else 0

    cus_ant  = soma(df_anterior, positivo=False)
    cus_atu  = soma(df_atual,    positivo=False)
    delta_cus = ((cus_atu - cus_ant) / cus_ant * 100) if cus_ant > 0 else 0

    # ── Pendências ──
    pendentes = df[df["Status"].str.contains("Pendente|Atraso", case=False, na=False)]["Valor"].abs().sum()
    pct_pendente = (pendentes / fat_total * 100) if fat_total > 0 else 0

    return {
        "faturamento_bruto":   fat_total,
        "custo_operacional":   custo_total,
        "resultado_liquido":   resultado,
        "margem_liquida_pct":  margem,
        "impostos_totais":     cat_impostos,
        "folha_encargos":      cat_folha,
        "saneamento":          cat_saneamento,
        "pendencias":          pendentes,
        "pct_pendente":        pct_pendente,
        "delta_fat_pct":       delta_fat,
        "delta_cus_pct":       delta_cus,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. GRÁFICOS
# ─────────────────────────────────────────────────────────────────────────────
def grafico_evolucao(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de linha — Evolução mensal: Faturamento vs. Custos vs. Resultado.
    """
    df_pos   = df[df["Valor"] > 0].copy()
    df_neg   = df[df["Valor"] < 0].copy()

    # Agrupa por mês
    fat_mes  = (df_pos.groupby("Mês", sort=False)["Valor"]
                .sum().reset_index().rename(columns={"Valor": "Faturamento"}))
    cus_mes  = (df_neg.groupby("Mês", sort=False)["Valor"]
                .sum().abs().reset_index().rename(columns={"Valor": "Custos"}))

    merged = pd.merge(fat_mes, cus_mes, on="Mês", how="outer").fillna(0)
    merged["Resultado"] = merged["Faturamento"] - merged["Custos"]

    # Ordena cronologicamente
    if "Data" in df.columns:
        ordem = (df.groupby("Mês")["Data"].min()
                 .sort_values().index.tolist())
        cat_map = {m: i for i, m in enumerate(ordem)}
        merged["_ord"] = merged["Mês"].map(cat_map)
        merged = merged.sort_values("_ord").drop(columns="_ord")

    fig = go.Figure()
    cores = {"Faturamento": "#667eea", "Custos": "#f85149", "Resultado": "#3fb950"}

    for col in ["Faturamento", "Custos", "Resultado"]:
        fig.add_trace(go.Scatter(
            x=merged["Mês"], y=merged[col],
            mode="lines+markers",
            name=col,
            line=dict(color=cores[col], width=2.5),
            marker=dict(size=7, symbol="circle"),
            fill="tozeroy" if col == "Resultado" else "none",
            fillcolor="rgba(63,185,80,0.06)" if col == "Resultado" else None,
            hovertemplate=f"<b>{col}</b><br>%{{x}}<br>R$ %{{y:,.2f}}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="📈 Evolução Financeira Mensal", font=dict(size=16, color="#f0f6fc")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e", family="Inter, sans-serif"),
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(color="#8b949e"),
            title_font=dict(color="#8b949e"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            tickprefix="R$ ",
            tickformat=",.0f",
            zeroline=True,
            zerolinecolor="rgba(255,255,255,0.1)",
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.04)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            font=dict(color="#e8e8f0"),
        ),
        hovermode="x unified",
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig


def grafico_categorias(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras horizontais — Despesas por categoria.
    """
    df_neg = df[df["Valor"] < 0].copy()
    cat_sum = (df_neg.groupby("Categoria")["Valor"]
               .sum().abs().sort_values(ascending=True))

    cores_bar = px.colors.sequential.Purpor[::-1][:len(cat_sum)]

    fig = go.Figure(go.Bar(
        x=cat_sum.values,
        y=cat_sum.index,
        orientation="h",
        marker=dict(
            color=cores_bar,
            line=dict(color="rgba(255,255,255,0.1)", width=1),
        ),
        text=[f"R$ {v:,.0f}" for v in cat_sum.values],
        textposition="inside",
        textfont=dict(color="white", size=11),
        hovertemplate="<b>%{y}</b><br>R$ %{x:,.2f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="💸 Despesas por Categoria (Acumulado)", font=dict(size=16, color="#f0f6fc")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e"),
        xaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.05)",
            tickprefix="R$ ", tickformat=",.0f",
            zeroline=False,
        ),
        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def grafico_status_pizza(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de rosca — distribuição por Status.
    """
    status_sum = df.groupby("Status")["Valor"].count().reset_index()
    status_sum.columns = ["Status", "Contagem"]

    cores_status = {
        "Pago":      "#3fb950",
        "Pendente":  "#d2a322",
        "Em Atraso": "#f85149",
    }

    fig = go.Figure(go.Pie(
        labels=status_sum["Status"],
        values=status_sum["Contagem"],
        hole=0.6,
        marker=dict(
            colors=[cores_status.get(s, "#8b949e") for s in status_sum["Status"]],
            line=dict(color="#0f0f1a", width=3),
        ),
        textinfo="percent+label",
        textfont=dict(color="white", size=12),
        hovertemplate="<b>%{label}</b><br>%{value} registros<br>%{percent}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="✅ Status dos Lançamentos", font=dict(size=16, color="#f0f6fc")),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e"),
        showlegend=True,
        legend=dict(
            bgcolor="rgba(255,255,255,0.04)",
            bordercolor="rgba(255,255,255,0.08)",
            font=dict(color="#e8e8f0"),
        ),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 7. INTEGRAÇÃO COM GOOGLE GEMINI (Chatbot)
# ─────────────────────────────────────────────────────────────────────────────
def construir_system_prompt(df: pd.DataFrame, kpis: dict) -> str:
    """
    Constrói o System Prompt enviado ao Gemini com o contexto financeiro completo.

    Args:
        df:   DataFrame com os dados financeiros
        kpis: Dicionário com os KPIs calculados

    Returns:
        str: System prompt formatado
    """
    try:
        tabela_md = df.head(80).to_markdown(index=False)
    except Exception:
        tabela_md = df.head(80).to_string(index=False)

    resumo_kpis = f"""
FATURAMENTO BRUTO TOTAL:   R$ {kpis['faturamento_bruto']:>12,.2f}
CUSTOS OPERACIONAIS TOTAL: R$ {kpis['custo_operacional']:>12,.2f}
RESULTADO LÍQUIDO:         R$ {kpis['resultado_liquido']:>12,.2f}
MARGEM LÍQUIDA:            {kpis['margem_liquida_pct']:>11.1f}%
IMPOSTOS E TRIBUTOS:       R$ {kpis['impostos_totais']:>12,.2f}
FOLHA + ENCARGOS:          R$ {kpis['folha_encargos']:>12,.2f}
SANEAMENTO DE CONTAS:      R$ {kpis['saneamento']:>12,.2f}
PENDÊNCIAS FINANCEIRAS:    R$ {kpis['pendencias']:>12,.2f}  ({kpis['pct_pendente']:.1f}% do fat.)
""".strip()

    return f"""
Você é um Consultor Financeiro Sênior de BPO (Business Process Outsourcing), com mais de 15 anos de experiência em:
- Contabilidade Gerencial e Fiscal
- Análise de Desempenho Operacional (KPIs e OKRs)
- Gestão de Folha de Pagamento e Encargos Trabalhistas
- Planejamento Tributário (Simples Nacional, Lucro Presumido, Lucro Real)
- Saneamento e Recuperação de Contas a Receber
- Controladoria e Business Intelligence Financeiro

SEU COMPORTAMENTO:
- Responda SEMPRE em Português do Brasil, com linguagem técnica mas acessível
- Seja analítico, direto e propositivo — foque em diagnóstico e soluções
- Use dados concretos do contexto fornecido para embasar suas análises
- Identifique proativamente riscos financeiros, ineficiências e oportunidades
- Quando pertinente, sugira ações corretivas específicas e mensuráveis
- Formate respostas longas com headers e bullet points para facilitar a leitura

DADOS FINANCEIROS DO CLIENTE (contexto para análise):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESUMO DOS KPIs PRINCIPAIS:
{resumo_kpis}

TABELA DETALHADA DE LANÇAMENTOS (até 80 linhas):
{tabela_md}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Responda à pergunta do usuário utilizando exclusivamente os dados acima como base analítica.
""".strip()


def obter_resposta_gemini(
    pergunta: str,
    historico: list,
    system_prompt: str,
    api_key: str,
    modelo: str = "gemini-1.5-flash",
) -> str:
    """
    Envia a mensagem ao Google Gemini e retorna a resposta textual.

    Args:
        pergunta:     Pergunta atual do usuário
        historico:    Lista de dicts {"role": ..., "content": ...}
        system_prompt: Contexto financeiro para o modelo
        api_key:      Chave de API do Google AI
        modelo:       Identificador do modelo Gemini

    Returns:
        str: Resposta gerada pelo modelo
    """
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            model_name=modelo,
            system_instruction=system_prompt,
            generation_config={
                "temperature":     0.4,
                "top_p":           0.9,
                "max_output_tokens": 2048,
            },
        )

        # Converte histórico para o formato da API Gemini
        history_gemini = []
        for msg in historico:
            role = "user" if msg["role"] == "user" else "model"
            history_gemini.append({
                "role": role,
                "parts": [msg["content"]],
            })

        chat = model.start_chat(history=history_gemini)
        response = chat.send_message(pergunta)
        return response.text

    except ImportError:
        return (
            "❌ **Biblioteca não instalada.** Execute:\n\n"
            "```bash\npip install google-generativeai\n```\n\n"
            "Em seguida, reinicie o aplicativo."
        )
    except Exception as exc:
        err = str(exc)
        if "API_KEY" in err.upper() or "invalid" in err.lower():
            return (
                "🔑 **Chave de API inválida ou não configurada.**\n\n"
                "Insira sua chave Google AI na barra lateral do aplicativo."
            )
        return f"⚠️ **Erro ao consultar o Gemini:**\n\n```\n{err}\n```"


# ─────────────────────────────────────────────────────────────────────────────
# 8. SIDEBAR — Configurações
# ─────────────────────────────────────────────────────────────────────────────
def renderizar_sidebar() -> tuple[str, str, str]:
    """
    Renderiza a barra lateral com configurações do app.

    Returns:
        tuple: (api_key, sheets_url, modelo_selecionado)
    """
    with st.sidebar:
        st.markdown("### ⚙️ Configurações")
        st.markdown("---")

        # ── API Key ──
        st.markdown("**🔑 Google AI API Key**")
        api_key = st.text_input(
            label="Chave API",
            value=os.environ.get("GEMINI_API_KEY", ""),
            type="password",
            placeholder="AIza...",
            help="Obtenha gratuitamente em: aistudio.google.com",
            label_visibility="collapsed",
        )
        st.markdown(
            "<small>Obtenha sua chave em "
            "<a href='https://aistudio.google.com' target='_blank' "
            "style='color:#667eea;'>aistudio.google.com</a></small>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # ── Google Sheets URL ──
        st.markdown("**📋 Google Sheets (opcional)**")
        sheets_url = st.text_input(
            label="URL do Sheets",
            placeholder="https://docs.google.com/spreadsheets/d/.../edit?usp=sharing",
            help=(
                "Cole a URL pública do seu Google Sheets. "
                "O arquivo deve ter colunas: Data, Categoria, Valor, Status"
            ),
            label_visibility="collapsed",
        )
        if sheets_url:
            st.success("✅ URL detectada")
        else:
            st.info("📊 Usando dados de demonstração")

        st.markdown("---")

        # ── Modelo ──
        st.markdown("**🤖 Modelo Gemini**")
        modelo = st.selectbox(
            label="Modelo",
            options=[
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-2.0-flash",
                "gemini-2.5-flash-preview-05-20",
            ],
            index=0,
            help="Flash = mais rápido; Pro = mais analítico",
            label_visibility="collapsed",
        )

        st.markdown("---")

        # ── Limpar histórico ──
        if st.button("🗑️ Limpar Histórico do Chat", use_container_width=True):
            st.session_state.mensagens = []
            st.rerun()

        st.markdown("---")

        # ── Instruções rápidas ──
        with st.expander("📖 Como usar", expanded=False):
            st.markdown(
                """
                1. Insira sua **API Key** do Google AI
                2. (Opcional) Cole a URL do seu **Google Sheets**
                3. Explore os **KPIs** e gráficos
                4. Use o **chat** para perguntas analíticas

                **Exemplo de perguntas:**
                - *"Qual é minha maior despesa?"*
                - *"Como está a margem líquida?"*
                - *"Quais contas estão em atraso?"*
                - *"Como reduzir custos tributários?"*
                """
            )

        # ── Info rodapé ──
        st.markdown(
            "<br><small style='color:#30363d;'>Dashboard BPO v1.0 · Gemini AI</small>",
            unsafe_allow_html=True,
        )

    return api_key, sheets_url, modelo


# ─────────────────────────────────────────────────────────────────────────────
# 9. SEÇÃO DE KPIs
# ─────────────────────────────────────────────────────────────────────────────
def renderizar_kpis(kpis: dict):
    """Renderiza os cartões de KPI usando st.metric."""
    cols = st.columns(4, gap="medium")

    with cols[0]:
        st.metric(
            label="💰 Faturamento Bruto",
            value=f"R$ {kpis['faturamento_bruto']:,.0f}",
            delta=f"{kpis['delta_fat_pct']:+.1f}% vs. período ant.",
            delta_color="normal",
        )

    with cols[1]:
        st.metric(
            label="📉 Custos Operacionais",
            value=f"R$ {kpis['custo_operacional']:,.0f}",
            delta=f"{kpis['delta_cus_pct']:+.1f}% vs. período ant.",
            delta_color="inverse",
        )

    with cols[2]:
        cor_margem = "normal" if kpis["resultado_liquido"] >= 0 else "inverse"
        st.metric(
            label="📊 Resultado Líquido",
            value=f"R$ {kpis['resultado_liquido']:,.0f}",
            delta=f"Margem: {kpis['margem_liquida_pct']:.1f}%",
            delta_color=cor_margem,
        )

    with cols[3]:
        st.metric(
            label="⚠️ Pendências",
            value=f"R$ {kpis['pendencias']:,.0f}",
            delta=f"{kpis['pct_pendente']:.1f}% do faturamento",
            delta_color="inverse" if kpis["pendencias"] > 0 else "normal",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    cols2 = st.columns(3, gap="medium")

    with cols2[0]:
        st.metric(
            label="🏦 Impostos & Tributos",
            value=f"R$ {kpis['impostos_totais']:,.0f}",
            delta=f"{kpis['impostos_totais']/kpis['faturamento_bruto']*100:.1f}% do fat." if kpis['faturamento_bruto'] else "—",
            delta_color="off",
        )

    with cols2[1]:
        st.metric(
            label="👥 Folha + Encargos",
            value=f"R$ {kpis['folha_encargos']:,.0f}",
            delta=f"{kpis['folha_encargos']/kpis['faturamento_bruto']*100:.1f}% do fat." if kpis['faturamento_bruto'] else "—",
            delta_color="off",
        )

    with cols2[2]:
        st.metric(
            label="🔄 Saneamento de Contas",
            value=f"R$ {kpis['saneamento']:,.0f}",
            delta="Recuperado no período",
            delta_color="normal",
        )


# ─────────────────────────────────────────────────────────────────────────────
# 10. SEÇÃO DO CHATBOT
# ─────────────────────────────────────────────────────────────────────────────
def renderizar_chat(df: pd.DataFrame, kpis: dict, api_key: str, modelo: str):
    """
    Renderiza a interface de chat integrado com o Google Gemini.

    Args:
        df:      DataFrame com os dados financeiros
        kpis:    KPIs calculados
        api_key: Chave Google AI
        modelo:  Modelo Gemini selecionado
    """
    st.markdown('<div class="chat-header">🤖 Consultor Financeiro IA</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="chat-sub">Faça perguntas analíticas sobre seus dados financeiros. '
        "O assistente usa IA Gemini com contexto completo do seu balanço.</div>",
        unsafe_allow_html=True,
    )

    # Inicializa histórico de mensagens no session_state
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    # ── Mensagem de boas-vindas (apenas na primeira vez) ──
    if not st.session_state.mensagens:
        boas_vindas = (
            "👋 Olá! Sou seu **Consultor Financeiro de BPO**. "
            f"Analisei os dados disponíveis: faturamento de **R$ {kpis['faturamento_bruto']:,.0f}**, "
            f"custos de **R$ {kpis['custo_operacional']:,.0f}** e margem líquida de "
            f"**{kpis['margem_liquida_pct']:.1f}%**.\n\n"
            "Como posso ajudar? Você pode me perguntar sobre:\n"
            "- 📊 Análise de margens e rentabilidade\n"
            "- 💸 Redução de custos e otimização tributária\n"
            "- ⚠️ Gestão de inadimplência e saneamento\n"
            "- 👥 Eficiência da folha de pagamento\n"
            "- 📈 Tendências e projeções financeiras"
        )
        st.session_state.mensagens.append({"role": "assistant", "content": boas_vindas})

    # ── Exibe histórico ──
    container_chat = st.container(height=420, border=False)
    with container_chat:
        for msg in st.session_state.mensagens:
            with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
                st.markdown(msg["content"])

    # ── Input do usuário ──
    pergunta = st.chat_input(
        placeholder="Ex: Qual categoria está consumindo mais do meu faturamento?",
        key="chat_input",
    )

    if pergunta:
        # Verifica API Key
        if not api_key:
            st.error(
                "🔑 **API Key não configurada.** "
                "Insira sua chave Google AI na barra lateral para ativar o chat."
            )
            return

        # Adiciona mensagem do usuário
        st.session_state.mensagens.append({"role": "user", "content": pergunta})

        # Gera resposta
        with st.spinner("🧠 Analisando seus dados..."):
            system_prompt = construir_system_prompt(df, kpis)
            # Passa histórico excluindo a mensagem atual e a de boas-vindas (apenas para contexto)
            historico_envio = [
                m for m in st.session_state.mensagens[1:-1]  # exclui boas-vindas e msg atual
                if m["role"] in ("user", "assistant")
            ]
            resposta = obter_resposta_gemini(
                pergunta=pergunta,
                historico=historico_envio,
                system_prompt=system_prompt,
                api_key=api_key,
                modelo=modelo,
            )

        # Adiciona resposta ao histórico
        st.session_state.mensagens.append({"role": "assistant", "content": resposta})
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 11. FUNÇÃO PRINCIPAL — ORQUESTRAÇÃO DA INTERFACE
# ─────────────────────────────────────────────────────────────────────────────
def main():
    """Ponto de entrada principal do dashboard."""

    # ── Sidebar ──
    api_key, sheets_url, modelo = renderizar_sidebar()

    # ── Cabeçalho ──
    col_titulo, col_data = st.columns([3, 1])
    with col_titulo:
        st.markdown(
            '<h1 class="main-header">📊 Dashboard BPO Financeiro</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="sub-header">Visão 360° das Operações Financeiras · '
            "Análise Inteligente com Google Gemini AI</p>",
            unsafe_allow_html=True,
        )
    with col_data:
        st.markdown("<br>", unsafe_allow_html=True)
        hoje = date.today().strftime("%d/%m/%Y")
        st.info(f"📅 Atualizado em: **{hoje}**")

    # ── Carregamento de Dados ──
    with st.spinner("⏳ Carregando dados financeiros..."):
        df, fonte = carregar_dados(sheets_url)

    # Badge de fonte dos dados
    if fonte == "sheets":
        st.success("✅ Dados carregados do **Google Sheets**")
    else:
        st.info(
            "📊 Exibindo **dados de demonstração**. "
            "Conecte seu Google Sheets na barra lateral para usar dados reais."
        )

    st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)

    # ── KPIs ──
    kpis = calcular_kpis(df)
    st.markdown("### 🎯 Indicadores-Chave de Performance (KPIs)")
    renderizar_kpis(kpis)

    st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)

    # ── Gráficos ──
    st.markdown("### 📈 Visualizações Financeiras")
    col_g1, col_g2 = st.columns([3, 2], gap="medium")

    with col_g1:
        st.plotly_chart(grafico_evolucao(df), use_container_width=True)

    with col_g2:
        tab1, tab2 = st.tabs(["💸 Por Categoria", "✅ Por Status"])
        with tab1:
            st.plotly_chart(grafico_categorias(df), use_container_width=True)
        with tab2:
            st.plotly_chart(grafico_status_pizza(df), use_container_width=True)

    st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)

    # ── Tabela de dados + Chat lado a lado ──
    col_tab, col_chat = st.columns([2, 3], gap="large")

    with col_tab:
        st.markdown("### 🗂️ Lançamentos Recentes")

        # Filtro por categoria
        categorias = ["Todas"] + sorted(df["Categoria"].unique().tolist())
        cat_filtro = st.selectbox(
            "Filtrar por Categoria:",
            options=categorias,
            key="filtro_cat",
        )

        df_exibir = df if cat_filtro == "Todas" else df[df["Categoria"] == cat_filtro]

        # Formata para exibição
        df_fmt = df_exibir.copy()
        if "Data" in df_fmt.columns:
            df_fmt["Data"] = df_fmt["Data"].dt.strftime("%d/%m/%Y")
        df_fmt["Valor"] = df_fmt["Valor"].apply(
            lambda x: f"R$ {x:+,.2f}" if pd.notna(x) else "—"
        )

        colunas_exibir = [c for c in ["Data", "Mês", "Categoria", "Valor", "Status"] if c in df_fmt.columns]
        st.dataframe(
            df_fmt[colunas_exibir].tail(50),
            use_container_width=True,
            hide_index=True,
            height=400,
        )

        # Botão de download
        csv_download = df_exibir.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Exportar CSV",
            data=csv_download,
            file_name=f"financeiro_{date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_chat:
        st.markdown("### 💬 Chat com Consultor IA")
        renderizar_chat(df, kpis, api_key, modelo)

    # ── Rodapé ──
    st.markdown('<hr class="gradient-divider">', unsafe_allow_html=True)
    st.markdown(
        "<center><small style='color:#30363d;'>"
        "Dashboard BPO Financeiro · Powered by Streamlit & Google Gemini AI · "
        f"© {date.today().year}"
        "</small></center>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__" or True:
    main()
