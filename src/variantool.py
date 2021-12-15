import dash
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output, State
from plot_functions import *
import dash_bootstrap_components as dbc

from dash_bootstrap_templates import load_figure_template

options = []
for country in eu_countries:
    options.append({"label": country, "value": country})
options2 = [{"label": "all", "value": "all"}] + options
migration_matrix = create_migration_matrix(horizon)
col = '#61BFF3'
light = '#95D5FC'

# This loads the "cerulean" themed figure template from dash-bootstrap-templates library,
# adds it to plotly.io and makes it the default figure template.
load_figure_template("cerulean")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

server=app.server



(styles,legend) = discrete_background_color_bins(migration_matrix_short, n_bins=9, columns=migration_matrix_short.columns[1:])



def find_interval(day,markers):
    """
    Method finding the 2 closest markers of the sliding window (lower and upper) to the time step "day"
    :param day: time step for which the intervals need to be found
    :param markers: the set of all markers of the sliding window
    :return: the time steps of the 2 markers constituting the interval
    """
    left = 0
    right = horizon
    for marker in markers.keys():
        marker = int(marker)
        if marker <= day and marker > left and marker != horizon:
            left = marker
        elif marker > day and marker < right:
            right = marker
    return left,right

def keep_symmetric(day, data):
    """
    Method making sure the migration matrix is symmetric when it is modified
    :param day: the time step on which the matrix was modified
    :param data: value of the migration matrix on day "day"
    :return: the migration matrix on day "day" modified so that it is symmetrical
    """
    old_data = migration_matrix[day]
    for i in range(old_data.shape[0]):
        for j in range(old_data.shape[1]):
            if old_data[i][j] != data[i][j]:
                data[j][i] = data[i][j]
    return data

