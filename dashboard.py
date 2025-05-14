import streamlit as st
import pandas as pd
import plotly.express as px
from babel.numbers import format_currency

#Conexão e regras de negócio
dimen_produto = pd.read_csv("dimen_produto.csv")
dimen_clientes = pd.read_csv("dimen_clientes.csv")
dimen_vendedor = pd.read_csv("dimen_vendedor.csv")
dimen_fornecedor = pd.read_csv("dimen_fornecedor.csv")
dimen_tempo = pd.read_csv("dimen_tempo.csv", parse_dates=["data"])
vendas_fato = pd.read_csv("vendas_fato.csv")

dimen_tempo['data'] = pd.to_datetime(dimen_tempo['data'], errors='coerce')
dimen_tempo['ano'] = dimen_tempo['data'].dt.year

#Aqui gera a conexão com as tabelas
df = vendas_fato.merge(dimen_produto, on='id_produto') \
                .merge(dimen_clientes, on='id_cliente') \
                .merge(dimen_vendedor, on='id_vendedor') \
                .merge(dimen_fornecedor, on='id_fornecedor') \
                .merge(dimen_tempo, on='id_tempo')

df['data'] = pd.to_datetime(df['data'], errors='coerce')
df['ano'] = df['data'].dt.year

#Criando filtros interativos
st.sidebar.header("🎯 Filtros")

anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano da Venda", anos_disponiveis, default=anos_disponiveis)

produtos = st.sidebar.multiselect("Produtos", df['nome_produto'].unique(), default=df['nome_produto'].unique())
vendedores = st.sidebar.multiselect("Vendedores", df['nome_vendedor'].unique(), default=df['nome_vendedor'].unique())
clientes = st.sidebar.multiselect("Clientes", df['nome_cliente'].unique(), default=df['nome_cliente'].unique())

#Aplicando os filtros
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['nome_produto'].isin(produtos)) &
    (df['nome_vendedor'].isin(vendedores)) &
    (df['nome_cliente'].isin(clientes))
]

# Garantir que as datas são válidas antes de continuar com a agregação e gráficos
df_filtrado = df_filtrado.dropna(subset=['data', 'valor_total', 'id_venda'])

#Recalcular as KPIs
total_vendas = df_filtrado['valor_total'].sum()
num_vendas = df_filtrado['id_venda'].nunique()
clientes_ativos = df_filtrado['id_cliente'].nunique()

#Agregação dos dados
df_produtos_vendas = df_filtrado.groupby('nome_produto')['valor_total'].sum().reset_index()
df_vendedores_vendas = df_filtrado.groupby('nome_vendedor')['valor_total'].sum().reset_index()
df_clientes_vendas = df_filtrado.groupby('nome_cliente')['valor_total'].sum().reset_index()
df_fornecedores_vendas = df_filtrado.groupby('nome_fornecedor')['valor_total'].sum().reset_index()


#Criando o Dashboard
st.title("📊 Dashboard de Vendas")

#Paginas ou Abas exigidas
pg1, pg2, pg3 = st.tabs(["📊 Vendas", "📈 Produtos e Clientes", "📊 Relatórios"])

#Pg1 com as vendas
with pg1:
    st.subheader("KPIs das vendas")
    formatted_total_vendas = format_currency(total_vendas, 'BRL', locale='pt_BR')
    col1, col2, col3 = st.columns([2,2,2])

    col1.markdown(f"<h3 style='font-size: 20px;'>💰 Total de Vendas<br><span style='font-size: 30px;'>{formatted_total_vendas}</span></h3>", unsafe_allow_html=True)
    
    col2.markdown(f"""
    <div style="text-align: center;">
        <h3 style='font-size: 20px;'>🧾 Nº de Vendas<br>
        <span style='font-size: 30px;'>{num_vendas}</span></h3>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div style="text-align: center;">
        <h3 style='font-size: 20px;'>👥 Clientes Ativos<br>
        <span style='font-size: 30px;'>{clientes_ativos}</span></h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Vendas ao Longo do Tempo")
    df_tempo_vendas = df_filtrado.groupby('ano', as_index=False)['valor_total'].sum().reset_index()
    fig6 = px.line(df_tempo_vendas, x='ano', y='valor_total', title="Vendas ao Longo do Tempo")

    # Encontrando o valor máximo para ajustar o eixo Y
    max_y_value = df_tempo_vendas['valor_total'].max()

    # Modificando o eixo 'x' para exibir apenas os anos inteiros (sem valores quebrados)
    fig6.update_layout(
        xaxis=dict(
            tickmode='linear',        # Força uma escala linear
            dtick=1,                  # Distância entre os ticks (valores no eixo X)
            tick0=df_tempo_vendas['ano'].min()  # Começa do primeiro ano no DataFrame
        ),
        yaxis=dict(
        range=[0, max_y_value * 1.1]  # Definindo o range do eixo Y(valor máximo + 10%)
        )
    )
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Vendas por Produto")
    fig1 = px.bar(df_produtos_vendas, x= 'nome_produto', y='valor_total', title="Total de Vendas por Produto")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Vendas por Vendedor")
    fig2 = px.bar(df_vendedores_vendas, x='nome_vendedor', y='valor_total', title="Total de Vendas por Vendedor")
    st.plotly_chart(fig2, use_container_width=True)

#Pg2 com produtos e clientes
with pg2:
    st.subheader("Vendas por Produto")
    fig3 = px.pie(df_produtos_vendas, names='nome_produto', values='valor_total', title="Participação de vendas por produto")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Vendas por Cliente")
    fig4 = px.bar(df_clientes_vendas, x='nome_cliente', y='valor_total', title="Vendas por Cliente")
    st.plotly_chart(fig4, use_container_width=True)

#Pg3 Relatórios
with pg3:
    st.subheader("Relatório de Vendas por Fornecedor")
    fig5 = px.bar(df_fornecedores_vendas, x='nome_fornecedor', y='valor_total', title="Vendas por fornecedor")
    st.plotly_chart(fig5, use_container_width=True)