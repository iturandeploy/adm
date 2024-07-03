from tools_st import StreamlitApp
import streamlit as st
from tools import connection, convert_int_to_date, formata_velocidade, process_comercial_time, process_km_date
import pandas as pd
import datetime
from datetime import timedelta
from graphics import graph_bar

app = StreamlitApp()

app.header_principal('CONDUÇÃO PERÍODO')
###########################################################################################

conn = connection('adm')

speed = pd.read_sql_query(f"select * from speed_km", conn)

speed['DateasInt'] = speed['DateasInt'].apply(convert_int_to_date)

###########################################################################################

data_min = speed['DateasInt'].min()
data_max = speed['DateasInt'].max()

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
df_filtered = speed[(speed['DateasInt'] >= data_min_datetime) & (speed['DateasInt'] <= data_max_datetime)]


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




#############################################################################################
st.subheader("Distância Percorrida")

col1, col2 = st.columns(2)

soma = round(df_filtered['SomaKm'].sum(),2)

ipkm = df_filtered[df_filtered['DateasInt']>='20200101']

with col1:
    st.subheader("IPKM")

with col2:
    st.subheader("Total Km")
    st.metric('', formata_velocidade(soma, "Km"))

#############################################################################################
st.subheader('', divider='rainbow')
st.subheader("Distância Percorrida por Período")
c1, c2, c3 = st.columns(3)

durante_semana = df_filtered[(df_filtered['DiaSemana']>1) & (df_filtered['DiaSemana']<7)]
fim_semana = df_filtered[(df_filtered['DiaSemana']==1) | (df_filtered['DiaSemana']==7)]

horario_comercial_durante = durante_semana[durante_semana['Horario_Comercial']!='FORA DO HORÁRIO COMERCIAL']
fora_comercial_durante = durante_semana[durante_semana['Horario_Comercial']=='FORA DO HORÁRIO COMERCIAL']

horario_comercial_fim = fim_semana[fim_semana['Horario_Comercial']!='FORA DO HORÁRIO COMERCIAL']
fora_comercial_fim = fim_semana[fim_semana['Horario_Comercial']=='FORA DO HORÁRIO COMERCIAL']

sum_horario_comercial_durante = round(horario_comercial_durante['SomaKm'].sum(),2)
sum_fora_comercial_durante = round(fora_comercial_durante['SomaKm'].sum(),2)

sum_horario_comercial_fim = round(horario_comercial_fim['SomaKm'].sum(),2)
sum_fora_comercial_fim = round(fora_comercial_fim['SomaKm'].sum(),2)

with c1:
    st.subheader("")
    st.subheader("")
    st.subheader("")
    st.subheader("Horário Comercial")
    st.subheader("")
    st.markdown("")
    st.subheader("Fora Horário Comercial")

with c2:
    st.subheader(":blue[Durante a Semana]")
    st.metric('',formata_velocidade(sum_horario_comercial_durante, "Km"))
    st.metric('',formata_velocidade(sum_fora_comercial_durante, "Km"))

with c3:
    st.subheader(":green[Final de Semana]")
    st.metric('', formata_velocidade(sum_horario_comercial_fim, "Km"))
    st.metric('', formata_velocidade(sum_fora_comercial_fim, "Km"))


#############################################################################################

# GRÁFICOS

motoristas = process_comercial_time(df_filtered)

top_5 = motoristas.head(4)

fig1 = graph_bar(top_5, ["% Horario Comercial", "% Fora Horario Comercial"], 'Motorista', "", "Percentual", "Motorista", "")

placa = df_filtered.groupby(["Placa"])['SomaKm'].sum().reset_index()
placa.sort_values(by="SomaKm", ascending=False, inplace=True)
print(placa)
placa = placa.head(7)

fig2 = graph_bar(placa, "SomaKm", "Placa", "", "", "Placa", "")

km_date = process_km_date(df_filtered)

import plotly.express as px

fig3 = px.area(km_date, x='Data', y=['HC Semana',  'HNC Semana',  'HC Final Semana',  'HNC Final Semana'])

#############################################################################################

st.subheader('', divider='rainbow')

c1, c2 = st.columns(2)

with c1:
    st.subheader("KM por Período Semana")
    st.plotly_chart(fig1, use_container_width=True)
with c2:
    st.subheader("KM por Placa")
    st.plotly_chart(fig2, use_container_width=True)



#############################################################################################
st.subheader('', divider='rainbow')
st.plotly_chart(fig3, use_container_width=True)
#st.dataframe(km_date, hide_index=True)