# ------------------------------------------------------------------------------
# App layout
app.layout = dbc.Container(fluid=True, children=[
    html.H1("Number of days before the peak of infection is reached per country", style={'text-align': 'center'}, className="bg-primary text-white p-2"),
    html.Div(className='row',
             style={'display': 'flex', 'background-color':col,'border': '1px solid black','borderRadius': '15px',"width":"1600px", 'margin-left':'100px','margin-top':'20px'},
             children=[
        html.Div(style={'margin-left':'20px','margin-top':'5px',"width":"550px"},children=[
            html.Div(style={'display':'flex'}, children=[
                html.Div(id='origin_container', style={'fontWeight': 'bold'}, children='The origin country of the virus'),
                dcc.Dropdown(id="slct_country_origin",
                             options=options,
                             multi=False,
                             value='united kingdom',
                             style={'width': "190px",'margin-left':'10px'}
                             ),
            ]),
            html.Div(id='origin_explainer', children='On day 0, this country has 10 inhabitants infected by the virus.')]),
        html.Div(style={"margin-left": "0px","width":"650px",'margin-top':'5px'}, children=[
            html.Div(style={'display':'flex'}, children=[
                html.Div(id='beta_container', style={'fontWeight': 'bold'}, children='The infection rate of the virus'),
                dcc.Input(id="beta", type="number", value=0.2, style={'width':'45px','margin-left':'10px'}),
            ]),
            html.Div(id='beta_explainer', style={'margin-bottom':'5px'},children='This is the average number of contacts per person per time '
                                                   'multiplied by the probability of disease transmission in a contact '
                                                   'between a susceptible and a infectious subject.')]),
        html.Div(style={"margin-left": "40px",'margin-top':'5px'}, children=[
            html.Div(style={'display':'flex'}, children=[
                html.Div(id='gamma_container', style={'fontWeight': 'bold'}, children='The recovery rate of the virus'),
                dcc.Input(id="gamma", type="number", value=0.1, style={'width':'45px','margin-left':'10px'}),
            ]),
            html.Div(id='gamma_explainer', children='This is the daily probability of recovery.')])]),
    dcc.Tabs(id='tabs',style={'margin-top':'20px'},children=[
    dcc.Tab(label='Migration Matrix', selected_style={'background-color':col,'fontWeight':'bold'},style={'background-color':light}, children=[
        html.Br(),
        html.Div(style={"margin-top":"20px","margin-left": "250px",'width':'1600px','display': 'flex'},children=[
            html.Div(style={'width':'1200px'},children=[
                dcc.RangeSlider(
                    id='day_slider',
                    min=0,
                    max=horizon,
                    step=5,
                    value=[0],
                    tooltip={'always_visible':True},
                    marks={0: {'label': 'Day 0', 'style': {'color':'black','fontWeight': 'bold'}},
                           horizon: {'label': 'Day '+str(horizon), 'style': {'color':'black','fontWeight': 'bold'}}}
                )]),
            html.Div(style={"margin-left": "50px"},children=[
                html.Button('Add Marker', id='add_marker_button', n_clicks=0, style={'border': '1px solid black','borderRadius': '15px'})
            ])]),
        html.Br(),
        html.Div(style={'display':'flex'}, children=[
            html.Button('Reset Matrix', id='reset_button', n_clicks=0,style={'border': '1px solid black', 'borderRadius': '15px', "margin-left": "80px", 'background-color':col,
                                                                    'margin-top': '35px', 'width': '200px', 'height': '50px', 'fontWeight': 'bold'}),

            html.Div(style={'background-color':col,'border': '1px solid black','borderRadius': '15px',"width":"1180px",
                            "height":"80px",'display': 'flex', 'margin-top': "20px","margin-left": "100px"}, children=[
                html.Div(style={'margin-top':'5px',"margin-left": "20px","width":"200px"}, children=[
                    html.Div(id='country1', style={'fontWeight': 'bold'}, children='Country 1'),
                    dcc.Dropdown(id="slct_country_1",
                                 options=options2,
                                 multi=False,
                                 value='all',
                                 style={'width': "200px"}
                                 ),
                ]),
                html.Div(style={'margin-top':'5px',"margin-left": "30px","width":"200px"}, children=[
                    html.Div(id='country2', style={'fontWeight': 'bold'}, children='Country 2'),
                    dcc.Dropdown(id="slct_country_2",
                                 options=options2,
                                 multi=False,
                                 value='all',
                                 style={'width': "200px"}
                                 ),
                ]),
                html.Div(style={'margin-top':'5px',"margin-left": "30px","width":"200px"}, children=[
                    html.Div(id='factor_explainer', style={'fontWeight': 'bold'}, children='Multiplication Factor'),
                    dcc.Input(id="factor", type="number", value=1.0, style={'width': "50px"})
                ]),
                html.Div(id='multiplicator_explainer', style={"margin-left": "10px",'margin-top':'15px','width':'360px'}, children=' '),
                html.Button('Apply', id='multiplicator_button', n_clicks=0,style={'border': '1px solid black','borderRadius': '15px',"margin-left": "20px",'margin-top':'15px','width':'80px','height':'50px'})
            ])]),
        html.Div(id='matrix_title', style={'fontWeight': 'bold',"margin-top":"30px"}, children='SYMMETRIC MIGRATION MATRIX : number of daily movers between 2 countries in thousands'),
        html.Div(style={'display': 'flex',},children=[
            dash_table.DataTable(
                id='migration_table',
                columns=[{'name': c, 'id': c} for c in migration_matrix_short.columns],
                data=migration_matrix_short.to_dict('records'),
                editable=True,
                style_header={
                    'backgroundColor': 'grey',
                    'color': 'white',
                    'textAlign': 'left',
                    'fontWeight': 'bold'
                },
                style_cell={'minWidth': 30, 'maxWidth': 30, 'width': 30, 'minHeight': 12, 'maxHeight': 12, 'Height': 12},
                style_cell_conditional=[{
                        'if': {'column_id': ''},
                        'backgroundColor': 'grey',
                        'color': 'white',
                        'textAlign': 'left',
                        'fontWeight': 'bold'
                    }],
                style_data_conditional=styles,
                fill_width=False
            ),
            html.Div(style={'padding-left': '100px'},children=[
                dcc.Graph(id='travel_map', style={'width': '800px','height':'800px'},figure={})
                ])
            ]
        ),
    ]),
    dcc.Tab(label='Graphs', selected_style={'background-color':col,'fontWeight':'bold'},style={'background-color':'#95D5FC'}, children=[
        html.Div(style={'display':'flex'},children=[
            html.Div(
                [dcc.Graph(id='infection_heatmap', figure={},style={'height':'600px','width':'1200px'}),
                 html.Div([
                     html.Div(dcc.Input(id='filename_heatmap', type='text', placeholder='Enter the name of the file')),
                     html.Button('Save Heatmap as pdf', id='save_heatmap', n_clicks=0),
                     html.Div(id='text_save_heatmap', children='')
                 ], style={'padding-left': '350px','display':'flex','margin-top': '10px'})],
                style={'padding-left': '20px'}
            ),
            html.Div([
                dcc.Graph(id='infection_map', figure={},style={'height':'600px','width':'600px'}),
                html.Div([
                    html.Div(dcc.Input(id='filename_map', type='text', placeholder='Enter the name of the file')),
                    html.Button('Save Map as pdf', id='save_map', n_clicks=0,style={'padding-left': '15px'}),
                    html.Div(id='text_save_map', children='')
                ], style={'padding-left': '70px','display':'flex','margin-top': '10px'})],
                style={'padding-left': '0px'}
                ),
    ])])])

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='infection_map', component_property='figure'),
     Output(component_id='infection_heatmap', component_property='figure')],
    Input(component_id='tabs', component_property='value'),
    [State(component_id='slct_country_origin', component_property='value'),
     State(component_id='beta', component_property='value'),
     State(component_id='gamma', component_property='value')]
)
def update_graph(tab, origin_country, beta, gamma):
    countries = create_countries(eu_countries, origin=origin_country, beta=beta, gamma=gamma, Horizon=horizon)

    mig = migration_matrix *1000

    Ires = simulate(countries, mig)

    fig1 = plot_mig(mig, eu_countries, 'Infected rate in EU countries with baseline migration')
    fig1 = add_I_map_day(fig1, Ires, eu_countries)

    dictI = {}
    for i, country in enumerate(eu_countries):
        dictI[country] = Ires[i].index(max(Ires[i]))
    dictI = dict(sorted(dictI.items(), key=lambda item: item[1]))
    order_countries = dictI.keys()
    fig2 = plot_heatmap(eu_countries, Ires, order_countries, 'Infected rate in EU countries with baseline migration')

    return fig1, fig2


