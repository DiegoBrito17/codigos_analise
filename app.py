# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import textwrap

# === Configuração da página ===
st.set_page_config(
    page_title="Dashboard - Online Retail",
    page_icon="📊",
    layout="wide"
)

# -----------------------
# 1. Carregar os dados
# -----------------------
@st.cache_data
def load_data(path="Online Retail.xlsx"):
    df = pd.read_excel(path)
    df = df.dropna(subset=['CustomerID'])
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    return df

df = load_data()

# -----------------------
# Barra lateral - filtros
# -----------------------
st.sidebar.header("Filtros")
paises = sorted(df['Country'].unique())
pais_selecionado = st.sidebar.selectbox("Selecione o país", paises, index=paises.index("United Kingdom") if "United Kingdom" in paises else 0)

min_date = df['InvoiceDate'].min().date()
max_date = df['InvoiceDate'].max().date()
periodo = st.sidebar.date_input("Período", value=(min_date, max_date), min_value=min_date, max_value=max_date)

top_n = st.sidebar.slider("Top N (produtos/clientes)", min_value=5, max_value=20, value=10, step=1)

# Aplicar filtros
start_date, end_date = pd.to_datetime(periodo[0]), pd.to_datetime(periodo[1])
df_filtrado = df[
    (df['Country'] == pais_selecionado) &
    (df['InvoiceDate'] >= start_date) &
    (df['InvoiceDate'] <= end_date + pd.Timedelta(days=1))
]

# Se não houver dados após filtro, aviso
if df_filtrado.empty:
    st.warning("Nenhum dado disponível com os filtros selecionados.")
    st.stop()

# -----------------------
# KPIs no topo
# -----------------------
total_revenue = df_filtrado['TotalPrice'].sum()
unique_customers = df_filtrado['CustomerID'].nunique()
total_orders = df_filtrado['InvoiceNo'].nunique()
avg_ticket = total_revenue / total_orders if total_orders else 0

k1, k2, k3, k4 = st.columns([2,2,2,2])
k1.metric("Faturamento total (GBP)", f"£{total_revenue:,.2f}")
k2.metric("Clientes únicos", f"{unique_customers:,}")
k3.metric("Pedidos (invoices)", f"{total_orders:,}")
k4.metric("Ticket médio", f"£{avg_ticket:,.2f}")

st.markdown("---")

# -----------------------
# Preparar dados para gráficos
# -----------------------
# Top produtos (quantidade)
produtos_vendidos = (
    df_filtrado
    .groupby('Description')['Quantity']
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .reset_index()
)

# Coluna com versão curta do nome (para melhorar visual)
def truncate(text, width=35):
    return text if len(text) <= width else textwrap.shorten(text, width=width, placeholder="...")

produtos_vendidos['short_desc'] = produtos_vendidos['Description'].apply(lambda x: truncate(str(x), 35))

# Top clientes (faturamento)
clientes_ativos = (
    df_filtrado
    .groupby('CustomerID')['TotalPrice']
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .reset_index()
)

# -----------------------
# Layout: 2 colunas para gráficos
# -----------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Top {top_n} Produtos mais vendidos — {pais_selecionado}")
    fig1 = px.bar(
        produtos_vendidos,
        x='short_desc',
        y='Quantity',
        hover_data={'Description': True, 'Quantity': True},
        labels={'short_desc':'Produto', 'Quantity':'Quantidade Vendida'},
        title="Produtos mais vendidos",
        height=450
    )
    fig1.update_layout(margin=dict(t=50, b=120), template="plotly_white", xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader(f"Top {top_n} Clientes por Faturamento — {pais_selecionado}")
    fig2 = px.bar(
        clientes_ativos,
        x='CustomerID',
        y='TotalPrice',
        labels={'CustomerID':'Cliente', 'TotalPrice':'Faturamento (GBP)'},
        title="Clientes que mais gastaram",
        height=450
    )
    fig2.update_layout(margin=dict(t=50, b=80), template="plotly_white", xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# -----------------------
# Faturamento mensal (largura total)
# -----------------------
st.subheader(f"Faturamento Mensal — {pais_selecionado}")
faturamento_mensal = (
    df_filtrado
    .groupby(pd.Grouper(key='InvoiceDate', freq='M'))['TotalPrice']
    .sum()
    .reset_index()
)
fig3 = px.line(
    faturamento_mensal,
    x='InvoiceDate',
    y='TotalPrice',
    labels={'InvoiceDate':'Data', 'TotalPrice':'Faturamento (GBP)'},
    title="Faturamento Mensal",
    height=420
)
fig3.update_traces(mode='lines+markers')
fig3.update_layout(template="plotly_white", margin=dict(t=50, b=50))
st.plotly_chart(fig3, use_container_width=True)

# -----------------------
# Rodapé com informações
# -----------------------
st.caption(f"Dados filtrados: {start_date.date()} até {end_date.date()} • Total de linhas: {len(df_filtrado):,}")
