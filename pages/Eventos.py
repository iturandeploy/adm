from tools_st import StreamlitApp
from tools import connection
import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
from graphics import simple_pie, bar_plot

app = StreamlitApp()

app.header_principal('EVENTOS')

#########################################################################################################################################
conn = connection('adm')
query = 'SELECT * FROM eventos'

df = pd.read_sql_query(query, conn)
####################################################################################################################################################################

st.sidebar.title('Filtros')
# Converter data_min e data_max para datetime64[ns]
data_min = df['event_datetime'].min()
data_max = df['event_datetime'].max()

today = datetime.datetime.now().date()

min_date = today - timedelta(days=30)
with st.sidebar.expander("Datas"):
    data_min_input = st.date_input("Data Inicial", min_date)
    data_max_input = st.date_input("Data Final", today)

data_min_datetime = pd.to_datetime(data_min_input)
data_max_datetime = pd.to_datetime(data_max_input)

df_filtered = df[(df['event_datetime'] >= data_min_datetime) & (df['event_datetime'] <= data_max_datetime)]
#print(df_filtered)

with st.sidebar.expander("Motorista"):
    lista_motoristas = list(df_filtered['driver_name'].unique())
    lista_motoristas.sort()
    motoristas = st.multiselect("Selecione um ou mais motoristas", lista_motoristas)

    if motoristas:
        df_filtered = df_filtered[df_filtered['driver_name'].isin(motoristas)]

with st.sidebar.expander("Evento"):
    lista_eventos = list(df_filtered['event_name'].unique())
    lista_eventos.sort()
    events = st.multiselect("Selectine um ou mais eventos", lista_eventos)

    if events:
        df_filtered = df_filtered[df_filtered['event_name'].isin(events)]

##################################################################################################################################
count_events = list(set(list(df_filtered['trip_event_id'])))
# print(len(count_events))
qtd_events = len(count_events)

df_events = df_filtered.groupby(['event_name'])['trip_event_id'].count().reset_index().sort_values(by='trip_event_id', ascending=False)
df_events = df_events.head(5)

soma = df_events['trip_event_id'].sum()

novo = []
for index, row in df_events.iterrows():
    row['Percentual'] = round(row['trip_event_id'] / soma,4)
    novo.append(row)

df_events = pd.DataFrame(novo)
print(df_events)

top5 = list(df_events['event_name'])

fig = simple_pie(labels=df_events['event_name'], values=df_events['Percentual'])

c1, c2 = st.columns(2)

with c1:
    st.subheader("Percentual TOP 5 Eventos")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    cc1, cc2, cc3 = st.columns(3)
    with cc2:
        st.subheader("Quantidade de Eventos")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.metric('', qtd_events)
st.subheader('', divider='rainbow')
#############################################################################################################################################################

st.subheader("TOP 5 Eventos por Período")

top5_events = df_filtered[df_filtered['event_name'].isin(top5)]

top5_events['event_datetime'] = pd.to_datetime(top5_events['event_datetime'])
top5_events['data'] = top5_events['event_datetime'].dt.date

final = top5_events.groupby(['data','event_name'])['event_name'].count().reset_index(name='Contagem')

final.columns = ['Data','Evento','Contagem']

#print(final)

fig = bar_plot(final, 'Data','Contagem','Evento','v','','Data','Quantidade de Eventos')

st.plotly_chart(fig, use_container_width=True)
st.subheader('', divider='rainbow')
#############################################################################################################################################################

top_motoristas = df_filtered[['driver_name','event_name']]

top_motoristas = top_motoristas.groupby(['driver_name','event_name'])['event_name'].count().reset_index(name='Contagem')

contagem_eventos_motoristas = top_motoristas.groupby(['driver_name'])['Contagem'].sum().reset_index().sort_values(by='Contagem',ascending=False)
contagem_eventos_motoristas = contagem_eventos_motoristas[~contagem_eventos_motoristas['driver_name'].str.startswith('Motorista')]
contagem_eventos_motoristas = contagem_eventos_motoristas[contagem_eventos_motoristas['driver_name']!='Sem motorista']

top10_motoristas = contagem_eventos_motoristas.head(10)
minimo_inf = contagem_eventos_motoristas['Contagem'].min()
tail10_motoristas = contagem_eventos_motoristas[contagem_eventos_motoristas['Contagem']==minimo_inf]

lista_top10 = list(top10_motoristas['driver_name'].unique())
lista_tail10 = list(tail10_motoristas['driver_name'].unique())

top10_motoristas = top_motoristas[top_motoristas['driver_name'].isin(lista_top10)]
tail10_motoristas = top_motoristas[top_motoristas['driver_name'].isin(lista_tail10)]

c1, c2 = st.columns(2)

fig_top10 = bar_plot(top10_motoristas, "Contagem", "driver_name","event_name", "h", "", "Motoristas", "Quantidade")
fig_tail10 = bar_plot(tail10_motoristas, "Contagem", "driver_name","event_name", "h", "", "Quantidade","Motoristas")

with c1:
    st.subheader("TOP 10 MOTORISTAS COM MAIS EVENTOS")
    st.plotly_chart(fig_top10, use_container_width=True)

with c2:
    st.subheader("TOP MOTORISTAS COM MENOS EVENTOS")
    st.plotly_chart(fig_tail10, use_container_width=True)

st.subheader('', divider='rainbow')

