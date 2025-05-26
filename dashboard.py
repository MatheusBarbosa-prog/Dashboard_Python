import streamlit as st
import pandas as pd
import plotly.express as px
from babel.numbers import format_currency

#Função para formatação dos valores(R$) no padrão BR
def formatar_valores(coluna):
    return coluna.map(lambda x: f"R$ {x:,.2f}".replace(",","X").replace(".",",").replace("X","."))

#Etapa 2: Conexão dos dados e regras de negócio

dimen_produto = pd.read_csv("dimen_produto.csv")
dimen_clientes = pd.read_csv("dimen_clientes.csv")
dimen_vendedor = pd.read_csv("dimen_vendedor.csv")
dimen_fornecedor = pd.read_csv("dimen_fornecedor.csv")
dimen_tempo = pd.read_csv("dimen_tempo.csv", parse_dates=["data"])
vendas_fato = pd.read_csv("vendas_fato.csv")

dimen_tempo['data'] = pd.to_datetime(dimen_tempo['data'], errors='coerce')

#Conexão das tabelas fato com as dimensões
df = vendas_fato.merge(dimen_produto, on='id_produto') \
                .merge(dimen_clientes, on='id_cliente') \
                .merge(dimen_vendedor, on='id_vendedor') \
                .merge(dimen_fornecedor, on='id_fornecedor') \
                .merge(dimen_tempo, on='id_tempo')

#Ajustando formato de data e criando a coluna "Ano"
df['data'] = pd.to_datetime(df['data'], errors='coerce')
df['ano'] = df['data'].dt.year

#Regras de negócios com filtros e agregações
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

#Agregação de vendas por estado
df_estado_vendas = df_filtrado.groupby('estado')['valor_total'].sum().reset_index()

# Garantir que as datas são válidas antes de continuar com a agregação e gráficos
df_filtrado = df_filtrado.dropna(subset=['data', 'valor_total', 'id_venda'])

#Cálculo das KPIs
total_vendas = df_filtrado['valor_total'].sum()
num_vendas = df_filtrado['id_venda'].nunique()
clientes_ativos = df_filtrado['id_cliente'].nunique()

