import plotly.express as px
import plotly.graph_objects as go

def graph_bar(df, xaxis, yaxis, title, xaxis_title, yaxis_title, legend_title):

    fig = px.bar(df, 
                x=xaxis,
                y=yaxis,
                orientation='h',
                barmode='stack',
                title=title,
                color_discrete_sequence=['blue','yellow'])
    
    fig.update_layout(xaxis_title=xaxis_title,
                    yaxis_title=yaxis_title,
                    legend_title=legend_title,
                    height=400)
    
    return fig

def graph_histogram(df, xaxis, yaxis, xaxis_title, yaxis_title, legend_title):
    fig = px.histogram(
        df, 
        x=xaxis, 
        y=yaxis, 
        barmode='group',
        color_discrete_sequence=['blue', 'yellow']
    )

    # Atualize o layout do gráfico
    fig.update_layout(
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        legend_title=legend_title,
        height=400,
        showlegend=False
    )

    return fig

def simple_pie(labels, values):

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.7, showlegend=True)])
    return fig

def simple_bar(df, x, y, media):
    fig = px.bar(data_frame=df, x=x, y=y)

    fig.update_layout(showlegend=False,
                      xaxis_title='',
                      yaxis_title='',
                      title=f'Linha média: {media}',
                      yaxis=dict(range=[0, 100]))

    return fig


def bar_plot(df, x, y, color, orientation, title, xtitle, ytitle):

    fig = px.bar(data_frame=df, x=x, y=y, color=color, orientation=orientation)

    fig.update_layout(
        title=title,
        xaxis_title=xtitle,
        yaxis_title=ytitle
    )

    return fig