import load_data as data
import auxiliary as aux
import app_layout as layout

import dash
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State


# Election percentage data
valg_data = data.valg_percent

# Font sizing
figure_text_size = 14

# Initialize the Dash app
app = dash.Dash(__name__)


# Define the layout of the app
app.layout = layout.make_layout(valg_data)


# Global Constants
default_hover_layout = dict(
        bgcolor="rgb(68,68,68)",
        font_color="white"
    )

@app.callback(
    Output("muni-dropdown", "value"),
    [Input("muni-dropdown", "value"),
     Input("scatter", 'selectedData'),
     Input("map", 'selectedData'),
     State("selection-style", 'value'),
     Input("reset", "n_clicks")]
)
def update_municipalities(dropdown_selection, scatter_selection, map_seletion, cross_filtering, click):
    trigger = get_triggers()

    selection = []

    if ('scatter.selectedData' in trigger and scatter_selection and (len(scatter_selection['points']) == 0)):
        return dash.no_update

    if ('map.selectedData' in trigger and map_seletion):
        selection = [point['location'] for point in map_seletion['points']]
    
    if ('scatter.selectedData' in trigger and scatter_selection):
        selection = [point['customdata'][0] for point in scatter_selection['points']]
    
    if ('muni-dropdown.value' in trigger):
        return dash.no_update
    
    if dropdown_selection and cross_filtering: return list(set(selection).intersection(dropdown_selection))
    return selection

@app.callback(
        Output('bar', 'figure'),
        [Input('bar', 'clickData'),
        Input('year-dropdown', 'value'),
        Input('party-dropdown', 'value'),
        Input('muni-dropdown', 'value'),
        Input("bar_chart_sorting", 'value')]
)
def update_bar(clickParty, selected_year, selected_party, selected_municipalities, sorting_type):
    trigger = get_triggers()

    # Makes Grouped Buttons work
    if trigger is None: trigger = []

    #If not municipality is choosen, i.e. all are in focus
    if selected_municipalities is not None and len(selected_municipalities) == 0:
        selected_municipalities = valg_data['stemmested'].unique()

    municipality_data = data.valg_raw.copy()
    mask = data.valg_raw['stemmested'].isin(selected_municipalities)
    municipality_data = municipality_data[mask]
            
    parties = aux.parties_with_votes(aux.election_result(municipality_data), selected_year)
    
    # Sort by alphabetical (the Å-Ø exchange is to enforce correct ordering)
    parties = parties.sort_values('parti', ascending=True, key=lambda p: p.str.replace('Å', 'Ø'*10)) 
    if sorting_type == 1:
        parties = parties.sort_values('stemmer', ascending=False) # Sort by votes

        
    #update barchart
    fig = px.bar(parties, x=parties['parti'].str.split('.').str[0], y='stemmer', width=800, text=parties['parti'])
    fig.update_traces(hovertemplate = "<b>%{text}</b>", textposition='none')
    
    fig.update_layout(
        margin=dict(r=10, b=0),
        xaxis_title='Party',
        yaxis_title="Votes (%)",
        title = f'Votes for Parties ({selected_year})' if 'map' not in trigger else f'Votes for Parties in the selected municipalities ({selected_year})',
        font = dict(size = figure_text_size),
        hoverlabel=default_hover_layout,
        dragmode=False,
        annotations = [dict( x = row[0].split(".")[0], 
                            y = row[2]+0.9, 
                            text = "{:.1f}%".format(row[2]), 
                            showarrow=False, 
                            font=dict(size=12)) for _, row in parties.iterrows()],
    )

    #Choose party
    if 'bar.clickData' in trigger:
        selected_party = clickParty['points'][0]['text']
    
    party = selected_party.split(".")[0]
    marker_colors = [aux.party_color(letter) for letter in parties['parti'].str.split('.').str[0]]
    marker_opacity = [1.0 if letter == party else 0.3 for letter in parties['parti'].str.split(".").str[0]]
    marker_pattern = ["" if letter == party else "/" for letter in parties['parti'].str.split(".").str[0]]

    fig.update_traces(marker_color = marker_colors,
                      marker_opacity = marker_opacity, 
                      marker_pattern_shape = marker_pattern,
                      marker_pattern_size = 7)

    return fig

# Define a callback to update the figure based on dropdown selections
@app.callback(
        Output('map', 'figure'),
        [Input('party-dropdown', 'value'),
        Input('year-dropdown', 'value'), 
        Input('bar', 'clickData'),
        Input('muni-dropdown', 'value'),
        Input("map_style", 'value'),
        Input("map", "clickData"),
        Input("map", "selectedData")
        ]
)
def update_map(selected_party, selected_year, clickParty, selected_muni, map_style, _, __):
    trigger = get_triggers()
        
    if 'bar' in trigger:
        selected_party = clickParty['points'][0]['text']

    filtered_data = valg_data[(valg_data['parti'] == selected_party) & (valg_data['year'] == selected_year)]

    fig = reload_map(filtered_data, map_style, selected_muni)

    return fig

