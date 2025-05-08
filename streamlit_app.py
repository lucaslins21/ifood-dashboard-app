import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="iFood Dashboard", layout="wide")
st.title("📦 iFood Dashboard Generator")

st.markdown("Envie seu arquivo `pedidos.csv` exportado do iFood para visualizar seus dados de consumo:")

uploaded_file = st.file_uploader("📁 Envie seu arquivo .csv", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Remove pedidos recusados ou cancelados
    df = df[~df["status"].isin(["DECLINED", "CANCELLED"])]

    # Processa datas
    df["data_pedido"] = pd.to_datetime(df["data_pedido"])
    df["ano"] = df["data_pedido"].dt.year
    df["ano_mes"] = df["data_pedido"].dt.to_period("M").astype(str)
    df["mes_extenso"] = df["data_pedido"].dt.strftime("%m/%Y")

    # Filtro por ano
    anos_disponiveis = sorted(df["ano"].unique(), reverse=True)
    anos_selecionados = st.multiselect("📅 Selecione o(s) ano(s):", anos_disponiveis, default=anos_disponiveis)
    df_filtrado = df[df["ano"].isin(anos_selecionados)]

    # Métricas principais
    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total gasto", f"R$ {df_filtrado['valor'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("📦 Número de pedidos", len(df_filtrado))
    col3.metric("🧾 Ticket médio", f"R$ {df_filtrado['valor'].mean():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")

    # Top Restaurantes
    top_restaurantes = df_filtrado.groupby("restaurante")["valor"].sum().sort_values(ascending=False).head(10)
    df_restaurantes = top_restaurantes.reset_index()
    df_restaurantes.columns = ["restaurante", "valor"]

    fig1 = px.bar(
        df_restaurantes,
        x="valor",
        y="restaurante",
        orientation='h',
        labels={"valor": "Gasto Total (R$)", "restaurante": "Restaurante"},
        title="🍽️ Top 10 Restaurantes por Gasto"
    )
    fig1.update_traces(
        hovertemplate="%{customdata} em %{y}<extra></extra>",
        customdata=[f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") for v in df_restaurantes["valor"]],
        marker_color="#f63366"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Gastos por Mês
    gastos_mes = df_filtrado.groupby("mes_extenso")["valor"].sum().reset_index()
    fig2 = px.line(
        gastos_mes,
        x="mes_extenso",
        y="valor",
        markers=True,
        title="📆 Gastos por Mês",
        labels={"mes_extenso": "Mês", "valor": "Gasto Total (R$)"}
    )
    fig2.update_traces(
        hovertemplate="R$ %{y:,.2f} em %{x}<extra></extra>",
        line_color="#f63366",
        marker=dict(color="#f63366")
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Gastos por Dia da Semana
    dia_map = {
        "Sunday": "domingo",
        "Monday": "segunda-feira",
        "Tuesday": "terça-feira",
        "Wednesday": "quarta-feira",
        "Thursday": "quinta-feira",
        "Friday": "sexta-feira",
        "Saturday": "sábado"
    }
    df_filtrado["dia_semana"] = df_filtrado["data_pedido"].dt.day_name().map(dia_map)
    ordem_dias = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"]
    gastos_dia_semana = df_filtrado.groupby("dia_semana")["valor"].sum().reindex(ordem_dias)

    df_dia_semana = pd.DataFrame({
        "dia_semana": gastos_dia_semana.index,
        "valor": gastos_dia_semana.values
    })

    fig3 = px.bar(
        df_dia_semana,
        x="dia_semana",
        y="valor",
        labels={"dia_semana": "Dia da Semana", "valor": "Gasto Total (R$)"},
        title="📅 Gastos por Dia da Semana"
    )
    fig3.update_traces(
        hovertemplate="R$ %{y:,.2f} no(a) %{x}<extra></extra>",
        marker_color="#f63366"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Tabela formatada
    df_filtrado["data_formatada"] = df_filtrado["data_pedido"].dt.strftime("%d/%m/%Y")
    df_ordenado = df_filtrado.sort_values("data_pedido", ascending=False).reset_index(drop=True)
    colunas_para_exibir = ["restaurante", "valor", "data_formatada", "dia_semana"]
    df_tabela = df_ordenado[colunas_para_exibir].rename(columns={
        "restaurante": "🍴 Restaurante",
        "valor": "💰 Valor (R$)",
        "data_formatada": "📅 Data do Pedido",
        "dia_semana": "🗓️ Dia da Semana"
    })

    st.markdown("### 📋 Tabela de Pedidos")
    st.dataframe(df_tabela.style.format({"💰 Valor (R$)": "R${:,.2f}"}), use_container_width=True)

else:
    st.warning("Por favor, envie seu arquivo CSV exportado do iFood para visualizar o dashboard.")





