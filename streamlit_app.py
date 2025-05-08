import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="iFood Dashboard", layout="wide")
st.title("📦 iFood Dashboard Generator")

st.markdown("""
Faça o upload do seu arquivo `pedidos.csv` exportado do iFood para visualizar suas estatísticas de consumo.
""")

#upload do arquivo CSV
uploaded_file = st.file_uploader("📁 Envie seu arquivo .csv", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    #remove status irrelevantes
    df = df[~df["status"].isin(["DECLINED", "CANCELLED"])]

    #conversão de datas e colunas auxiliares
    df["data_pedido"] = pd.to_datetime(df["data_pedido"])
    df["ano"] = df["data_pedido"].dt.year
    df["ano_mes"] = df["data_pedido"].dt.to_period("M").astype(str)

    #filtro por ano (multiselect)
    anos_disponiveis = sorted(df["ano"].unique(), reverse=True)
    anos_selecionados = st.multiselect("📅 Selecione o(s) ano(s):", anos_disponiveis, default=anos_disponiveis)
    df_filtrado = df[df["ano"].isin(anos_selecionados)]

    #métricas principais
    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total gasto", f"R$ {df_filtrado['valor'].sum():.2f}")
    col2.metric("📦 Número de pedidos", len(df_filtrado))
    col3.metric("🧾 Ticket médio", f"R$ {df_filtrado['valor'].mean():.2f}")

    st.markdown("---")

    #top restaurantes por gasto
    top_restaurantes = df_filtrado.groupby("restaurante")["valor"].sum().sort_values(ascending=False).head(10)
    fig1 = px.bar(top_restaurantes, x=top_restaurantes.values, y=top_restaurantes.index,
                  orientation='h', labels={'x': 'Valor Total (R$)', 'y': 'Restaurante'},
                  title="🍽️ Top 10 Restaurantes por Gasto")
    st.plotly_chart(fig1, use_container_width=True)

    #gastos por mês
    gastos_mes = df_filtrado.groupby("ano_mes")["valor"].sum().reset_index()
    fig2 = px.line(gastos_mes, x="ano_mes", y="valor", markers=True, title="📆 Gastos por Mês")
    st.plotly_chart(fig2, use_container_width=True)

    #gastos por dia da semana
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

    fig3 = px.bar(gastos_dia_semana, x=gastos_dia_semana.index, y=gastos_dia_semana.values,
                  labels={'x': 'Dia da Semana', 'y': 'Gasto Total (R$)'},
                  title="📅 Gastos por Dia da Semana")
    st.plotly_chart(fig3, use_container_width=True)

    #tabela de pedidos
    st.markdown("### 📋 Tabela de Pedidos")
    colunas_para_mostrar = [col for col in df_filtrado.columns if col not in ["id_usuario", "data_registro"]]
    st.dataframe(df_filtrado[colunas_para_mostrar].sort_values("data_pedido", ascending=False).reset_index(drop=True))

else:
    st.warning("Por favor, envie seu arquivo CSV exportado do iFood para visualizar o dashboard.")