def reload_map(filtered_data, map_style, selected_muni):
    spacial_data = data.kommuner_geojson
    if map_style == 2:
        spacial_data = data.carto_geojson

    fig = go.Figure(data=go.Choroplethmapbox(
        geojson = spacial_data,
        featureidkey = 'properties.navn',
        locations = filtered_data['stemmested'],
        z = filtered_data['stemmer'],
        colorscale = 'viridis',
        reversescale=True,
        colorbar_title="Votes (%)",
        hovertemplate="%{z:.1f}%<extra>%{location}</extra>"
    ))
    fig.update_layout(
        mapbox_center={'lat': 56.23205043365613, 'lon': 11.453154691145753},
        margin={"r": 10, "t": 30, "l": 0, "b": 0},
        mapbox_style = 'carto-positron',
        mapbox_zoom=5.6,
        autosize = True,
        font = dict(size = figure_text_size),
        clickmode = 'event+select',
        dragmode='select'
    )
    
    if map_style == 2:
        fig.update_layout(mapbox_style="white-bg")
    
    fig.update_traces(marker_opacity = [1.0 for _ in filtered_data['stemmested']])
    if selected_muni:
        fig.update_traces(marker_opacity = [1.0 if sted in selected_muni else 0.3 for sted in filtered_data['stemmested']])
    
    return fig

# Update party options based on year
@app.callback(
    Output('party-dropdown', 'value'),
    Output('party-dropdown', 'options'),
    [Input('party-dropdown', 'value'),
     Input('party-dropdown', 'options'),
     Input('year-dropdown', 'value'),
     Input('bar', 'clickData')]
)
def update_party_dropdown(party, options, selected_year, clickParty):
    trigger = get_triggers()

    if 'bar' in trigger:
        party = clickParty['points'][0]['text']
    
    if 'year-dropdown' in trigger:
        options = list(aux.parties_with_votes(valg_data, selected_year)['parti'].unique())
        if party not in options:
            return options[0], options
    return party, options
    
@app.callback(
    Output('scatter', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('party-dropdown', 'value'),
     Input('muni-dropdown', 'value'),
     Input("data-dropdown", 'value')]
)
def update_scatter(selected_year, selected_party, selected_municipalities, selected_data):    
    #Scatter variables
    x_data_title = "Default"
    x_suffix = ""
    x_data = None
    x_column = None
    
    votes = valg_data[(valg_data['parti'] == selected_party) & (valg_data['year'] == int(selected_year))][['stemmested', 'stemmer']]
    if "Age" in selected_data:
        x_column = "alder"
        x_data = data.alder_data[(data.alder_data['year'] == selected_year) & (data.alder_data['køn'] == "I alt")][['stemmested', x_column]]
        x_data_title = "Age"
        x_suffix = " years"
        
    elif "Cars" in selected_data:
        x_column = "percentage"
        x_data = data.car_data[(data.car_data['year'] == selected_year)][['stemmested', x_column]]
        x_data_title = "Famalies with a car"
        x_suffix = "%"

    elif "Population" in selected_data:
        x_column = "change"
        x_data = data.population_data[(data.population_data['year'] == selected_year)][['stemmested', x_column]]
        x_data_title = "Population change"
        x_suffix = "‰"
    
    elif "Education" in selected_data:
        x_column = "avg education"
        x_data = data.education_data[(data.education_data['year'] == selected_year)][['stemmested', x_column]]
        x_data_title = "Education"
        x_suffix = " years"
        
    elif "Salary" in selected_data:
        x_column = "avg salary"
        x_data = data.salary_data[data.salary_data['year'] == selected_year][['stemmested', x_column]]
        x_data_title = "Salary"
        x_suffix = " DKK"
    
    elif "Unemployment" in selected_data:
        x_column = "ratio"
        x_data = data.unemployment_data[data.unemployment_data['year'] == selected_year][['stemmested', x_column]]
        x_data_title = "Unemployment rate"
        x_suffix = "%"
    
    elif "Crime" in selected_data:
        x_column = "ratio"
        x_data = data.crime_data[data.crime_data['year'] == selected_year][['stemmested', x_column]]
        x_data_title = "Reported crimes"
        x_suffix = " per 1.000 citizens"
        
    
    df = votes.merge(x_data, on=['stemmested'], how='left')
    
    party_color = aux.party_color(selected_party[0])
    fig = px.scatter(df, x=x_column, y='stemmer', 
                     hover_data='stemmested', 
                     color_discrete_sequence=[party_color],
                     )
    fig.update_traces(hovertemplate = "<b>%{text}</b><br>" + x_data_title + ": %{x:.1f}" + x_suffix + "<br>Votes: %{y:.1f}%", text=[i for i in df['stemmested']])
    fig.update_yaxes(title=dict(text="Votes (%)"))
    fig.update_xaxes(title=dict(text=x_data_title + f" ({x_suffix.strip()})"))
    fig.update_layout(
        # font_size=22,
        margin=dict(r=20, b=0),
        title=f"Votes vs {x_data_title}",
        font = dict(size = figure_text_size),
        clickmode = 'event+select',
        hoverlabel=default_hover_layout,
        dragmode='select',
        autosize=True
    )
    fig.update_traces(marker=dict(size=12, opacity=0.7, line=dict(width=1.5, color='black')))
        
    if selected_municipalities:
        fig.update_traces(selectedpoints = df[df['stemmested'].isin(selected_municipalities)].index)

    return fig


def get_triggers():
    return [p['prop_id'] for p in dash.callback_context.triggered][0]

# Used to open municipality selection
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


if __name__ == '__main__':
    allow_duplicate=True
    app.run_server(debug=True)
