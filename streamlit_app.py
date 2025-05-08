import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="iFood Dashboard", layout="wide")

# Injeção de CSS leve + Font Awesome para ícones
st.markdown("""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#f63366'><i class='fas fa-chart-pie'></i> iFood Dashboard Generator</h1>", unsafe_allow_html=True)

# Upload
uploaded_file = st.sidebar.file_uploader("📁 Envie seu arquivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df["data_pedido"] = pd.to_datetime(df["data_pedido"])
    df["ano"] = df["data_pedido"].dt.year
    df["ano_mes"] = df["data_pedido"].dt.to_period("M").astype(str)
    dias = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    df["dia_semana"] = df["data_pedido"].dt.dayofweek.apply(lambda x: dias[x])


    df = df[df["status"] == "CONCLUDED"]
    df = df.drop(columns=["id_usuario", "data_registro", "status", "id_pedido"])

    # Filtros na sidebar
    st.sidebar.markdown("### <i class='fas fa-filter'></i> Filtros", unsafe_allow_html=True)
    anos_disponiveis = sorted(df["ano"].unique(), reverse=True)
    anos_selecionados = st.sidebar.multiselect("Ano(s):", anos_disponiveis, default=anos_disponiveis)
    df = df[df["ano"].isin(anos_selecionados)]

    # Métricas
    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total gasto", f"R$ {df['valor'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("📦 Pedidos", len(df))
    col3.metric("🧾 Ticket médio", f"R$ {df['valor'].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")

    cor = "#f63366"

    # Top Restaurantes
    st.markdown("### <i class='fas fa-utensils'></i> Top Restaurantes", unsafe_allow_html=True)
    top = df.groupby("restaurante")["valor"].sum().sort_values(ascending=False).head(10).reset_index()
    fig1 = px.bar(top, x="valor", y="restaurante", orientation="h", labels={"valor": "Gasto Total (R$)", "restaurante": "Restaurante"})
    fig1.update_traces(marker_color=cor, hovertemplate="R$ %{x:,.2f} em %{y}")
    fig1.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig1, use_container_width=True)

    # Gastos por Mês
    st.markdown("### <i class='fas fa-calendar-alt'></i> Gastos por Mês", unsafe_allow_html=True)
    mes = df.groupby("ano_mes")["valor"].sum().reset_index()
    fig2 = px.line(mes, x="ano_mes", y="valor", labels={"ano_mes": "Mês", "valor": "Gasto Total (R$)"}, markers=True)
    fig2.update_traces(line_color=cor, marker_color=cor, hovertemplate="R$ %{y:,.2f} em %{x}")
    st.plotly_chart(fig2, use_container_width=True)

    # Gastos por Dia da Semana
    st.markdown("### <i class='fas fa-calendar-day'></i> Gastos por Dia da Semana", unsafe_allow_html=True)
    ordem = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"]
    df["dia_semana"] = pd.Categorical(df["dia_semana"], categories=ordem, ordered=True)
    dia = df.groupby("dia_semana")["valor"].sum().reset_index()
    fig3 = px.bar(dia, x="dia_semana", y="valor", labels={"dia_semana": "Dia da Semana", "valor": "Gasto Total (R$)"})
    fig3.update_traces(marker_color=cor, hovertemplate="R$ %{y:,.2f} no(a) %{x}")
    st.plotly_chart(fig3, use_container_width=True)

    # Tabela final
    st.markdown("### <i class='fas fa-table'></i> Tabela de Pedidos", unsafe_allow_html=True)
    tabela = df[["restaurante", "valor", "data_pedido", "dia_semana"]].copy()
    tabela["data_pedido"] = tabela["data_pedido"].dt.strftime("%d/%m/%Y")
    tabela = tabela.sort_values("data_pedido", ascending=False).reset_index(drop=True)
    tabela.columns = ["🍴 Restaurante", "💰 Valor (R$)", "📅 Data", "📆 Dia da Semana"]
    st.dataframe(tabela, use_container_width=True)

else:
    st.info("Por favor, envie um arquivo CSV para começar.")






