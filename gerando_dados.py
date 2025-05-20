# gerar_dados.py
import pandas as pd
import numpy as np
from datetime import datetime
from geopy.geocoders import Nominatim
from time import sleep

# Semente para resultados consistentes
np.random.seed(10)

# Produtos
produtos = ['Smartphone', 'Tablet', 'Notebook', 'Smartwatch', 'Câmeras']
categorias = ['Eletrônicos', 'Portáteis', 'Fotografia']

dimen_produto = pd.DataFrame({
    'id_produto': range(1, len(produtos) + 1),
    'nome_produto': produtos,
    'categoria': np.random.choice(categorias, size=len(produtos)),
    'preco_unitario': np.random.uniform(100, 5000, size=len(produtos)).round(2)
})
dimen_produto.to_csv("dimen_produto.csv", index=False)

# Clientes
nomes_clientes = ['Empresa 1', 'Empresa 2', 'Empresa 3', 'Empresa 4', 'Empresa 5']
cidades = ['Recife', 'Parnamirim', 'Coxixola', 'João Pessoa', 'Caruaru']
estados = ['PE', 'RN', 'PB', 'PB', 'PE']

dimen_clientes = pd.DataFrame({
    'id_cliente': range(1, len(nomes_clientes) + 1),
    'nome_cliente': nomes_clientes,
    'cidade': cidades,
    'estado': estados
})

#Adicionando a latitude e longitude
geolocator = Nominatim(user_agent="geoapi")

def geocode(row):
    try:
        location = geolocator.geocode(f"{row['cidade']}, {row['estado']}, Brasil")
        sleep(1) #Evita bloqueio na aplicação por excesso de requisição, isso acontece quando utiliza o Nominatim
        if location:
            return pd.Series([location.latitude, location.longitude])
    except:
        return pd.Series([None, None])
    
dimen_clientes[['latitude', 'longitude']] = dimen_clientes.apply(geocode, axis=1)
dimen_clientes.to_csv("dimen_clientes.csv", index=False)

# Vendedores
vendedores = ['Marcia', 'Arthur', 'Chico', 'Matheus', 'Luan']
dimen_vendedor = pd.DataFrame({
    'id_vendedor': range(1, len(vendedores) + 1),
    'nome_vendedor': vendedores,
    'departamento': np.random.choice(['Vendas', 'Atendimento'], size=len(vendedores))
})
dimen_vendedor.to_csv("dimen_vendedor.csv", index=False)

# Fornecedores
fornecedores = ['Dell', 'Xiaomi', 'Samsung']
dimen_fornecedor = pd.DataFrame({
    'id_fornecedor': range(1, len(fornecedores) + 1),
    'nome_fornecedor': fornecedores,
    'pais': np.random.choice(['Brasil', 'EUA', 'China'], size=len(fornecedores))
})
dimen_fornecedor.to_csv("dimen_fornecedor.csv", index=False)

# Tempo
datas = pd.date_range(start="2023-01-01", end=datetime.today(), freq='D')
dimen_tempo = pd.DataFrame({
    'id_tempo': range(1, len(datas) + 1),
    'data': datas,
    'ano': datas.year,
    'mes': datas.month,
    'dia_semana': datas.strftime('%A')
})
dimen_tempo.to_csv("dimen_tempo.csv", index=False)

# Fato Vendas
n_vendas = 100
vendas_fato = pd.DataFrame({
    'id_venda': range(1, n_vendas + 1),
    'id_produto': np.random.choice(dimen_produto['id_produto'], size=n_vendas),
    'id_cliente': np.random.choice(dimen_clientes['id_cliente'], size=n_vendas),
    'id_vendedor': np.random.choice(dimen_vendedor['id_vendedor'], size=n_vendas),
    'id_fornecedor': np.random.choice(dimen_fornecedor['id_fornecedor'], size=n_vendas),
    'id_tempo': np.random.choice(dimen_tempo['id_tempo'], size=n_vendas),
    'quantidade': np.random.randint(1, 10, size=n_vendas)
})

# Calculando o valor total
preco_dicio = dimen_produto.set_index('id_produto')['preco_unitario'].to_dict()
vendas_fato['preco_unitario'] = vendas_fato['id_produto'].map(preco_dicio)
vendas_fato['valor_total'] = (vendas_fato['quantidade'] * vendas_fato['preco_unitario']).round(2)
vendas_fato.to_csv("vendas_fato.csv", index=False)

print("✅ Dados gerados com sucesso!")
