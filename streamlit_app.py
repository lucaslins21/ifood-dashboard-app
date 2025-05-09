import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="iFoodStats",
    page_icon="https://github.com/lucaslins21/ifood-dashboard-app/blob/main/img/favicon.png?raw=true",
    layout="wide"
)

def format_currency_br(value):
    return f"R$ {value:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

#estilo
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
            width: 100%;
            text-align: center;
            display: flex;
            justify-content: center;
        }
        .metric-card p {
            margin: 0;
            font-size: 24px;
            font-weight: bold;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='margin-top: 1rem; color:#f63366'><i class='fa-solid fa-chart-pie'></i> iFoodStats</h1>", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader("📂 Envie seu arquivo pedidos.csv", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["data_pedido"] = pd.to_datetime(df["data_pedido"])
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df[df["status"] == "CONCLUDED"]

    df["ano"] = df["data_pedido"].dt.year
    anos = df["ano"].unique().tolist()
    anos_selecionados = st.sidebar.multiselect("Ano(s):", sorted(anos, reverse=True), default=sorted(anos, reverse=True))
    df = df[df["ano"].isin(anos_selecionados)]

    if not df.empty:
    total_gasto = df["valor"].sum()
    num_pedidos = len(df)
    ticket_medio = total_gasto / num_pedidos if num_pedidos else 0

    pedido_mais_caro = df.loc[df["valor"].idxmax()]
    ticket_medio = total_gasto / num_pedidos if num_pedidos else 0
    pedido_mais_caro = df.loc[df["valor"].idxmax()]
    pedido_mais_barato = df.loc[df["valor"].idxmin()]

    st.markdown(f"""
    <div class='metric-container'>
        <div class='metric-card' style='align-items: center; display: flex; flex-direction: column;'>
            <i class='fa-solid fa-coins'></i>
            <h3 style='text-align: center;'>Total gasto</h3>
            <p style='text-align: center;'>{format_currency_br(total_gasto)}</p>
        </div>
        <div class='metric-card' style='align-items: center; display: flex; flex-direction: column;'>
            <i class='fa-solid fa-receipt'></i>
            <h3 style='text-align: center;'>Pedidos</h3>
            <p style='text-align: center;'>{num_pedidos}</p>
        </div>
        <div class='metric-card' style='align-items: center; display: flex; flex-direction: column;'>
            <i class='fa-solid fa-ticket'></i>
            <h3 style='text-align: center;'>Ticket médio</h3>
            <p style='text-align: center;'>{format_currency_br(ticket_medio)}</p>
        </div>
        <div class='metric-card' style='align-items: center; display: flex; flex-direction: column;'>
            <i class='fa-solid fa-arrow-up'></i>
            <h3 style='text-align: center;'>Pedido mais caro</h3>
            <p style='text-align: center;'>{format_currency_br(pedido_mais_caro['valor'])} em {pedido_mais_caro['restaurante']}</p>
        </div>
        <div class='metric-card' style='align-items: center; display: flex; flex-direction: column;'>
            <i class='fa-solid fa-arrow-down'></i>
            <h3 style='text-align: center;'>Pedido mais barato</h3>
            <p style='text-align: center;'>{format_currency_br(pedido_mais_barato['valor'])} em {pedido_mais_barato['restaurante']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


    #gráfico Top Restaurantes
    st.markdown("### <i class='fas fa-utensils'></i> Top Restaurantes", unsafe_allow_html=True)
    top = df.groupby("restaurante")["valor"].sum().sort_values(ascending=False).head(10).reset_index()
    fig1 = px.bar(top, x="valor", y="restaurante", orientation="h",
                  labels={"valor": "Gasto Total (R$)", "restaurante": "Restaurante"})
    fig1.update_traces(marker_color="#f63366", hovertemplate="R$ %{x:,.2f} em %{y}")
    fig1.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig1, use_container_width=True)

    #gastos por Mês
    st.markdown("### <i class='fas fa-calendar-alt'></i> Gastos por Mês", unsafe_allow_html=True)
    df["ano_mes"] = df["data_pedido"].dt.to_period("M").astype(str)
    mes = df.groupby("ano_mes")["valor"].sum().reset_index()
    fig2 = px.line(mes, x="ano_mes", y="valor", markers=True,
                   labels={"ano_mes": "Mês", "valor": "Gasto Total (R$)"})
    fig2.update_traces(line_color="#f63366", marker_color="#f63366",
                       hovertemplate="R$ %{y:,.2f} em %{x}")
    st.plotly_chart(fig2, use_container_width=True)

    #gastos por Dia da Semana (com nome manual)
    st.markdown("### <i class='fas fa-calendar-day'></i> Gastos por Dia da Semana", unsafe_allow_html=True)
    ordem = ["domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"]
    dias_map = {0: "segunda-feira", 1: "terça-feira", 2: "quarta-feira", 3: "quinta-feira", 4: "sexta-feira", 5: "sábado", 6: "domingo"}
    df["dia_semana"] = df["data_pedido"].dt.dayofweek.map(dias_map)
    df["dia_semana"] = pd.Categorical(df["dia_semana"], categories=ordem, ordered=True)
    dia = df.groupby("dia_semana")["valor"].sum().reset_index()
    fig3 = px.bar(dia, x="dia_semana", y="valor", labels={"valor": "Gasto Total (R$)", "dia_semana": "Dia da Semana"})
    fig3.update_traces(marker_color="#f63366", hovertemplate="R$ %{y:,.2f} no(a) %{x}")
    st.plotly_chart(fig3, use_container_width=True)

    #tabela de pedidos
    st.markdown("### <i class='fas fa-table'></i> Tabela de Pedidos", unsafe_allow_html=True)
    df_visual = df[["restaurante", "valor", "data_pedido", "dia_semana"]].copy()
    df_visual.columns = ["🍴 Restaurante", "💰 Valor (R$)", "📅 Data", "📅 Dia da Semana"]
    df_visual["💰 Valor (R$)"] = df_visual["💰 Valor (R$)"].map(format_currency_br)
    df_visual["📅 Data"] = df_visual["📅 Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df_visual, use_container_width=True)

else:
    st.markdown("""
    <div style='margin-top: 2rem; padding: 1.5rem; border-radius: 10px; color: #83858c;'>
        <h2 style='color: #f63366; font-size: 1.7rem; line-height: 2.4rem; word-break: break-word; text-align: center;'>
            <i class='fa-solid fa-circle-info'></i>
            Como obter o arquivo <code style="font-size: 1.3rem;">pedidos.csv</code> do iFood?
        </h2>
        <p style='font-size: 16px; text-align: center;'>Siga os passos abaixo dentro do aplicativo do iFood:</p>
    </div>
""", unsafe_allow_html=True)


    col1, col2, col3 = st.columns(3)

    col1.image("img/print 1.png", use_container_width=True, caption="1. Acesse seu perfil")
    col2.image("img/print 2.png", use_container_width=True, caption="2. Vá em Ajuda")
    col3.image("img/print 3.png", use_container_width=True, caption="3. Toque em Privacidade e dados")

    col4, col5 = st.columns(2)

    col4.image("img/print 4.png", use_container_width=True, caption="4. Selecione 'Quero uma cópia dos meus dados'")
    col5.image("img/print 5.png", use_container_width=True, caption="5. Clique em 'Solicitar Cópia'")

    st.markdown("""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">

    <div style="margin-top: 1rem; padding: 1.5rem; border-radius: 10px; font-size: 15px; line-height: 1.6; color: #83858c;">
        <p style="margin-bottom: 1rem;">
            <i class="fas fa-hourglass-half" style="color: orange;"></i>
            <strong>  Em até 24 horas</strong>, o iFood enviará um arquivo <code>.zip</code> com seus dados. Ao descompactar, você encontrará três arquivos:
            <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
                <li><i class="fas fa-file-csv" style="color: #999;"></i> <code>enderecos.csv</code></li>
                <li><i class="fas fa-file-csv" style="color: #999;"></i> <code>pedidos.csv</code></li>
                <li><i class="fas fa-file-csv" style="color: #999;"></i> <code>usuarios.csv</code></li>
            </ul>
        </p>
        <p style="margin-top: 1rem; padding: 0.8rem 1rem; border-left: 5px solid #ff4b4b; border-radius: 6px;">
            <i class="fas fa-thumbtack" style="color: #ff4b4b;"></i>
            <strong>Envie apenas o arquivo <code>pedidos.csv</code></strong> clicando na <strong>seta <i class='fa-solid fa-chevron-right'></i> no canto superior esquerdo</strong> desta página.
        </p>
    </div>
    """, unsafe_allow_html=True)









