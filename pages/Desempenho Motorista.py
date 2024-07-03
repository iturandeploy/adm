from tools_st import StreamlitApp
import streamlit as st
from tools import medias_desempenho, convert_to_numeric, connection
import pandas as pd
import datetime
from datetime import timedelta
from graphics import simple_bar
import plotly.express as px

app = StreamlitApp()

app.header_principal('DESEMPENHO MOTORISTA')

query = 'SELECT * FROM desempenho_drivers'
conn = connection('adm')

df = pd.read_sql_query(query, conn)
print(df)

df.fillna(0, inplace=True)

###

#####################################################################################################################################################

# Converter data_min e data_max para datetime64[ns]
data_min = df['data_nota'].min()
data_max = df['data_nota'].max()

st.sidebar.title('Filtros')

today = datetime.datetime.now().date()

min_date = today - timedelta(days=30)
with st.sidebar.expander("Datas"):
    data_min_input = st.date_input("Data Inicial", min_date)
    data_max_input = st.date_input("Data Final", today)

data_min_datetime = pd.to_datetime(data_min_input)
data_max_datetime = pd.to_datetime(data_max_input)

df['data_nota'] = pd.to_datetime(df['data_nota'])

df_filtered = df[(df['data_nota'] >= data_min_datetime) & (df['data_nota'] <= data_max_datetime)]
print(df_filtered)

with st.sidebar.expander("Motorista"):
    motoristas = st.multiselect("Selecione um ou mais motoristas", list(df_filtered['motorista'].unique()))

    if motoristas:

        df_filtered = df_filtered[df_filtered['motorista'].isin(motoristas)]

