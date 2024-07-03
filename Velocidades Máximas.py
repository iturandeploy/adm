import streamlit as st
import pandas as pd
from tools import connection, formata_velocidade, open_process_speed
from functions import infractions_top5
import datetime
from datetime import timedelta
from tools_st import StreamlitApp
from graphics import graph_bar, graph_histogram
import numpy as np

st.set_page_config(layout='wide')

app = StreamlitApp()

app.header_principal('VELOCIDADES MÁXIMAS')

conn = connection('adm')

df = open_process_speed(conn)

# df = df[(df['DriverFirstName']!="Sem Motorista") & (df['DriverFirstName']!="SEM MOTORISTA")]

# Converter data_min e data_max para datetime64[ns]
data_min = df['DateasInt'].min()
data_max = df['DateasInt'].max()

df['DateasInt'] = pd.to_datetime(df['DateasInt'], format='%Y%m%d')
df['MaxSpeed'] = pd.to_numeric(df['MaxSpeed'], errors='coerce')
df['SomaKm'] = pd.to_numeric(df['SomaKm'], errors='coerce')
df['FlExcesso'] = pd.to_numeric(df['FlExcesso'], errors='coerce')
df['FlSeco'] = pd.to_numeric(df['FlSeco'], errors='coerce')
df['FlMolhado'] = pd.to_numeric(df['FlMolhado'], errors='coerce')

st.sidebar.title('Filtros')

today = datetime.datetime.now().date()
min_date = today - timedelta(days=30)
with st.sidebar.expander("Datas"):
    data_min_input = st.date_input("Data Inicial", min_date)
    data_max_input = st.date_input("Data Final", today)

# Converter data_min_input e data_max_input para datetime64[ns]
data_min_datetime = pd.to_datetime(data_min_input)
data_max_datetime = pd.to_datetime(data_max_input)

# Aplicar os filtros com as datas convertidas
df_filtered = df[(df['DateasInt'] >= data_min_datetime) & (df['DateasInt'] <= data_max_datetime)]

with st.sidebar.expander("Divisão"):
    options = st.multiselect("Selecione uma ou mais opções", ['Todos', 'Comercial', 'Operacional'])

    if 'Todos' in options or len(options) == 0:
        # Se 'Todos' estiver selecionado ou nenhum filtro for aplicado
        pass
    else:
        # Aplicar filtro com base nas opções selecionadas
        df_filtered = df_filtered[df_filtered['Divisao'].isin(options)]

with st.sidebar.expander("Motoristas"):
    motoristas = st.multiselect("Selecione um ou mais motoristas", list(df_filtered['DriverFirstName'].unique()))
    print(motoristas)

    if motoristas:
        print(f'O MOTORISTA É {motoristas}')
        df_filtered = df_filtered[df_filtered['DriverFirstName'].isin(motoristas)]

with st.sidebar.expander("Placa"):
    placas = st.multiselect("Selecione uma ou mais placas", df_filtered['Placa'].unique())

    if placas:
        df_filtered = df_filtered[df_filtered['Placa'].isin(placas)]


##################################################################################################################################

print(f'A maior velocidade encontrada no dataframe filtrado foi de {df_filtered["MaxSpeed"].max()} Km/h e foi do seguinte motorista: {df_filtered[df_filtered["MaxSpeed"]==df_filtered["MaxSpeed"].max()]["DriverFirstName"].values[0]}')

df_formatado = pd.DataFrame({
        "Ano":df_filtered['DateasInt'].dt.year.astype(str),
        "Mês":df_filtered['DateasInt'].dt.month,
        "Dia":df_filtered['DateasInt'].dt.day,
        "Placa":df_filtered['Placa'],
        "Motorista":df_filtered['DriverFirstName'],
        "Max Velocidade":df_filtered['MaxSpeed']
    })

df_formatado = df_formatado[df_formatado['Max Velocidade']>0]
df_formatado.sort_values(by='Max Velocidade', ascending=False, inplace=True)


#################################################################################################################################

# Filtro de Infrações

top_5_motoristas_long = infractions_top5(df_filtered)
fig = graph_bar(top_5_motoristas_long, "Total", "DriverFirstName",
                "Total de Infrações por Motorista (FlSeco e FlMolhado)",
                "Total de Infrações", "Motorista",
                "Tipo de Infração")


#################################################################################################################################
fig_inf_dia = graph_histogram(df_filtered, "DateasInt", ["FlSeco", "FlMolhado"], "Total de Infrações", "Data", "Quantidade por Período e Clima")

#################################################################################################################################

col1, col2, = st.columns(2, gap='small')

# Métricas Velocidade

#df_filtered.to_excel('teste.xlsx', index=False)

filtro_seco = df_filtered[df_filtered['FlSeco'] != 0]
#filtro_seco.to_excel("filtro_seco.xlsx", index=False)
print(filtro_seco)
filtro_molhado = df_filtered[df_filtered['FlMolhado'] != 0]
print(filtro_molhado)
#filtro_molhado.to_excel("filtro_molhado.xlsx", index=False)

vel_max = df_filtered['MaxSpeed'].max()

vel_max_seco = filtro_seco['MaxSpeed'].max()
print(f'A velocidade máxima no seco foi de {vel_max_seco}')
vel_max_molh = filtro_molhado['MaxSpeed'].max()
print(f'A velocidade máxima no molhado foi de {vel_max_molh}')

print(f'Comparação para saber se vel_max_seco = nan: {np.isnan(vel_max_seco)}')

#container = st.container(border=True)
# if len(filtro_seco)!=0 and len(filtro_molhado)!=0:
with col1:
    if np.isnan(vel_max_molh):
        st.subheader(":blue[Molhado] :thunder_cloud_and_rain:")
        st.metric('', formata_velocidade(0, "Km/h"))
    else:
        st.subheader(":blue[Molhado] :thunder_cloud_and_rain:")
        st.metric('', formata_velocidade(vel_max_molh, "Km/h"))
        
with col2:
    if np.isnan(vel_max_seco):
        st.subheader(":orange[Seco] :sunny:")
        st.metric('', formata_velocidade(vel_max, "Km/h"))
    else:
        st.subheader(":orange[Seco] :sunny:")
        st.metric('', formata_velocidade(vel_max_seco, "Km/h"))
# else:
#     st.subheader("A velocidade máxima encontrada sem especificação de condições de pista seca ou molhada foi")
#     st.metric('', formata_velocidade(vel_max, "Km/h"))

st.subheader('',divider='rainbow')

c1, c2 = st.columns(2)
with st.container():
    with c1:
        st.dataframe(df_formatado, hide_index=True)

    with c2:
        st.markdown("TESTE")

st.subheader('', divider='rainbow')

col1_1, col1_2 = st.columns(2)

with col1_1:
    # st.dataframe(infracoes_motoristas, hide_index=True)
    st.plotly_chart(fig, use_container_width=True)

with col1_2:
    st.markdown('TESTE2')
    
st.subheader('', divider='rainbow')

st.plotly_chart(fig_inf_dia, use_container_width=True)

st.subheader('', divider='rainbow')

 ##################################################################################################################################################

st.dataframe(df_filtered, hide_index=True)