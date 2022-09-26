import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd
import json

CENTER_LAT, CENTER_LON = -15.79943891899545, -47.89949674558088

# df = pd.read_csv("HIST_PAINEL_COVIDBR_2022_Parte1_12jun2022.csv", sep=";")
# df_states = df[(~df["estado"].isna()) & (df["codmun"].isna())] 
# df_brasil = df[df["regiao"] == "Brasil"]
# df_states.to_csv("df_states.csv")
# df_brasil.to_csv("df_brasil.csv")

df_states = pd.read_csv("df_states.csv")
df_brasil = pd.read_csv("df_brasil.csv")

df_states_ = df_states[df_states["data"] == "2022-06-01"]
#<<<<<LATIDODES E LONGITUDES DOS ESTADOS BRASILEIROS/DIVISAS>>>>>>
brazil_states = json.load(open("geojson/brazil_geo.json", "r"))
df_data = df_states[df_states["estado"] == "DF"]

select_columns = {'casosAcumulado':" Casos Acumulados",
                 'casosNovos': "Novos casos", 
                 'obitosAcumulado': "Óbitos Acumulados",
                 'obitosNovos': "Óbitos por dia"}


#----DESCOBRINDO AS CHAVES E ANALIZANDOS OS DADOS.----
# type(brazil_states)
# brazil_states.keys()
# brazil_states["type"]
# brazil_states["features"]
#A CHAVE FEATURES SÃO OS DADOS QUE QUERO!

#-------ANALIZANDO A CHAVE FEATURES:A CARA DO ARQUIVO.GEOJSON
# type(brazil_states["features"]) Lista
# type(brazil_states["features"][0]) Dict
# brazil_states["features"][0].keys() DESCOBRINDO AS CHAVES DO DICIONÁRIO
# brazil_states["features"][0]["id"] #LE É UMA INFORMAÇÃO QUE IREMOS UTILIZAR NA CRIAÇÃO DO MAPA, PARA IDENTIFICAR, PARA CADA UM DESSES ELEMENTOS, QUAL QUE É O IDENTIFICADOR QUE ELE TEM. É PRECISO CASAR ESSAS ESPECIFICAÇÕES GEOMETRICAS DO MAPA COM AS INFORMAÇÕES NO MEU DADO. PRECISA TER ALGUM VALOR EM COMUM COM O ARQUIVO.CSV PARA QUE O GRAFICO SEJA CRIADO DA FORMA ADEQUADA, E QUE POSSAMOS COLORIR CADA UM DOS ESTADOS EM FUNÇÃO DA INFORMAÇÃO QUE SERÁ MOSTRADO.
# brazil_states["features"][0]["geometry"]  ELE VAI TER UMA SÉRIE DE PONTOS AONDE ELE MOSTRA TODAS A LATITUDES E LONGITUDES DAS DIVISÕES DO MAPA.
# EM RESUMO: É NECESSARIO SABER O ID E A GEOMETRICA PARA CASAR COM O DATAFRAME QUE SERÁ PINTADO. 


#<<<<<<<<<< CRIAÇÃO DO MAPA!!! >>>>>>>>>> 
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG]) #Aqui dentro será o Dashboard. O dbc será usado para estilizar o dashboard

fig = px.choropleth_mapbox (df_states_, locations="estado", color="casosNovos",
                        center={"lat": -15.79943891899545, "lon": -47.89949674558088}, zoom=4, 
                        geojson=brazil_states, color_continuous_scale="Redor", opacity=0.4,
                        hover_data={"casosAcumulado": True, "casosNovos": True, "obitosNovos": True, "estado": True}) #VAI CONTER O GRÁFICO DO MAPA! Mapas do choropleth é do tipo que tem as divisões coloridas nos mapas, onde se mostra uma outra informação. Mapbox é uma api externa que cria graficos visualmente mais bonitos.
fig.update_layout(
    paper_bgcolor="#242424",
    autosize=True,
    margin=go.Margin(l=0, r=0, t=0, b=0),
    showlegend=False,
    mapbox_style="carto-darkmatter"
) #Colorindo e centralizando o mapa, sem bordas brancas. 


#<<<<CRIANDO O GRAFICO DE BARRAS QUE FICA POR BAIXO
fig2 = go.Figure(layout={"template": "plotly_dark"})
fig2.add_trace(go.Scatter(x=df_data["data"], y=df_data["casosAcumulado"]))
fig2.update_layout(
        paper_bgcolor="#242424",
        plot_bgcolor="#242424",
        autosize=True,
        margin=dict(l=10, r=10, t=10, b=10)
)

#<<<<<<<<<<<< CONSTRUÇÃO DO LAYOUT!! >>>>>>>>>>>>>
#A FORMA UTILIZADA É A DA BOOTSTRAP DO DASH,NA PARTE DE LAYOUT NA DOCUMENTAÇÃO, USANDO UM SISTEMA DE DIVITE A TELA EM 12, PODENDO USAR FRAÇÕES DISSO. 
#É PRECISO 3 FUNÇÕES BASICAS: Container, Row e Col

