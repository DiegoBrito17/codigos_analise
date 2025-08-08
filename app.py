import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------
# 1. Carregar os dados
# -----------------------
@st.cache_data
def load_data():
    df = pd.read_excel('Online Retail.xlsx')
    df = df.dropna(subset=['CustomerID'])
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    return df

df = load_data()

st.title("📊 Dashboard - Online Retail")

# -----------------------
# 2. Filtros
# -----------------------
paises = df['Country'].unique()
pais_selecionado = st.selectbox("Selecione o país", sorted(paises))

df_filtrado = df[df['Country'] == pais_selecionado]

# -----------------------
# 3. Produtos mais vendidos
# -----------------------
st.subheader(f"Top 10 Produtos mais vendidos em {pais_selecionado}")
produtos_vendidos = df_filtrado.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)

fig1, ax1 = plt.subplots()
produtos_vendidos.plot(kind='bar', ax=ax1)
ax1.set_ylabel("Quantidade Vendida")
st.pyplot(fig1)

# -----------------------
# 4. Clientes que mais gastaram
# -----------------------
st.subheader(f"Top 10 Clientes por Faturamento em {pais_selecionado}")
clientes_ativos = df_filtrado.groupby('CustomerID')['TotalPrice'].sum().sort_values(ascending=False).head(10)

fig2, ax2 = plt.subplots()
clientes_ativos.plot(kind='bar', ax=ax2)
ax2.set_ylabel("Faturamento Total (GBP)")
st.pyplot(fig2)

# -----------------------
# 5. Faturamento mensal
# -----------------------
st.subheader(f"Faturamento Mensal em {pais_selecionado}")
faturamento_mensal = df_filtrado.groupby(pd.Grouper(key='InvoiceDate', freq='M'))['TotalPrice'].sum()

fig3, ax3 = plt.subplots()
ax3.plot(faturamento_mensal.index, faturamento_mensal.values)
ax3.set_ylabel("Faturamento (GBP)")
st.pyplot(fig3)