@app.callback(
    Output(component_id='day_slider', component_property='marks'),
    Input(component_id='add_marker_button', component_property='n_clicks'),
    Input(component_id='reset_button', component_property='n_clicks'),
    State(component_id='day_slider', component_property='value'),
    State(component_id='day_slider', component_property='marks'),
)
def update_slider(n_clicks_add,n_clicks_reset,day,marker):
    ctx = dash.callback_context
    if not ctx.triggered:
        pass
    elif 'add' in ctx.triggered[0]['prop_id']:
        marker[day[0]] = {'label' : 'Day ' + str(day[0]), 'style': {'color':'black','fontWeight': 'bold'}}
    elif 'reset' in ctx.triggered[0]['prop_id']:
        global migration_matrix
        migration_matrix = create_migration_matrix(horizon)
        marker = {0: {'label': 'Day 0', 'style': {'color': 'black', 'fontWeight': 'bold'}},
              horizon: {'label': 'Day ' + str(horizon), 'style': {'color': 'black', 'fontWeight': 'bold'}}}
    return marker

@app.callback(
    Output(component_id='multiplicator_explainer', component_property='children'),
    Input(component_id='slct_country_1', component_property='value'),
    Input(component_id='slct_country_2', component_property='value'),
    Input(component_id='day_slider', component_property='value'),
    Input(component_id='day_slider', component_property='marks'),
    Input(component_id='factor', component_property='value'),
)
def update_multiplicator_explainer(country1,country2,day,markers,factor):
    left, right = find_interval(day[0], markers)
    return 'Multiply daily migration flow between ' + country1 + ' and ' + country2 + ' from day ' + str(left) \
           + ' to day ' + str(right) + ' by ' + str(factor)

