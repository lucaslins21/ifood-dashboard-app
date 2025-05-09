import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="iFoodStats", layout="wide")

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

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df["data_pedido"] = pd.to_datetime(df["data_pedido"])
    df["valor"] = pd.to_numeric(df["valor"], errors='coerce')
    df["dia_semana"] = df["data_pedido"].dt.day_name(locale='pt_BR')

    # Métricas principais
    total_gasto = df["valor"].sum()
    num_pedidos = len(df)
    ticket_medio = total_gasto / num_pedidos if num_pedidos > 0 else 0
    pedido_mais_caro = df.loc[df["valor"].idxmax()]
    pedido_mais_barato = df.loc[df["valor"].idxmin()]

    valor_max = f"R$ {pedido_mais_caro['valor']:.2f}".replace(".", ",")
    valor_min = f"R$ {pedido_mais_barato['valor']:.2f}".replace(".", ",")

    restaurante_max = pedido_mais_caro['restaurante']
    restaurante_min = pedido_mais_barato['restaurante']

    # Mostrando as métricas no topo
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