app.layout = dbc.Container(
    dbc.Row([        
        dbc.Col([
            html.Div([
                html.Img(id="logo", src=app.get_asset_url("biomedicina-logo-9980D97C53-seeklogo.com.png"), height=60), #LOGO DA BIOMEDICINA NO CANTO SUPERIOR ESQUERDO
                html.Img(id="logo1", src=app.get_asset_url("c-UDF.png"), height=100), #LOGO DA UDF
                html.Img(id="logo2", src=app.get_asset_url("logo_dark.png"), height=60), #LOGO DO ASIMOV ACADEMY
                html.H5("Evolução da COVID-19 em 2022"), #FRASE EM BAIXO 
                dbc.Button("BRASIL", color="primary", id="location-button", size="lg")    #BOTÃO AZUL "BRASIL"      
            ], style={}),
            html.P("Informe a data na qual deseja obter informações:", style={"margin-top": "40px"}), #ESCRIÇÃO DA DATA
            html.Div(id="div-test", children=[
                dcc.DatePickerSingle(
                    id="date-picker",
                    min_date_allowed=df_brasil["data"].min(),
                    max_date_allowed=df_brasil["data"].max(),
                    initial_visible_month=df_brasil["data"].min(),
                    date=df_brasil["data"].max(),
                    display_format="D MMMM, YYYY",
                    style={"border": "0px solid black"} #CALENTARIO PARA ESCOLHER O DIA A SER VISTO NO GRAFICO DE BARRAS "FIG2" LOCALIZADO NA COLUNA DA FIGURA 2
                )
            ]),

        dbc.Row([ #CAIXA DE NÚMEROS DE "CASOS RECUPERADOS" E "EM ACOMPANHAMENTO".
            dbc.Col([
                dbc.Card([
                     dbc.CardBody([
                        html.Span("Casos Recuperados", className="card-text"),
                        html.H3(style={"color": "#adfc92"}, id="casos-recuperados-text"),
                        html.Span("Em acompanhamento", className="card-text"),
                        html.H5(id="em-acompanhamento-text"),
                     ])
                ], color="ligth", outline=True, style={"margin-top": "10px",
                                        "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                        "color": "#FFFFFF"})
            ], md=4),
            dbc.Col([ #CAIXA DE NÚMEROS DE "CASOS CONFIRMADOS TOTAIS" E "NOVOS CASOS".
                dbc.Card([
                     dbc.CardBody([
                        html.Span("Casos confirmados totais", className="card-text"),
                        html.H3(style={"color": "#389fd6"}, id="casos-confirmados-text"),
                        html.Span("Novos casos na data", className="card-text"),
                        html.H5(id="novos-casos-text"),
                     ])
                ], color="ligth", outline=True, style={"margin-top": "10px",
                                    "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                    "color": "#FFFFFF"})
            ], md=4),
            dbc.Col([ #CAIXA DE NÚMEROS DE "ÓBITOS CONFIRMADOS" E "ÓBITOS NA DATA".
                dbc.Card([
                     dbc.CardBody([
                        html.Span("Óbitos confirmados", className="card-text"),
                        html.H3(style={"color": "#DF2935"}, id="obitos-text"),
                        html.Span("Óbitos na data", className="card-text"),
                        html.H5(id="obitos-na-data-text"),
                     ])
                ], color="ligth", outline=True, style={"margin-top": "10px",
                                     "box-shadow": "0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)",
                                     "color": "#FFFFFF"})
            ], md=4),
           
        ]), 
            
            html.Div([
            html.P("Selecione que tipo de dado deseja visualizar:", style={"margin-top": "25px"}), 
            dcc.Dropdown(id="location-dropdown",
                        options=[{"label": j, "value": i} for i, j in select_columns.items()],
                        value="casosNovos",
                        style={"margin-top": "10px"}
                        ),
            dcc.Graph(id="line-graph", figure=fig2)
            ]) 

        ], md=5, style={"padding": "25px", "background-color": "#242424"}),


        dbc.Col([
            dcc.Loading(id="loading-1", type="default",
            children=[
                dcc.Graph(id="choropleth-map", figure=fig, style={"height": "100vh", "margin-right": "10px"})
                ]
            )            
        ], md=7)
    ], class_name='g-0'),
fluid=True) # AQUI DENTRO ESTARÁ O NOSSO LAYOUT. É IMPORTANTE TODA A COLUNA ESTÁ DENTRO DE UMA LINHA. 


#<<<<< INTERATIVIDADE >>>>>>
#1Selecionando o estado no mapa, ele apresentará informações para este estado no mapa, se clicar no botão BRASIL, é ara ele retornar para as informações do Brasil
#2Ao selecionar uma data, o mapa se atualize e mostre como estava a situação por estado naquela data selecioda, e os valores tambem se alterem para aquela data.
#3Ao trocar casos por dia e obtos totais, o grafico tambem trocasse. 
#4Dependendo da informação selecionada, o grafico mude para grafico de barras.

@app.callback(#=-=-=-=-=-=-=-=-INTERATIVIDADE NÚMERO 1 =-=-=-=-=-=-=-=-=-=-=-=-=-=
    [
        Output("casos-recuperados-text", "children"),
        Output("em-acompanhamento-text", "children"),
        Output("casos-confirmados-text", "children"),
        Output("novos-casos-text", "children"),
        Output("obitos-text", "children"),
        Output("obitos-na-data-text", "children"),
        
    ], 
    [Input("date-picker", "date"), Input("location-button", "children")]
    )
def display_status(date, location):
    if location == "BRASIL":
        df_data_on_date = df_brasil[df_brasil["data"]==date]
    else:
        df_data_on_date = df_states[(df_states["estado"] == location) & (df_states["data"] == date)]
    
    
    df_data_on_date["Recuperadosnovos"]
    recuperados_novos = "-" if df_data_on_date["Recuperadosnovos"].isna().values[0] else f'{int(df_data_on_date["Recuperadosnovos"].values[0]):,}'.replace(",", ".") 
    acompanhamentos_novos = "-" if df_data_on_date["emAcompanhamentoNovos"].isna().values[0]  else f'{int(df_data_on_date["emAcompanhamentoNovos"].values[0]):,}'.replace(",", ".") 
    casos_acumulados = "-" if df_data_on_date["casosAcumulado"].isna().values[0]  else f'{int(df_data_on_date["casosAcumulado"].values[0]):,}'.replace(",", ".") 
    casos_novos = "-" if df_data_on_date["casosNovos"].isna().values[0]  else f'{int(df_data_on_date["casosNovos"].values[0]):,}'.replace(",", ".") 
    obitos_acumulado = "-" if df_data_on_date["obitosAcumulado"].isna().values[0]  else f'{int(df_data_on_date["obitosAcumulado"].values[0]):,}'.replace(",", ".") 
    obitos_novos = "-" if df_data_on_date["obitosNovos"].isna().values[0]  else f'{int(df_data_on_date["obitosNovos"].values[0]):,}'.replace(",", ".") 
    return (
            recuperados_novos, 
            acompanhamentos_novos, 
            casos_acumulados, 
            casos_novos, 
            obitos_acumulado, 
            obitos_novos,
            )


@app.callback(Output("line-graph", "figure"), #----- INTERATIVIDADE: MUDANDO O TIPO DE GRÁFICO QUE APARECE, DEPENDENDO DA INFORMAÇÃO SELECIONADA. /////
            [
                Input("location-dropdown", "value"), Input("location-button", "children"), 

            ]
            )
def plot_line_graph(plot_type, location):
    if location == "BRASIL":
        df_data_on_location = df_brasil.copy()
    else:
        df_data_on_location = df_states[df_states["estado"] == location]

    bar_plots = ["casosNovos", "obitosNovos"]

    fig2 = go.Figure(layout={"template": "plotly_dark"})
    if plot_type in bar_plots:
        fig2.add_trace(go.Bar(x=df_data_on_location["data"], y=df_data_on_location[plot_type]))
    else:
                fig2.add_trace(go.Scatter(x=df_data_on_location["data"], y=df_data_on_location[plot_type]))


    fig2.update_layout(
        paper_bgcolor="#242424",
        plot_bgcolor="#242424",
        autosize=True,
        margin=dict(l=10, r=10, b=10, t=10),
        )
    return fig2


@app.callback( #------------------ INTERATIVIDADE: MUDANDO OS DADOS DO MAPA DE A CORDO COM A DATA SELECIONADA.
    Output("choropleth-map", "figure"), 
    [Input("date-picker", "date")]
)
def update_map(date):
    df_data_on_states = df_states[df_states["data"] == date]

    fig = px.choropleth_mapbox(df_data_on_states, locations="estado", geojson=brazil_states, 
        center={"lat": CENTER_LAT, "lon": CENTER_LON},  # https://www.google.com/maps/ -> right click -> get lat/lon
        zoom=4, color="casosAcumulado", color_continuous_scale="Redor", opacity=0.55,
        hover_data={"casosAcumulado": True, "casosNovos": True, "obitosNovos": True, "estado": False}
        )

    fig.update_layout(paper_bgcolor="#242424", mapbox_style="carto-darkmatter", autosize=True,
                    margin=go.layout.Margin(l=0, r=0, t=0, b=0), showlegend=False)
    return fig



@app.callback(
    Output("location-button", "children"),
    [Input("choropleth-map", "clickData"), Input("location-button", "n_clicks")]
)


def update_location(click_data, n_clicks):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if click_data is not None and changed_id != "location-button.n_clicks": 
        state=click_data["points"][0]["location"]
        return "{}".format(state)
    else:
        return "BRASIL"






if __name__ == "__main__":
    app.run_server(debug=True)