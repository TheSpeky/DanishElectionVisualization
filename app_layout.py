
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import auxiliary as aux


#text size variables
html_title_size = '1.2vw'
html_options_size = '1vw'


def make_layout(valg_data):
    return html.Div([
        html.Link(rel="stylesheet", href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"),
        html.Div([
        
        # Top div
        html.Div(children=[
            html.Div(children=[
                html.H2("Danish General Elections", style={'text-align': 'center'}),
                    html.Div(children=[
                        html.Div(children=[
                            make_selection_options(valg_data),
                            make_toggles()], style={'display':'flex', 'flex-direction':'row', 'width':'100%', 'justify-content': 'space-evenly'}),
                        make_municiaplity_selection_and_reset(valg_data)
                    ])
                ], style={'width':'45%'}),
            make_barchart(),
        ], id='top-div'),

        html.Div(children=[
        make_scatter_plot(),
        make_map()], id='bottom-div')        
        ], id='container', style={'display':'flex', 'flex-direction':'column'})
    ], id='background')
   
   
def make_map():
    return html.Div(
            children=[
                dcc.Graph(id='map', responsive=False, config = {'displaylogo': False, 
                                                               'displayModeBar': True})
            ], id='map-style')
    
def make_scatter_plot():
    return html.Div(
            children=[
                dcc.Graph(id='scatter',
                          responsive=True,
                          config = {'displaylogo': False, 
                                                  'displayModeBar': True,
                                                  'showAxisDragHandles': False,
                                                  'modeBarButtonsToRemove': ['autoScale2d']})
            ], id='scatter-style')

def make_barchart():
    return html.Div(children=[
        dcc.Graph(id='bar', 
                    responsive=False,
                    config = {'displaylogo': False, 
                                        'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'pan2d', 'zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'], 
                                        'displayModeBar': True,
                                        'showAxisDragHandles': False})
        ], id='bar-style')
     
def make_selection_options(valg_data):
    return html.Div(
            children=[
                html.Label("Party Selector", style={'font-size':html_title_size}, id='party_label'),
                dcc.Dropdown(
                    id='party-dropdown',
                    options=[{'label': party, 'value': party} for party in aux.parties_with_votes(valg_data, valg_data['year'].unique()[-1])['parti'].unique()],
                    value=valg_data['parti'].unique()[0],
                    clearable=False,
                    style={'margin-bottom':'4%', 'font-size':html_options_size, 'white-space': 'nowrap', 'text-overflow': 'ellipsis'}
                ),
                html.Label("Year Selector", style={'font-size':html_title_size}),
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': year, 'value': year} for year in valg_data['year'].unique()],
                    value=valg_data['year'].unique()[-1],
                    clearable=False,
                    multi=False,
                    style={'margin-bottom':'4%', 'font-size':html_options_size}
                ),
                html.Div(children=[
                    html.Label("Data Selector", style={'font-size':html_title_size}),
                    DashIconify(id='info_icon',icon="feather:info", width=25, style={'margin-top':'1%', 'margin-left':'2%'}),
                    dbc.Tooltip(
                        "All data contains every person in a municipality (including those who cannot vote).",
                        target="info_icon",
                    ),
                ], style={'display':'flex' }),
                dcc.Dropdown(
                    id='data-dropdown',
                    options=["Age", "Cars", "Population", "Education", "Salary", "Unemployment", "Crime"],
                    value="Age",
                    clearable=False,
                    style={'margin-bottom':'4%', 'font-size':html_options_size}
                )]
                , id='selection-container')
    
def make_toggles():
    return html.Div(children=[
                html.Div(
                    children=[
                        html.Label("Bar Chart Sorting", style={'font-size':html_title_size}),
                        dbc.RadioItems(
                            id="bar_chart_sorting",
                            className="btn-group",
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-primary",
                            labelCheckedClassName="active",
                            options=[
                                {"label": "Votes", "value": 1},
                                {"label": "Alphabetical", "value": 2},
                            ],
                            value=1,
                            style={'font-size':html_options_size}
                        )
                    ],
                    className="radio-group", style={'display':'flex', 'flex-direction': 'column', 'align-items': 'center', 'margin-bottom':'6%'}
                ),
                html.Div(
                    children=[
                        html.Label("Map Style", style={'font-size':html_title_size}),
                        dbc.RadioItems(
                            id="map_style",
                            className="btn-group",
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-primary",
                            labelCheckedClassName="active",
                            options=[
                                {"label": "Choropleth", "value": 1},
                                {"label": "Cartogram", "value": 2},
                            ],
                            value=1,
                            # style={'font-size':html_options_size}
                        )
                    ],
                    className="radio-group", style={'display':'flex', 'flex-direction': 'column', 'align-items': 'center', 'margin-bottom':'6%'}
                ),
                html.Div(
                    children=[
                        html.Label("Cross Filtering", style={'font-size':html_title_size}),
                        dbc.RadioItems(
                            id="selection-style",
                            className="btn-group",
                            inputClassName="btn-check",
                            labelClassName="btn btn-outline-primary",
                            labelCheckedClassName="active",
                            options=[
                                {"label": "Off", "value": False},
                                {"label": "On", "value": True},
                            ],
                            value=False,
                        )
                    ],
                    className="radio-group", style={'display':'flex', 'flex-direction': 'column', 'align-items': 'center', 'margin-bottom':'4%'}
                )], id="toggles")
    
def make_municiaplity_selection_and_reset(valg_data):
    return  html.Div([
                dbc.Button("Select Municipalities", id="open", n_clicks=0, style={'width':'30%', 'margin-left':'19%', 'margin-right':'2%'}),
                dbc.Button("Reset", id="reset", n_clicks=0, style={'width':'25%'}),
                dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Municipalities Selected")),
                dcc.Dropdown(
                    id='muni-dropdown',
                    options=sorted([{'label': sted, 'value': sted} for sted in valg_data['stemmested'].unique()], key=lambda d: d['value']),
                    value=[],
                    clearable=True,
                    multi=True,
                    maxHeight=400,
                    style={'margin':'auto', 'margin-top':'2%', 'margin-bottom':'2%', 'width':'95%', 'font-size':html_options_size}#, 'overflowY': 'auto'},
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ms-auto", n_clicks=0
                    )
                ),], id="modal", is_open=False, centered=False, scrollable=True, size="xl",
                style={'height':'100vh', 'width':'100vw', 'padding':'5%', 'align-items': 'center'}
            )], style={'display':'flex', 'flex-direction':'row', 'width':'100%', 'justify-content': 'flex-start', 'margin-top':'2%'})
    