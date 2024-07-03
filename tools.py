import pandas as pd
import pymysql

# Define a função de conversão
def convert_int_to_date(date_as_int):
    return pd.to_datetime(str(date_as_int), format='%Y%m%d')

# Define a função para converter inteiros em datetime
def date_parser(date_as_int):
    return pd.to_datetime(str(date_as_int), format='%Y%m%d')

def connection(database):

    db = pymysql.connect(
            host="10.100.0.55",       # Endereço do servidor MySQL
            user="renanrt",    # Seu nome de usuário MySQL
            passwd="Abcd1234",    # Sua senha MySQL
            db=database, # Nome do seu banco de dados
            port=9030
        )

    return db

def formata_velocidade(valor, medida):
    
    return f'{valor} {medida}'

def tratamento_strings(df, coluna):
    df[coluna] = df[coluna].str.strip()
    df[coluna] = df[coluna].apply(lambda x: ' '.join(x.split()))

    return df

def formata_cor(string, color):
    return (f":{color}[{string}]")

def open_process_speed(conn):

    query = "SELECT * FROM speed_km"

    df = pd.read_sql_query(query, conn)

    df['DateasInt'] = df['DateasInt'].apply(convert_int_to_date)

    df = tratamento_strings(df, "DriverFirstName")

    df_divisao = pd.read_sql_query("SELECT * FROM divisao", conn)

    df = pd.merge(df, df_divisao, on='Placa')

    del(df_divisao)

    return df

def process_comercial_time(df):

    df_f = df[(df['DiaSemana']>1) & (df['DiaSemana']<7)]

    df_f = df_f[['DriverFirstName','Horario_Comercial','SomaKm']]

    df_horario_comercial = df_f[df_f['Horario_Comercial']!='FORA DO HORÁRIO COMERCIAL']
    df_fora_comercial = df_f[df_f['Horario_Comercial']=='FORA DO HORÁRIO COMERCIAL']

    df_horario_comercial = df_horario_comercial[['DriverFirstName','SomaKm']]
    df_fora_comercial = df_fora_comercial[['DriverFirstName','SomaKm']]

    final = pd.merge(df_horario_comercial, df_fora_comercial, on='DriverFirstName', how='left')

    final.columns = ["Motorista", "Horario Comercial", "Fora Horario Comercial"]

    final = final.groupby("Motorista")[['Horario Comercial', 'Fora Horario Comercial']].sum().reset_index()

    final['Soma'] = final['Horario Comercial'] + final['Fora Horario Comercial']

    final.sort_values(by='Soma', ascending=False, inplace=True)

    final = final[final['Motorista']!="SEM MOTORISTA"]

    final["% Horario Comercial"] = round(final['Horario Comercial'] / (final['Horario Comercial'] + final['Fora Horario Comercial']), 2)
    final["% Fora Horario Comercial"] = round(final['Fora Horario Comercial'] / (final['Horario Comercial'] + final['Fora Horario Comercial']), 2)

    return final

def process_km_date(df):

    df = df[['DateasInt','Horario_Comercial', 'DiaSemana', 'SomaKm']]

    hc_semana = df[(df['DiaSemana']>1) & (df['DiaSemana']<7) & (df['Horario_Comercial']!='FORA DO HORÁRIO COMERCIAL')]
    hnc_semana = df[(df['DiaSemana']>1) & (df['DiaSemana']<7) & (df['Horario_Comercial']=='FORA DO HORÁRIO COMERCIAL')]

    hc_final_semana = df[((df['DiaSemana']==1) | (df['DiaSemana']==7)) & (df['Horario_Comercial']!='FORA DO HORÁRIO COMERCIAL')]
    hnc_final_semana = df[((df['DiaSemana']==1) | (df['DiaSemana']==7)) & (df['Horario_Comercial']=='FORA DO HORÁRIO COMERCIAL')]

    hc_semana = hc_semana.groupby(['DateasInt'])['SomaKm'].sum().reset_index()
    hnc_semana = hnc_semana.groupby(['DateasInt'])['SomaKm'].sum().reset_index()

    hc_final_semana = hc_final_semana.groupby(['DateasInt'])['SomaKm'].sum().reset_index()
    hnc_final_semana = hnc_final_semana.groupby(['DateasInt'])['SomaKm'].sum().reset_index()

    semana = pd.merge(hc_semana, hnc_semana, on='DateasInt')
    semana.columns = ['Data', 'HC Semana', 'HNC Semana']

    final_semana = pd.merge(hc_final_semana, hnc_final_semana, on='DateasInt')
    final_semana.columns = ['Data', 'HC Final Semana', 'HNC Final Semana']

    final = pd.merge(semana, final_semana, on='Data', how='outer')

    final.fillna(0, inplace=True)

    final.sort_values(by='Data', ascending=True, inplace=True)

    return final

# Função para converter um valor em numérico (inteiro ou float), tratando erros
def convert_to_numeric(value):
    try:
        return int(value)  # Tentar converter para inteiro
    except (ValueError, TypeError):
        try:
            return float(value)  # Tentar converter para float se inteiro falhar
        except (ValueError, TypeError):
            return pd.NA  # Retornar NaN se a conversão falhar

def medias_desempenho(df, coluna):
    # Converter os valores da coluna para float
    df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

    df = df[df[coluna]!=0]
    
    # Calcular a média da coluna convertida
    media = df[coluna].mean()
    
    if pd.isna(media):  # Verifica se a média é NaN
        media = None  # Atribui None se for NaN
    else:
        media = round(media, 0)  # Arredonda a média para 2 casas decimais
    
    return int(media)
