import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="iFoodStats", layout="wide")

# Função para formatar valores em reais com ponto e vírgula no estilo BR
def format_currency_br(value):
    return f"R$ {value:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

# Estilos e ícones
st.markdown("""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .block-container {
            padding-top: 1rem;
        }
        .metric-container {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 12px;
            flex: 1;
            min-width: 160px;
            color: white;
            text-align: center;
        }
        .metric-card i {
            font-size: 22px;
            margin-bottom: 8px;
            color: #f63366;
        }
        .metric-card h3 {
            margin: 0;
            font-size: 15px;
            color: #ccc;
        }
        .metric-card p {
            margin: 0;
            font-size: 24px;
            font-weight: bold;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#f63366'><i class='fa-solid fa-chart-pie'></i> iFoodStats</h1>", unsafe_allow_html=True)

# Upload
uploaded_file = st.sidebar.file_uploader("📂 Envie seu arquivo CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["data_pedido"] = pd.to_datetime(df["data_pedido"])
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")

    # Filtros
    df["ano"] = df["data_pedido"].dt.year
    anos = df["ano"].unique().tolist()
    anos_selecionados = st.sidebar.multiselect("Ano(s):", sorted(anos, reverse=True), default=sorted(anos, reverse=True))
    df = df[df["ano"].isin(anos_selecionados)]

    # Métricas
    st.markdown("""
    <div class='metric-container'>
        <div class='metric-card'>
            <i class='fa-solid fa-coins'></i>
            <h3>Total gasto</h3>
            <p>R$ {:,.2f}</p>
        </div>
        <div class='metric-card'>
            <i class='fa-solid fa-receipt'></i>
            <h3>Pedidos</h3>
            <p>{}</p>
        </div>
        <div class='metric-card'>
            <i class='fa-solid fa-ticket'></i>
            <h3>Ticket médio</h3>
            <p>R$ {:,.2f}</p>
        </div>
        <div class='metric-card'>
            <i class='fa-solid fa-arrow-up'></i>
            <h3>Pedido mais caro</h3>
            <p title="{}">{} em {}</p>
        </div>
        <div class='metric-card'>
            <i class='fa-solid fa-arrow-down'></i>
            <h3>Pedido mais barato</h3>
            <p title="{}">{} em {}</p>
        </div>
    </div>
    """.format(
        total_gasto, num_pedidos, ticket_medio,
        restaurante_max, valor_max, restaurante_max,
        restaurante_min, valor_min, restaurante_min
    ), unsafe_allow_html=True)

    # Gráfico - Top Restaurantes por Gasto
    st.markdown("### <i class='fas fa-utensils'></i> Top Restaurantes", unsafe_allow_html=True)
    top = df.groupby("restaurante")["valor"].sum().sort_values(ascending=False).head(10).reset_index()
    fig1 = px.bar(top, x="valor", y="restaurante", orientation="h",
                  labels={"valor": "Gasto Total (R$)", "restaurante": "Restaurante"})
    fig1.update_traces(marker_color="#f63366", hovertemplate="R$ %{x:,.2f} em %{y}")
    fig1.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico - Gastos por Mês
    st.markdown("### <i class='fas fa-calendar-alt'></i> Gastos por Mês", unsafe_allow_html=True)
    df["ano_mes"] = df["data_pedido"].dt.to_period("M").astype(str)
    mes = df.groupby("ano_mes")["valor"].sum().reset_index()
    fig2 = px.line(mes, x="ano_mes", y="valor", markers=True,
                   labels={"ano_mes": "Mês", "valor": "Gasto Total (R$)"})
    fig2.update_traces(line_color="#f63366", marker_color="#f63366",
                       hovertemplate="R$ %{y:,.2f} em %{x}")
    st.plotly_chart(fig2, use_container_width=True)

    # Gráfico - Gastos por Dia da Semana
    st.markdown("### <i class='fas fa-calendar-day'></i> Gastos por Dia da Semana", unsafe_allow_html=True)
    ordem = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"]
    df["dia_semana"] = df["data_pedido"].dt.day_name(locale='pt_BR').str.lower()
    df["dia_semana"] = pd.Categorical(df["dia_semana"], categories=ordem, ordered=True)
    dia = df.groupby("dia_semana")["valor"].sum().reset_index()
    fig3 = px.bar(dia, x="dia_semana", y="valor", labels={"valor": "Gasto Total (R$)", "dia_semana": "Dia da Semana"})
    fig3.update_traces(marker_color="#f63366", hovertemplate="R$ %{y:,.2f} no(a) %{x}")
    st.plotly_chart(fig3, use_container_width=True)

    # Tabela de pedidos
    st.markdown("### <i class='fas fa-table'></i> Tabela de Pedidos", unsafe_allow_html=True)
    df_visual = df[["restaurante", "valor", "data_pedido", "dia_semana"]].copy()
    df_visual.columns = ["🍴 Restaurante", "💰 Valor (R$)", "📅 Data", "📅 Dia da Semana"]
    df_visual["💰 Valor (R$)"] = df_visual["💰 Valor (R$)"].map(format_currency_br)
    df_visual["📅 Data"] = df_visual["📅 Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df_visual, use_container_width=True)

else:
    st.info("Por favor, envie um arquivo CSV para começar.")