#Agregação dos dados para gráficos e análises
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

    col1.markdown(f"<h3 style='font-size: 20px; color:#A2F5F9;'>💰 Total de Vendas<br><span style='font-size: 30px; color:#FFFFFF'>{formatted_total_vendas}</span></h3>", unsafe_allow_html=True)
    
    col2.markdown(f"""
    <div style="text-align: center;">
        <h3 style='font-size: 20px; color:#A2F5F9;'>🧾 Nº de Vendas<br>
        <span style='font-size: 30px; color:#FFFFFF;'>{num_vendas}</span></h3>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div style="text-align: center;">
        <h3 style='font-size: 20px; color:#A2F5F9;'>👥 Clientes Ativos<br>
        <span style='font-size: 30px; color:#FFFFFF;'>{clientes_ativos}</span></h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Vendas ao Longo do Tempo")
    
    #Agrupando os dados por ano
    df_tempo_vendas = df_filtrado.groupby('ano', as_index=False)['valor_total'].sum()
    
    #Formatando os valores
    df_tempo_vendas['valor_formatado'] = formatar_valores(df_tempo_vendas['valor_total'])

    fig1 = px.line(df_tempo_vendas, x='ano', y='valor_total', title=None, markers=True, custom_data=['valor_formatado'])

    # Encontrando o valor máximo para ajustar o eixo Y
    max_y_value = df_tempo_vendas['valor_total'].max()

    fig1.update_traces(
        hovertemplate="<b>Ano:</b> %{x}<br><b>Total Vendido:</b> %{customdata[0]}<extra></extra>"
    )

    # Modificando o eixo 'x' para exibir apenas os anos inteiros (sem valores quebrados)
    fig1.update_layout(
        xaxis_title='Ano',
        yaxis_title='Total de Vendas (R$)',

        xaxis_title_font=dict(
            size=16,
            color='#A2F5F9'
        ),
        yaxis_title_font=dict(
            size=16,
            color='#A2F5F9'
        ),

        xaxis=dict(
            tickmode='linear',        # Força uma escala linear
            dtick=1,                  # Distância entre os ticks (valores no eixo X)
            tick0=df_tempo_vendas['ano'].min(),  # Começa do primeiro ano no DataFrame
            showgrid = True
        ),
        yaxis=dict(
        range=[0, max_y_value * 1.2]  # Definindo o range do eixo Y
        )
    )
    st.markdown("""<h3 style='text-align: center; color: #A2F5F9; font-size: 18px; text-decoration: underline; margin-top:10px'> 📈 Evolução das Vendas entre 2023 e 2025</h3>""", unsafe_allow_html=True)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")
    st.subheader("Vendas por Produto")

    #Ordenando o DataFrame #2 do maior valor para o menor
    df_ordenado = df_produtos_vendas.sort_values(by='valor_total', ascending=False)
    df_ordenado['valor_formatado'] = formatar_valores(df_ordenado['valor_total'])

    #Aumentando os valores do eixo Y
    max_y_value3 = df_ordenado['valor_total'].max()
    
    fig2 = px.bar(df_ordenado, x= 'nome_produto', y='valor_total', title=None, custom_data=['valor_formatado'])

    fig2.update_traces(
        text = df_ordenado['valor_formatado'],
        textposition = 'outside',
        hovertemplate="<b>Produto:</b> %{x}<br><b>Total Vendido:</b> %{customdata[0]}<extra></extra>"
    )

    fig2.update_layout(
       
        xaxis_title = 'Nome do Produto',
        yaxis_title = 'Total de Vendas (R$)',

        xaxis_title_font=dict(
            size = 16,
            color = '#A2F5F9'
        ),
        yaxis_title_font=dict(
            size = 16,
            color = '#A2F5F9'
        ),

        yaxis = dict(range = [0, max_y_value3 * 1.18])#Aumenta o eixo Y em 10% além do valor máximo
    )
    st.markdown("""<h3 style='text-align: center; color: #A2F5F9; font-size: 18px; text-decoration: underline; margin-top:10px'> 💰 Total de Vendas por Produto</h3>""", unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("Vendas por Vendedor")

    #Ordenando os valores
    df_ordenado_vendedores = df_vendedores_vendas.sort_values(by='valor_total', ascending=False)
    df_ordenado_vendedores['valor_formatado'] = formatar_valores(df_ordenado_vendedores['valor_total'])

    #3º Gráfico, cálculo buscando o maior valor do eixo
    max_x_value = df_vendedores_vendas['valor_total'].max()
    x_range_max = max_x_value * 1.2
    
    fig3 = px.bar(df_ordenado_vendedores, x='valor_total', y='nome_vendedor', title=None, orientation='h', category_orders={'nome_vendedor': df_ordenado_vendedores['nome_vendedor'].tolist()}, custom_data=['valor_formatado'])

    fig3.update_traces(
        text = df_ordenado_vendedores['valor_formatado'],
        textposition = 'outside',
        hovertemplate="<b>Vendedor:</b> %{y}<br><b>Total Vendido:</b> %{customdata[0]}<extra></extra>"
    )

    fig3.update_layout(

        xaxis_title = 'Total de Vendas (R$)',
        yaxis_title = 'Nome do Vendedor',

        xaxis_title_font=dict(
            size = 16,
            color = '#A2F5F9'
        ),
        yaxis_title_font=dict(
            size = 16,
            color = '#A2F5F9'
        ),

        xaxis=dict(
            range=[0, x_range_max],
            showgrid = True
        )
    )
    st.markdown("""<h3 style='text-align: center; color: #A2F5F9; font-size: 18px; text-decoration: underline; margin-top:10px'> 💰 Total de Vendas por Vendedor</h3>""", unsafe_allow_html=True)
    st.plotly_chart(fig3, use_container_width=True)

#Pg2 com produtos e clientes
with pg2:

    cores_personalizadas = [ '#A2F5F9','#FF4136', '#0074D9', '#FFDC00', '#2ECC40']

    st.subheader("Vendas por Produto")

    df_produtos_ordenado = df_produtos_vendas.sort_values(by='valor_total', ascending=False)
    df_produtos_ordenado['valor_formatado'] = formatar_valores(df_produtos_ordenado['valor_total'])

    fig4 = px.pie(df_produtos_ordenado, names='nome_produto', values='valor_total', title=None, color_discrete_sequence = cores_personalizadas, custom_data=['valor_formatado'])

    fig4.update_traces(
        domain=dict(x=[0.2, 1.0]),
        textinfo = 'percent', #Exibe o percentual e o rótulo
        insidetextfont=dict(size = 10, family='Tahoma Black', color = 'black'),
        hovertemplate="<b>Produto:</b> %{label}<br><b>Total Vendido:</b> %{customdata[0]}<extra></extra>"
    )
    st.markdown("""<h3 style='text-align: center; color: #A2F5F9; font-size: 18px; text-decoration: underline; margin-top:10px;'> 📦 Proporção das Vendas por Produto</h3>""", unsafe_allow_html=True)
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    st.subheader("Vendas por Cliente")

    #Ordenação do DataFrame(gráfico 5)
    df_ordenado_clientes = df_clientes_vendas.sort_values(by='valor_total', ascending=False)
    df_ordenado_clientes['valor_formatado'] = formatar_valores(df_ordenado_clientes['valor_total'])

    # Calcula o valor máximo para ajustar o eixo Y
    max_y_value_clientes = df_ordenado_clientes['valor_total'].max()

    fig5 = px.bar(df_ordenado_clientes, x='nome_cliente', y='valor_total', title=None, custom_data=['valor_formatado'])

    fig5.update_traces(
        text = df_ordenado_clientes['valor_formatado'],
        textposition = 'outside',
        hovertemplate="<b>Cliente:</b> %{x}<br><b>Total Vendido:</b> %{customdata[0]}<extra></extra>"
    )

    fig5.update_layout(        
        xaxis_title = 'Nome do Cliente',
        yaxis_title = 'Total de Vendas (R$)',

        xaxis_title_font = dict(
            size = 16,
            color = '#A2F5F9'
        ),
        yaxis_title_font = dict(
            size = 16,
            color = '#A2F5F9'
        ),
        yaxis=dict(
            range=[0, max_y_value_clientes * 1.18] #Aumentar o valor do eixo y em 18%
        )
    )
    st.markdown("""<h3 style='text-align: center; color: #A2F5F9; font-size: 18px; text-decoration: underline; margin-top:10px'> 🧍 Total de Vendas por Cliente</h3>""", unsafe_allow_html=True)
    st.plotly_chart(fig5, use_container_width=True)

#Pg3 Relatórios
with pg3:

    if 'latitude' in df_filtrado.columns and 'longitude' in df_filtrado.columns:
        st.subheader("🗺️ Mapa de Vendas por Cidade")

        df_mapa = df_filtrado[['nome_cliente', 'cidade', 'estado', 'latitude', 'longitude', 'valor_total']].dropna()
        df_mapa['valor_formatado'] = formatar_valores(df_mapa['valor_total'])

        fig_mapa = px.scatter_mapbox(
            df_mapa,
            lat = "latitude",
            lon = "longitude",
            hover_name = "nome_cliente",
            hover_data = {"cidade": True,
                          "estado": True,
                          "valor_formatado": True,
                          "latitude": False,
                          "longitude": False,
                          "valor_total": False},
            size = "valor_total",
            color = "valor_total",
            zoom = 4,
            mapbox_style = "open-street-map",
            title = None
        )
        fig_mapa.update_traces(
            hovertemplate="<b>👤 Cliente:</b> %{hovertext}<br>" +
                            "<b>🏙️ Cidade:</b> %{customdata[0]}<br>" +
                            "<b>🗺️ Estado:</b> %{customdata[1]}<br>" +
                            "<b>💰 Total Vendido:</b> %{customdata[2]}<extra></extra>",
            hovertext=df_mapa['nome_cliente'],
            customdata=df_mapa[['cidade','estado','valor_formatado']].values
        )
        fig_mapa.update_layout(
            mapbox = dict(
                center = dict(lat = df_mapa['latitude'].mean(), lon = df_mapa['longitude'].mean()),
                zoom = 5.2
            )
        )
        st.markdown("""<h3 style='text-align: center; color: #A2F5F9; font-size: 18px; text-decoration: underline; margin-top:10px'>📍 Localização dos Clientes com base nas Vendas</h3>""", unsafe_allow_html=True)
        st.plotly_chart(fig_mapa, use_container_width = True)

    else:
        st.warning("Latitude e Longitude não encontrada nos dados dos clientes.")

    st.markdown("---")
    st.subheader("📦 Relatório de Vendas por Fornecedor")

    #Ordenando o DataFrame
    df_ordenado3 = df_fornecedores_vendas.sort_values(by='valor_total', ascending = False)
    df_ordenado3['valor_formatado'] = formatar_valores(df_ordenado3['valor_total'])

    #Ajuste do eixo com margem
    max_y_value2 = df_ordenado3['valor_total'].max()
    
    fig6 = px.bar(df_ordenado3, x='nome_fornecedor', y='valor_total', title=None, custom_data=['valor_formatado'])

    fig6.update_traces(
        text = df_ordenado3['valor_formatado'],
        textposition = 'outside',
        hovertemplate="<b>Fornecedor:</b> %{x}<br><b>Total Vendido:</b> %{customdata[0]}<extra></extra>"
    )

    fig6.update_layout(
        xaxis_title = 'Nome do Fornecedor',
        yaxis_title = 'Total de Vendas (R$)',

        xaxis_title_font = dict(
            size = 16,
            color = '#A2F5F9'
        ),
        yaxis_title_font = dict(
            size = 16,
            color = '#A2F5F9'
        ),
        yaxis = dict(range = [0, max_y_value2 * 1.18])
    )
    st.markdown("""<h3 style='text-align: center; color: #A2F5F9; font-size: 18px; text-decoration: underline; margin-top:10px'> 🧾 Total de Vendas por Fornecedor</h3>""", unsafe_allow_html=True)
    st.plotly_chart(fig6, use_container_width=True)