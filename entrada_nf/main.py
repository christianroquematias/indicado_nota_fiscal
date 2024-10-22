import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
import numpy as np

# Configuração da página do Streamlit - Esta linha deve ser a primeira do script!
st.set_page_config(layout='wide', page_title='Análise de Notas Fiscais')

# Função para obter o caminho do arquivo mais recente na pasta
def obter_arquivo_mais_recente(diretorio, padrao='entrada_mercadoria_'):
    arquivos = [os.path.join(diretorio, f) for f in os.listdir(diretorio) if f.startswith(padrao) and f.endswith('.xlsx')]
    arquivos.sort(key=os.path.getmtime, reverse=True)  # Ordenar por data de modificação
    return arquivos[0] if arquivos else None

# Diretório onde os arquivos Excel estão armazenados
diretorio_arquivos = 'C:\\Users\\Windows 10\\OneDrive\\entrada_nf\\arquivos'

# Obtendo o caminho do arquivo mais recente
arquivo_mais_recente = obter_arquivo_mais_recente(diretorio_arquivos)

# Verificar se encontrou o arquivo e carregar os dados
if arquivo_mais_recente:
    entrada_nf = pd.read_excel(arquivo_mais_recente)
    st.write(f"Arquivo carregado: {os.path.basename(arquivo_mais_recente)}")
else:
    st.write("Nenhum arquivo encontrado na pasta especificada.")

# Ajuste de datas e preenchimento
entrada_nf['data_entrada'] = pd.to_datetime(entrada_nf['data_entrada'], errors='coerce').dt.date
entrada_nf['data_emissao'] = pd.to_datetime(entrada_nf['data_emissao'], errors='coerce').dt.date  
entrada_nf['data_entrada'] = entrada_nf['data_entrada'].fillna(date.today())

# Filtros na barra lateral
st.sidebar.header('Filtros')
loja = st.sidebar.selectbox('Selecione a Loja:', ['Todas'] + list(entrada_nf['numero_loja'].unique()))
status = st.sidebar.multiselect('Selecione o Status:', ['Todos'] + list(entrada_nf['descricao_status'].unique()))
data_inicio = st.sidebar.date_input('Data de Início', entrada_nf['data_entrada'].min())
data_fim = st.sidebar.date_input('Data de Fim', entrada_nf['data_entrada'].max())

# Função para filtrar dados
def filtrar_dados(df, loja, status, data_inicio, data_fim):
    df_filtrado = df.copy()
    if loja != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['numero_loja'] == loja]
    if 'Todos' not in status and status:
        df_filtrado = df_filtrado[df_filtrado['descricao_status'].isin(status)]
    if data_inicio:
        df_filtrado = df_filtrado[df_filtrado['data_entrada'] >= data_inicio]
    if data_fim:
        df_filtrado = df_filtrado[df_filtrado['data_entrada'] <= data_fim]
    return df_filtrado

# Aplicar filtros
entrada_filtrada = filtrar_dados(entrada_nf, loja, status, data_inicio, data_fim)

# Exibição dos dados filtrados
st.header('Notas Fiscais Filtradas')
st.dataframe(entrada_filtrada)

# Média de dias entre datas por loja
media_dias_por_loja = entrada_filtrada.groupby('numero_loja')['dias_entre_datas'].mean().reset_index()
media_dias_por_loja = media_dias_por_loja[media_dias_por_loja['dias_entre_datas'] >= 4]

st.write('### Lojas com Média de Dias entre Datas Maior ou Igual a 4')
st.dataframe(media_dias_por_loja)

# Visualizações
st.header('Visualizações')

# Gráfico 1: Quantidade de Notas Fiscais por Loja
fig, ax = plt.subplots(figsize=(10, 6))
contagem_por_loja = entrada_filtrada['numero_loja'].value_counts()
bars = sns.barplot(x=contagem_por_loja.index, y=contagem_por_loja.values, ax=ax)

for bar in bars.patches:
    ax.annotate(f'{int(bar.get_height())}', 
                (bar.get_x() + bar.get_width() / 2., bar.get_height()), 
                ha='center', va='bottom', fontsize=10, color='black', 
                xytext=(0, 5), 
                textcoords='offset points')

ax.set_title('Quantidade de Notas Fiscais por Loja')
ax.set_xlabel('Número da Loja')
ax.set_ylabel('Quantidade de Notas Fiscais')
st.pyplot(fig)

# Gráfico 2: Quantidade de Notas Fiscais Distintas por Dia de Emissão
entrada_filtrada['dia_emissao'] = pd.to_datetime(entrada_filtrada['data_emissao'], errors='coerce').dt.day
soma_por_dia = entrada_filtrada.groupby('dia_emissao')['numero_nf'].nunique().reset_index(name='soma_notas')

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='dia_emissao', y='soma_notas', data=soma_por_dia, ax=ax)

for bar in ax.patches:
    ax.annotate(f'{int(bar.get_height())}', 
                (bar.get_x() + bar.get_width() / 2., bar.get_height()), 
                ha='center', va='bottom', fontsize=10, color='black', 
                xytext=(0, 5), 
                textcoords='offset points')

ax.set_title('Quantidade de Notas Fiscais Distintas por Dia')
ax.set_xlabel('Dia do Mês')
ax.set_ylabel('Quantidade de Notas Fiscais')
st.pyplot(fig)

# Gráfico 3: Média de Dias Conferido por Loja
st.header('Média de Dias Conferido por Loja')
media_dias_conferido = entrada_filtrada.groupby('numero_loja')['dias_entre_datas'].mean().reset_index()
media_dias_conferido['media_dias_conferido'] = np.ceil(media_dias_conferido['dias_entre_datas']) 
media_dias_conferido = media_dias_conferido[['numero_loja', 'media_dias_conferido']]

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x='numero_loja', y='media_dias_conferido', data=media_dias_conferido, ax=ax)

for bar in ax.patches:
    ax.annotate(f'{int(bar.get_height())}', 
                (bar.get_x() + bar.get_width() / 2., bar.get_height()), 
                ha='center', va='bottom', fontsize=10, color='black', 
                xytext=(0, 5), 
                textcoords='offset points')

ax.set_title('Média de Dias Conferido por Loja')
ax.set_xlabel('Número da Loja')
ax.set_ylabel('Média de Dias Conferido (Arredondada para Cima)')
st.pyplot(fig)
