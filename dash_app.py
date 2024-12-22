import json
import pandas as pd
from dash import Dash, html, dcc, Output, Input
import dash_bootstrap_components as dbc
import plotly.io as pio
import plotly.express as px
from datetime import timedelta

pio.templates.default = "plotly_white"

def create_graph_data():
    df = pd.DataFrame({
        'x': [1, 2, 3, 4, 5],
        'y': [10, 20, 30, 40, 50],
        'category': ['A', 'B', 'A', 'B', 'A']
    })
    return px.bar(df, x='x', y='y', color='category', barmode='group')


dash_app1 = None

def initialize_dash(server):
    global dash_app1
    dash_app1 = Dash(__name__, server=server,
                     url_base_pathname='/dash-tab1/',
                     external_stylesheets=[dbc.themes.BOOTSTRAP])
    try:
        init_first_tab()
        with open(file="temp/last_extracted_data.json") as f:
            dash_app1.layout.children[0].data = json.load(f)
    except Exception:
        print("First tab was not found.")

    # Third tab
    dash_app3 = Dash(__name__, server=server, url_base_pathname='/dash-tab3/')
    dash_app3.layout = html.Div([
        dcc.Graph(figure=create_graph_data())
    ])


# First tab
def init_first_tab():
    # Макет Dash приложения
    dash_app1.layout = html.Div([
        dcc.Store(id="weather_data"),
        dbc.Col([
            html.Div(id="current_cards"),

            # Фильтры для прогнозных данных
            dbc.Col([
                html.H3("Прогноз", style={'margin-top': '20px', 'margin-bottom': '10px'}),
                dbc.Row([
                    dbc.Col([
                        html.Label("Выберите параметр:", style={'margin-bottom': '10px'}),
                        dcc.Dropdown(
                            id='parameter-dropdown',
                            options=[
                                {'label': 'Температура', 'value': 'temperature'},
                                {'label': 'Скорость ветра', 'value': 'windSpeed'},
                                {'label': 'Влажность', 'value': 'humidity'},
                                {'label': 'Вероятность осадков', 'value': 'precipitationProbability'}
                            ],
                            value='temperature',
                        ),
                    ]),

                    dbc.Col([
                        html.Label("Выберите временной интервал (от 1 до 12 часов):",  style={'margin-bottom': '10px'}),
                        dcc.RangeSlider(
                            id='time-range-slider',
                            min=1, max=12, step=1,
                            marks={i: f'{i} ч' for i in range(1, 13)},
                            value=[1, 12],
                        ),
                    ])
                ], justify="evenly")
            ]),

            dcc.Graph(id='forecast-graph')
        ])
    ])



    @dash_app1.callback(
        Output('current_cards', 'children'),
        Input('weather_data', 'data')
    )
    def update_first_tab_current(weather_data):
        if not weather_data:
            return html.P("Нет данных для отображения.")

        df = pd.DataFrame(weather_data)

        current_temperature_card = dbc.Card(
            id="temperature_card",
            children=dbc.CardBody([
                html.H4("Текущая температура", className="card-title"),
                html.H2(f"{df.loc[0, 'temperature']} °C", className="card-text"),
            ])
        )

        current_wind_speed_card = dbc.Card(
            id="wind_speed_card",
            children=dbc.CardBody([
                html.H4("Текущая скорость ветра", className="card-title"),
                html.H2(f"{df.loc[0, 'windSpeed']} м/с", className="card-text"),
            ])
        )

        current_humidity_card = dbc.Card(
            id="humidity_card",
            children=dbc.CardBody([
                html.H4("Текущая влажность", className="card-title"),
                html.H2(f"{df.loc[0, 'humidity']} %", className="card-text"),
            ])
        )

        current_precipitation_card = dbc.Card(
            id="precipitation_card",
            children=dbc.CardBody([
                html.H4("Осадки", className="card-title"),
                html.H2(f"{'Есть' if df.loc[0, 'precipitationProbability'] >= 0.5 else 'Нет'}", className="card-text"),
            ])
        )

        return dbc.Row([
                    dbc.Col(current_temperature_card),
                    dbc.Col(current_wind_speed_card),
                    dbc.Col(current_humidity_card),
                    dbc.Col(current_precipitation_card)
                ])


    @dash_app1.callback(
        Output('forecast-graph', 'figure'),
        [
            Input('parameter-dropdown', 'value'),
            Input('time-range-slider', 'value'),
            Input('weather_data', 'data')
        ]
    )
    def update_first_tab_graph(selected_param, time_range, weather_data):
        if not weather_data:
            return px.line(title="Нет данных для отображения")

        df = pd.DataFrame(weather_data)
        df['datetime'] = pd.to_datetime(df['datetime'])

        from_time = df.loc[0, 'datetime'] + timedelta(hours=time_range[0])
        to_time = df.loc[0, 'datetime'] + timedelta(hours=time_range[1])

        filtered_df = df[(df['datetime'] >= from_time) & (df['datetime'] <= to_time)]
        param_to_name_dict = {
            'temperature': 'Температура, °С',
            'windSpeed': 'Скорость ветра, м/c',
            'humidity': 'Влажность, %',
            'precipitationProbability': 'Вероятность осадков, %',
        }
        if selected_param == 'temperature' or selected_param == 'windSpeed' or selected_param == 'precipitationProbability':
            fig = px.line(filtered_df,
                          x='datetime',
                          y=selected_param,
                          labels={'datetime': 'Часы', selected_param: param_to_name_dict[selected_param]})
        else:
            fig = px.bar(filtered_df,
                          x='datetime',
                          y=selected_param,
                          labels={'datetime': 'Часы', selected_param: param_to_name_dict[selected_param]})
        return fig

    return dash_app1