@app.callback(
    Output(component_id='matrix_title', component_property='children'),
    Output(component_id='migration_table', component_property='data'),
    Input(component_id='day_slider', component_property='value'),
    Input(component_id='day_slider', component_property='marks'),
    Input(component_id='multiplicator_button', component_property='n_clicks'),
    State(component_id='slct_country_1', component_property='value'),
    State(component_id='slct_country_2', component_property='value'),
    State(component_id='factor', component_property='value'),
)
def update_matrix(day,markers,n_clicks,country1,country2,factor):
    left, right = find_interval(day[0], markers)
    text = 'SYMMETRIC MIGRATION MATRIX : number of daily movers between 2 countries from day ' \
           + str(left) + ' to day ' + str(right) + ' in thousands'
    data = migration_matrix[min(day[0], horizon - 1)]
    trigger_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'multiplicator_button' and n_clicks > 0:
        if country1 == 'all':
            country1 = list(df_countries.index)
        else:
            country1 = [country1]
        if country2 == 'all':
            country2 = list(df_countries.index)
        else:
            country2 = [country2]
        for c1 in country1:
            index1 = list(df_countries.index).index(c1)
            for c2 in country2:
                index2 = list(df_countries.index).index(c2)
                data[index1][index2] = round(data[index1][index2] * factor)
                if country1!='all' or country2!='all':
                    data[index2][index1] = round(data[index2][index1] * factor)
    df = migration_matrix_short.copy()
    df[df.columns[1:]] = data
    return text,df.to_dict('records')



@app.callback(
    Output(component_id='travel_map', component_property='figure'),
    Input(component_id='migration_table', component_property='data'),
    State(component_id='day_slider', component_property='value'),
    State(component_id='day_slider', component_property='marks')
)
def update_matrix(rows,day,markers):
    left,right = find_interval(day[0],markers)
    data = pd.DataFrame(rows).drop('',axis=1).astype(float).values
    data = keep_symmetric(day[0],data)
    global migration_matrix
    migration_matrix[left:right] = [data for i in range(right-left)]
    mig = migration_matrix * 1000
    fig = plot_mig(mig, eu_countries, '', day=day[0])
    return fig


@app.callback(
    dash.dependencies.Output(component_id='text_save_heatmap', component_property='children'),
    dash.dependencies.Input(component_id='save_heatmap', component_property='n_clicks'),
    dash.dependencies.State(component_id='infection_heatmap', component_property='figure'),
    dash.dependencies.State(component_id='filename_heatmap', component_property='value'))
def update_output(n_clicks, fig, value):
    if n_clicks > 0:
        fig = go.Figure(fig)
        file_name = value + '.pdf'
        fig.write_image(file_name)
        return 'The figure has been saved under the name "{}"'.format(file_name)
    return ''


@app.callback(
    dash.dependencies.Output(component_id='text_save_map', component_property='children'),
    dash.dependencies.Input(component_id='save_map', component_property='n_clicks'),
    dash.dependencies.State(component_id='infection_map', component_property='figure'),
    dash.dependencies.State(component_id='filename_map', component_property='value'))
def update_output(n_clicks, fig, value):
    if n_clicks > 0:
        fig = go.Figure(fig)
        file_name = value + '.pdf'
        fig.write_image(file_name)
        return 'The figure has been saved under the name "{}"'.format(file_name)
    return ''


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)