try:

    # Substitua valores vazios na coluna 'safety_grade' por NaN
    df_filtered['safety_grade'] = df_filtered['safety_grade'].replace('', pd.NA)

    # Converta para tipo numérico
    df_filtered['safety_grade'] = pd.to_numeric(df_filtered['safety_grade'], errors='coerce').astype('Int64')



    #####################################################################################################################################################


    # Converter para tipo numérico
    df_filtered['safety_grade'] = pd.to_numeric(df_filtered['safety_grade'], errors='coerce').astype('float')

    # Calcular médias apenas se houver valores numéricos válidos
    filtro_safety = df_filtered['safety_grade'].dropna()
    filtro_safety = filtro_safety[filtro_safety != 0]

    # Verificar se há valores numéricos válidos antes de calcular a média
    media_safety = round(filtro_safety.mean(), 2) if not filtro_safety.empty else None

    # Exemplo similar para media_economia e media_score
    # Converter para tipo numérico
    df_filtered['fuel_grade'] = pd.to_numeric(df_filtered['fuel_grade'], errors='coerce').astype('float')

    # Calcular médias apenas se houver valores numéricos válidos
    filtro_fuel = df_filtered['fuel_grade'].dropna()
    filtro_fuel = filtro_fuel[filtro_fuel != 0]

    # Verificar se há valores numéricos válidos antes de calcular a média
    media_economia = round(filtro_fuel.mean(), 2) if not filtro_fuel.empty else None

    # Calcular media_score (média entre media_safety e media_economia)
    media_score = round((media_safety + media_economia) / 2, 2) if media_safety is not None and media_economia is not None else None

    total_km = df_filtered['total_km'].sum()

    # Atualize seus st.metric chamados para usar valores aceitáveis
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader('Média Nota Segurança :vertical_traffic_light:')
        st.metric('', media_safety)

    with col2:
        st.subheader('Média Score :sports_medal:')
        st.metric('', media_score)

    with col3:
        st.subheader("Média Nota Economia :fuelpump:")
        st.metric('', media_economia)

    with col4:
        st.subheader("Km Período  :oncoming_automobile:")
        st.metric('', total_km)

    st.subheader('', divider='rainbow')
    #####################################################################################################################################################
    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

    speed_grade = medias_desempenho(df_filtered, "speed_grade")
    acc_grade = medias_desempenho(df_filtered, "acceleration_grade")
    brakes_grade = medias_desempenho(df_filtered, "brakes_grade")
    bypass_grade = medias_desempenho(df_filtered, "bypass_grade")
    left_grade = medias_desempenho(df_filtered, "left_grade")
    right_grade = medias_desempenho(df_filtered, "right_grade")
    curve_grade = medias_desempenho(df_filtered, "curve_grade")

    with c1:
        with st.container(height=70, border=False):
            st.subheader("Velocidade")
        with st.container():
            st.metric("", speed_grade)

    with c2:
        with st.container(height=70, border=False):
            st.subheader("Aceleração")
        with st.container():
            st.metric("", acc_grade)


    with c3:
        with st.container(height=70, border=False):
            st.subheader("Frenagens")
        with st.container():
            st.metric("", brakes_grade)

    with c4:
        with st.container(height=70, border=False):
            st.subheader("Ultrapassagens")
        with st.container():
            st.metric("", bypass_grade,label_visibility='hidden')

    with c5:
        with st.container(height=70, border=False):
            st.subheader("Curva à esquerda")
        with st.container():
            st.metric("", left_grade)

    with c6:
        with st.container(height=70, border=False):
            st.subheader("Curva à direita")
        with st.container():
            st.metric("", right_grade)

    with c7:
        with st.container(height=70, border=False):
            st.subheader("Mudança de Faixa")
        with st.container():
            st.metric("", curve_grade)

    st.subheader('', divider='rainbow')

    #################################################################################################################
    fuel_grade = medias_desempenho(df_filtered, 'fuel_grade')
    safety_grade = medias_desempenho(df_filtered, 'safety_grade')

    df_speed = df_filtered[df_filtered['speed_grade']!=0].groupby(['data_nota'])['speed_grade'].mean().reset_index()

    df_fuel = df_filtered[df_filtered['fuel_grade']!=0].groupby(['data_nota'])['fuel_grade'].mean().reset_index()
    df_safety = df_filtered[df_filtered['safety_grade']!=0].groupby(['data_nota'])['safety_grade'].mean().reset_index()
    df_left = df_filtered[df_filtered['left_grade']!=0].groupby(['data_nota'])['left_grade'].mean().reset_index()
    df_right = df_filtered[df_filtered['right_grade']!=0].groupby(['data_nota'])['right_grade'].mean().reset_index()
    df_curve = df_filtered[df_filtered['curve_grade']!=0].groupby(['data_nota'])['curve_grade'].mean().reset_index()
    df_brakes = df_filtered[df_filtered['brakes_grade']!=0].groupby(['data_nota'])['brakes_grade'].mean().reset_index()
    df_acc = df_filtered[df_filtered['acceleration_grade']!=0].groupby(['data_nota'])['acceleration_grade'].mean().reset_index()
    df_bypass = df_filtered[df_filtered['bypass_grade']!=0].groupby(['data_nota'])['bypass_grade'].mean().reset_index()

    fig_velocidade = simple_bar(df_speed, 'data_nota', 'speed_grade', speed_grade)
    fig_fuel = simple_bar(df_fuel, 'data_nota','fuel_grade', fuel_grade)
    fig_safety = simple_bar(df_safety, 'data_nota', 'safety_grade', safety_grade)
    fig_left = simple_bar(df_left, 'data_nota', 'left_grade', left_grade)
    fig_right = simple_bar(df_right, 'data_nota', 'right_grade', right_grade)
    fig_curve = simple_bar(df_curve, 'data_nota', 'curve_grade', curve_grade)
    fig_brakes = simple_bar(df_brakes, 'data_nota', 'brakes_grade', brakes_grade)
    fig_acc = simple_bar(df_acc, 'data_nota', 'acceleration_grade', acc_grade)
    fig_bypass = simple_bar(df_bypass, 'data_nota', 'bypass_grade', bypass_grade)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("Velocidade")
        st.plotly_chart(fig_velocidade, use_container_width=True)
        st.markdown("")
        st.markdown("Curva à Esquerda")
        st.plotly_chart(fig_left, use_container_width=True)
        st.markdown("")
        st.markdown("Frenagens")
        st.plotly_chart(fig_brakes, use_container_width=True)

    with c2:
        st.markdown("Nota de Economia")
        st.plotly_chart(fig_fuel, use_container_width=True)
        st.markdown("")
        st.markdown("Curva à Direita")
        st.plotly_chart(fig_right, use_container_width=True)
        st.markdown("")
        st.markdown("Aceleração")
        st.plotly_chart(fig_acc, use_container_width=True)

    with c3:
        st.markdown("Nota de Segurança")
        st.plotly_chart(fig_safety, use_container_width=True)
        st.markdown("")
        st.markdown("Mudança Faixa")
        st.plotly_chart(fig_curve, use_container_width=True)
        st.markdown("")
        st.markdown("Ultrapassagens")
        st.plotly_chart(fig_bypass, use_container_width=True)

    st.subheader('', divider='rainbow')
    #################################################################################################################
    df_formatado = df_filtered[['driverid', 'motorista','total_km', 'safety_grade', 'fuel_grade']]
    df_formatado['score'] = round((df_formatado['safety_grade']+df_formatado['fuel_grade'])/2,2)

    drivers = df_formatado[['driverid', 'motorista']]
    drivers.drop_duplicates(inplace=True)

    score = df_formatado[df_formatado['score']!=0].groupby(['driverid'])['score'].mean().reset_index()

    total = df_formatado[df_formatado['total_km']!=0].groupby(['driverid'])['total_km'].sum().reset_index()

    final = pd.merge(drivers, total, on='driverid', how='left')
    final = pd.merge(final, score, on='driverid', how='left')
    final.sort_values(by='motorista', inplace=True)

    print(final)

    final.columns = ['DRIVER ID', 'MOTORISTA', 'TOTAL KM','SCORE']
    final.fillna(0,inplace=True)

    final = final[(final['SCORE']!=0) & (final['TOTAL KM']!=0)]
    final['SCORE'] = round(final['SCORE'],2)

    c1, c2 = st.columns(2)
    st.subheader('', divider='rainbow')

    print(f'O dataframe filtrado no momento é:')
    print(df_filtered)

    motorista = df_filtered[df_filtered['total_km']!=0].groupby(['motorista'])['total_km'].sum().reset_index()
    nota_seguranca = df_filtered[df_filtered['safety_grade']!=0].groupby(['motorista'])['safety_grade'].sum().reset_index()
    media_seguranca = df_filtered[df_filtered['safety_grade']!=0].groupby(['motorista'])['safety_grade'].mean().reset_index()

    final_motorista = pd.merge(motorista, nota_seguranca, on='motorista', how='left')
    final_motorista = pd.merge(final_motorista, media_seguranca, on='motorista', how='left')

    final_motorista.columns = ['Motorista', 'Km Total', 'Nota Segurança', 'Média Segurança']

    # Converter para numérico, se necessário
    final_motorista['Km Total'] = pd.to_numeric(final_motorista['Km Total'], errors='coerce')
    final_motorista['Nota Segurança'] = pd.to_numeric(final_motorista['Nota Segurança'], errors='coerce')
    final_motorista['Média Segurança'] = pd.to_numeric(final_motorista['Média Segurança'], errors='coerce')

    # Verificar e tratar valores nulos ou infinitos
    final_motorista = final_motorista.dropna()

    print(final_motorista)

    with c1:
        # Gráfico simples
        fig = px.scatter(final_motorista, x='Km Total', y='Nota Segurança', size='Média Segurança', hover_name='Motorista',
                         title='Relação da Soma de KM Percorrido pela soma da Nota de Segurança',
                         color='Média Segurança',
                         color_continuous_scale=px.colors.sequential.RdBu)
        st.plotly_chart(fig)
    with c2:
        final.sort_values(by='SCORE', ascending=False, inplace=True)
        st.dataframe(final, hide_index=True)
    #################################################################################################################

except:
    st.title("Não há dados para exibir com as datas filtradas!")