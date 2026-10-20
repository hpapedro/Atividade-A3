import os
import re
import pandas as pd
import streamlit as st
import plotly.express as px

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (STREAMLIT)
# ==============================================================================
st.set_page_config(
    page_title="Atividade A3 - Análise de Conversas do WhatsApp",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constantes de Estilo: Fundo Bege Unificado e Linhas/Textos Pretos
COR_FUNDO = "#F5F0E6"
COR_PRETO = "#000000"
BORDA_PRETA = "1px solid #000000"

# CSS Completo: Todo o fundo na mesma cor bege, com letras e linhas estritamente pretas
st.markdown(f"""
    <style>
        /* Fundo geral da aplicação e do header do Streamlit */
        html, body, .stApp, [data-testid="stHeader"], [data-testid="stToolbar"], .main, .block-container {{
            background-color: {COR_FUNDO} !important;
            color: {COR_PRETO} !important;
        }}

        /* Tipografia e cores de todos os textos para preto */
        h1, h2, h3, h4, h5, h6, p, span, div, label, li, caption {{
            color: {COR_PRETO} !important;
        }}

        /* Container principal */
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2.5rem;
        }}

        /* Cabeçalho da Aplicação */
        .header-bege {{
            background-color: {COR_FUNDO};
            border: 2px solid {COR_PRETO};
            border-radius: 6px;
            padding: 18px 24px;
            margin-bottom: 22px;
        }}
        .header-titulo {{
            font-size: 1.8rem;
            font-weight: 800;
            color: {COR_PRETO} !important;
            margin: 0;
        }}
        .header-subtitulo {{
            font-size: 1rem;
            color: {COR_PRETO} !important;
            margin-top: 5px;
            margin-bottom: 0;
            font-weight: 500;
        }}

        /* Cards de resumo */
        .card-resumo {{
            background-color: {COR_FUNDO};
            border: 1px solid {COR_PRETO};
            border-radius: 6px;
            padding: 14px 18px;
            text-align: center;
        }}
        .card-rotulo {{
            font-size: 0.85rem;
            font-weight: 700;
            color: {COR_PRETO} !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        .card-valor {{
            font-size: 1.8rem;
            font-weight: 900;
            color: {COR_PRETO} !important;
            margin: 0;
        }}

        /* Linha divisória preta */
        hr {{
            border-color: {COR_PRETO} !important;
            border-width: 1px !important;
            margin: 24px 0 !important;
        }}

        /* Abas com fundo bege, bordas pretas e texto preto */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            border-bottom: 2px solid {COR_PRETO};
            background-color: {COR_FUNDO} !important;
            margin-top: 12px;
            margin-bottom: 20px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {COR_FUNDO} !important;
            color: {COR_PRETO} !important;
            border: 1px solid {COR_PRETO} !important;
            border-bottom: none !important;
            border-radius: 6px 6px 0 0;
            padding: 10px 18px;
            font-weight: 700;
            font-size: 0.95rem;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {COR_PRETO} !important;
            color: #ffffff !important;
            border: 1px solid {COR_PRETO} !important;
        }}
        .stTabs [aria-selected="true"] span, .stTabs [aria-selected="true"] p {{
            color: #ffffff !important;
        }}

        /* Inputs e caixas de seleção com fundo bege e borda preta */
        input, textarea, select, [data-baseweb="select"] > div {{
            background-color: {COR_FUNDO} !important;
            color: {COR_PRETO} !important;
            border: 1px solid {COR_PRETO} !important;
            border-radius: 4px !important;
        }}

        /* Indicador de busca */
        .badge-busca {{
            background-color: {COR_FUNDO};
            color: {COR_PRETO} !important;
            border: 1px solid {COR_PRETO};
            padding: 8px 14px;
            border-radius: 4px;
            font-size: 0.95rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 12px;
        }}

        /* Dataframes com fundo bege e linhas pretas */
        [data-testid="stDataFrame"] {{
            border: 1px solid {COR_PRETO};
            border-radius: 4px;
            background-color: {COR_FUNDO} !important;
        }}
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# PROCESSAMENTO DOS DADOS (ROBUSTO: ANDROID E IOS)
# ==============================================================================
@st.cache_data(show_spinner=False)
def carregar_e_processar_dados(caminho_arquivo: str) -> pd.DataFrame:
    """
    Lê o arquivo de exportação do WhatsApp (.txt) e converte em um DataFrame.
    Suporta formatos Android e iOS, agrega múltiplas linhas e remove mensagens de sistema.
    Retorna rigorosamente as 4 colunas: ['data', 'hora', 'nome do remetente', 'mensagem'].
    """
    padrao_ios = re.compile(
        r"^\[(?P<data>\d{1,2}/\d{1,2}/\d{2,4}),?\s+(?P<hora>\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP]\.?[mM]\.?)?)\]\s+(?P<remetente>[^:]+?):\s*(?P<mensagem>.*)$"
    )

    padrao_android = re.compile(
        r"^(?P<data>\d{1,2}/\d{1,2}/\d{2,4}),?\s+(?P<hora>\d{1,2}:\d{2}(?::\d{2})?(?:\s*[apAP]\.?[mM]\.?)?)\s+-\s+(?P<remetente>[^:]+?):\s*(?P<mensagem>.*)$"
    )

    palavras_chave_sistema = [
        "mensagens e as chamadas são protegidas",
        "mensagens e ligações são protegidas",
        "criptografia de ponta a ponta",
        "entrou usando o link de convite",
        "saiu do grupo",
        "removeu",
        "adicionou",
        "mudou o número",
        "alterou o assunto",
        "mudou a imagem",
        "criou o grupo",
        "mensagens temporárias",
        "código de segurança alterado",
        "chamada de voz perdida",
        "chamada de vídeo perdida",
        "iniciou uma chamada"
    ]

    registros = []
    registro_atual = None

    with open(caminho_arquivo, mode="r", encoding="utf-8", errors="replace") as f:
        for linha in f:
            # Remoção de caracteres de controle Unicode invisíveis do WhatsApp
            linha_limpa = (
                linha.replace("\u200e", "")
                     .replace("\ufeff", "")
                     .replace("\u200b", "")
                     .replace("\u202f", " ")
                     .strip()
            )

            match = padrao_ios.match(linha_limpa) or padrao_android.match(linha_limpa)

            if match:
                if registro_atual is not None:
                    registros.append(registro_atual)

                data_bruta = match.group("data").strip()
                hora_bruta = match.group("hora").strip()
                remetente_bruto = match.group("remetente").strip()
                mensagem_bruta = match.group("mensagem").strip()

                partes_data = data_bruta.split("/")
                if len(partes_data) == 3:
                    dia, mes, ano = partes_data[0].zfill(2), partes_data[1].zfill(2), partes_data[2]
                    if len(ano) == 2:
                        ano = "20" + ano
                    data_formatada = f"{dia}/{mes}/{ano}"
                else:
                    data_formatada = data_bruta

                conteudo_total = f"{remetente_bruto} {mensagem_bruta}".lower()
                eh_sistema = any(termo in conteudo_total for termo in palavras_chave_sistema)

                if not eh_sistema:
                    registro_atual = {
                        "data": data_formatada,
                        "hora": hora_bruta,
                        "nome do remetente": remetente_bruto,
                        "mensagem": mensagem_bruta
                    }
                else:
                    registro_atual = None
            else:
                if registro_atual is not None and linha_limpa:
                    registro_atual["mensagem"] += "\n" + linha_limpa

        if registro_atual is not None:
            registros.append(registro_atual)

    colunas_obrigatorias = ["data", "hora", "nome do remetente", "mensagem"]
    df = pd.DataFrame(registros, columns=colunas_obrigatorias)
    return df


# ==============================================================================
# FLUXO DA APLICAÇÃO
# ==============================================================================
ARQUIVO_FONTE = "conversa.txt"

# Cabeçalho da Aplicação
st.markdown("""
    <div class="header-bege">
        <h1 class="header-titulo">Aplicação de Análise de Dados do WhatsApp</h1>
        <p class="header-subtitulo">Painel interativo em Streamlit para processamento e visualização da exportação de conversa (Android / iOS)</p>
    </div>
""", unsafe_allow_html=True)

try:
    # 4. TRATAMENTO DE ERROS
    if not os.path.exists(ARQUIVO_FONTE):
        raise FileNotFoundError(f"Arquivo '{ARQUIVO_FONTE}' não encontrado.")

    df = carregar_e_processar_dados(ARQUIVO_FONTE)

    if df.empty:
        st.warning("⚠️ O arquivo `conversa.txt` foi lido, mas nenhuma mensagem válida foi identificada.")
        st.stop()

    # ==========================================================================
    # RESUMO GERAL DAS MENSAGENS (MÉTRICAS CLARAS)
    # ==========================================================================
    total_msgs = len(df)
    total_remetentes = df["nome do remetente"].nunique()
    dias_distintos = df["data"].nunique()
    remetente_mais_ativo = df["nome do remetente"].mode()[0] if not df.empty else "N/A"

    st.markdown("### Resumo Geral das Mensagens")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="card-resumo">
                <div class="card-rotulo">Total de Mensagens</div>
                <div class="card-valor">{total_msgs:,}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="card-resumo">
                <div class="card-rotulo">Total de Remetentes</div>
                <div class="card-valor">{total_remetentes}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="card-resumo">
                <div class="card-rotulo">Dias com Mensagens</div>
                <div class="card-valor">{dias_distintos}</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="card-resumo">
                <div class="card-rotulo">Remetente Mais Ativo</div>
                <div class="card-valor">{remetente_mais_ativo}</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")

    # ==========================================================================
    # DATAFRAME COMPLETO INICIAL (REQUISITO 3)
    # ==========================================================================
    st.markdown("### DataFrame Completo (4 Colunas Estritas)")
    st.caption("Base de dados com as 4 colunas: data, hora, nome do remetente e mensagem.")
    st.dataframe(
        df,
        use_container_width=True,
        height=280
    )

    st.markdown("---")

    # ==========================================================================
    # AS 5 OPÇÕES DE ANÁLISE EM ABAS
    # ==========================================================================
    st.markdown("### Opções de Análise Solicitadas")

    aba1, aba2, aba3, aba4, aba5 = st.tabs([
        "1. Resumo das conversas",
        "2. Histórico do remetente",
        "3. Gráfico do histórico do remetente",
        "4. Gráfico de pizza",
        "5. Gráfico de linhas"
    ])

    # --------------------------------------------------------------------------
    # OPÇÃO 1: Resumo das conversas
    # --------------------------------------------------------------------------
    with aba1:
        st.markdown("#### Opção 1: Resumo das conversas")
        st.write("**Lista de remetentes e total de conversas ordenada do maior para o menor:**")

        df_resumo = (
            df["nome do remetente"]
            .value_counts()
            .reset_index()
        )
        df_resumo.columns = ["nome do remetente", "total de conversas"]

        st.dataframe(
            df_resumo,
            use_container_width=True
        )

    # --------------------------------------------------------------------------
    # OPÇÃO 2: Histórico do remetente
    # --------------------------------------------------------------------------
    with aba2:
        st.markdown("#### Opção 2: Histórico do remetente")
        st.write("**Filtre por remetente para ver suas mensagens (com data e hora):**")

        col_rem, col_busca = st.columns([1, 2])
        with col_rem:
            lista_remetentes = sorted(df["nome do remetente"].unique().tolist())
            remetente_selecionado = st.selectbox(
                "Selecione o remetente:",
                options=lista_remetentes,
                key="select_remetente_aba2"
            )

        with col_busca:
            texto_busca = st.text_input(
                "Buscar na mensagem (digite para filtrar em tempo real):",
                placeholder="Exemplo: digite para ver apenas as mensagens que contêm este termo...",
                key="input_busca_aba2"
            )

        if remetente_selecionado:
            df_historico = df[df["nome do remetente"] == remetente_selecionado][["data", "hora", "mensagem"]].copy()

            if texto_busca.strip():
                termo = texto_busca.strip()
                df_exibicao = df_historico[df_historico["mensagem"].str.contains(termo, case=False, na=False)].reset_index(drop=True)
                st.markdown(
                    f"<div class='badge-busca'>🔎 Mostrando apenas as <b>{len(df_exibicao):,}</b> mensagens contendo: <i>\"{termo}\"</i></div>",
                    unsafe_allow_html=True
                )
            else:
                df_exibicao = df_historico.reset_index(drop=True)
                st.caption(f"Mostrando todas as **{len(df_exibicao):,}** mensagens de **{remetente_selecionado}**.")

            st.dataframe(
                df_exibicao,
                use_container_width=True,
                height=350
            )

    # --------------------------------------------------------------------------
    # OPÇÃO 3: Gráfico do histórico do remetente (Histograma)
    # --------------------------------------------------------------------------
    with aba3:
        st.markdown("#### Opção 3: Gráfico do histórico do remetente")
        st.write("**Histograma da quantidade de conversas por dia para o remetente selecionado:**")

        lista_remetentes_3 = sorted(df["nome do remetente"].unique().tolist())
        remetente_grafico = st.selectbox(
            "Selecione o remetente:",
            options=lista_remetentes_3,
            key="select_remetente_aba3"
        )

        if remetente_grafico:
            df_remetente_grafico = df[df["nome do remetente"] == remetente_grafico].copy()

            df_remetente_grafico["_data_dt"] = pd.to_datetime(
                df_remetente_grafico["data"],
                format="%d/%m/%Y",
                errors="coerce"
            )

            df_diario = (
                df_remetente_grafico.groupby(["_data_dt", "data"])
                .size()
                .reset_index(name="quantidade de conversas")
                .sort_values(by="_data_dt")
            )

            fig_hist = px.bar(
                df_diario,
                x="data",
                y="quantidade de conversas",
                labels={"data": "Data", "quantidade de conversas": "Quantidade de conversas"},
                color_discrete_sequence=[COR_PRETO],
                template="plotly_white"
            )

            # Estilo: Fundo Bege e Linhas/Textos Pretos
            fig_hist.update_layout(
                paper_bgcolor=COR_FUNDO,
                plot_bgcolor=COR_FUNDO,
                font=dict(color=COR_PRETO),
                xaxis=dict(
                    showgrid=False,
                    linecolor=COR_PRETO,
                    tickcolor=COR_PRETO,
                    tickfont=dict(color=COR_PRETO),
                    title=dict(text="Data", font=dict(color=COR_PRETO)),
                    tickangle=-45
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(0, 0, 0, 0.15)",
                    linecolor=COR_PRETO,
                    tickcolor=COR_PRETO,
                    tickfont=dict(color=COR_PRETO),
                    title=dict(text="Quantidade de conversas", font=dict(color=COR_PRETO))
                ),
                bargap=0.15,
                hovermode="x unified"
            )

            st.plotly_chart(fig_hist, use_container_width=True)

    # --------------------------------------------------------------------------
    # OPÇÃO 4: Gráfico de pizza
    # --------------------------------------------------------------------------
    with aba4:
        st.markdown("#### Opção 4: Gráfico de pizza")
        st.write("**Percentual de mensagens de cada remetente no grupo todo:**")

        df_pizza = (
            df["nome do remetente"]
            .value_counts()
            .reset_index()
        )
        df_pizza.columns = ["nome do remetente", "quantidade de mensagens"]

        # Paleta com contraste nítido, contornos pretos e fundo bege
        fig_pizza = px.pie(
            df_pizza,
            names="nome do remetente",
            values="quantidade de mensagens",
            color_discrete_sequence=["#111827", "#4b5563", "#9ca3af", "#d1d5db"],
            template="plotly_white"
        )

        fig_pizza.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color=COR_PRETO, width=1.5)),
            textfont=dict(color="#ffffff")
        )

        fig_pizza.update_layout(
            paper_bgcolor=COR_FUNDO,
            plot_bgcolor=COR_FUNDO,
            font=dict(color=COR_PRETO),
            legend=dict(font=dict(color=COR_PRETO))
        )

        st.plotly_chart(fig_pizza, use_container_width=True)

    # --------------------------------------------------------------------------
    # OPÇÃO 5: Gráfico de linhas
    # --------------------------------------------------------------------------
    with aba5:
        st.markdown("#### Opção 5: Gráfico de linhas")
        st.write("**Quantidade de mensagens ao longo do tempo (data) para cada remetente:**")

        df_linhas = df.copy()
        df_linhas["_data_dt"] = pd.to_datetime(
            df_linhas["data"],
            format="%d/%m/%Y",
            errors="coerce"
        )

        df_evolucao = (
            df_linhas.groupby(["_data_dt", "data", "nome do remetente"])
            .size()
            .reset_index(name="quantidade de mensagens")
            .sort_values(by="_data_dt")
        )

        fig_line = px.line(
            df_evolucao,
            x="data",
            y="quantidade de mensagens",
            color="nome do remetente",
            markers=True,
            labels={
                "data": "Data",
                "quantidade de mensagens": "Quantidade de mensagens",
                "nome do remetente": "nome do remetente"
            },
            template="plotly_white",
            color_discrete_sequence=["#000000", "#b91c1c", "#1d4ed8", "#15803d"]
        )

        fig_line.update_layout(
            paper_bgcolor=COR_FUNDO,
            plot_bgcolor=COR_FUNDO,
            font=dict(color=COR_PRETO),
            xaxis=dict(
                showgrid=False,
                linecolor=COR_PRETO,
                tickcolor=COR_PRETO,
                tickfont=dict(color=COR_PRETO),
                title=dict(text="Data", font=dict(color=COR_PRETO)),
                tickangle=-45
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(0, 0, 0, 0.15)",
                linecolor=COR_PRETO,
                tickcolor=COR_PRETO,
                tickfont=dict(color=COR_PRETO),
                title=dict(text="Quantidade de mensagens", font=dict(color=COR_PRETO))
            ),
            hovermode="x unified",
            legend=dict(font=dict(color=COR_PRETO))
        )

        st.plotly_chart(fig_line, use_container_width=True)

except FileNotFoundError:
    st.error(
        f"🚨 **Arquivo Não Encontrado:** O arquivo `{ARQUIVO_FONTE}` não foi encontrado na pasta do projeto.\n\n"
        "Por favor, certifique-se de colocar o arquivo da conversa exportada do WhatsApp nesta pasta com o nome exato **`conversa.txt`**."
    )
except Exception as e:
    st.error(f"❌ Ocorreu um erro inesperado: `{e}`")
