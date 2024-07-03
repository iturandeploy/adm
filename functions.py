import pandas as pd

def infractions_top5(df_filtered):


    # Agrupar e somar as infrações por motorista
    infracoes_motoristas = df_filtered.groupby(['DriverFirstName'])[['FlSeco', 'FlMolhado']].sum().reset_index()

        # Remover motorista 'SEM MOTORISTA'
    infracoes_motoristas = infracoes_motoristas[infracoes_motoristas['DriverFirstName'] != 'SEM MOTORISTA']

        # Ordenar por FlSeco em ordem decrescente
    infracoes_motoristas = infracoes_motoristas.sort_values(by='FlSeco', ascending=False)

        # Selecionar os top 5 motoristas com mais infrações (FlSeco)
    top_5_motoristas = infracoes_motoristas.head(5)

        # Reverter a ordem dos dados para que o motorista com mais infrações apareça primeiro
    top_5_motoristas = top_5_motoristas[::-1]

        # Transformar os dados em formato longo (tidy format) para o gráfico de barras empilhadas
    top_5_motoristas_long = top_5_motoristas.melt(id_vars=['DriverFirstName'], 
                                                    value_vars=['FlSeco', 'FlMolhado'], 
                                                    var_name='Tipo', 
                                                    value_name='Total')
    
    return top_5_motoristas_long