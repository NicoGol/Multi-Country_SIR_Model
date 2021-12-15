import plotly.graph_objs as go
import colorlover
import pandas as pd
import plotly.express as px
from Country import *
import dash_html_components as html

def flow_arrows(fig, mig, countries, title, day, color="yellow"):
    """
    Method adding the arrows representing the importance of migration flux between european countries to map
    """
    for i, c1 in enumerate(countries):
        for j, c2 in enumerate(countries):
            if c1 < c2:
                flow_c1_c2 = mig[day][i][j]
                if flow_c1_c2 > 15000:
                    fig.add_trace(go.Scattergeo(
                        lat=[latitude[c1], latitude[c2]],
                        lon=[longitude[c1], longitude[c2]],
                        mode='lines',
                        line=dict(width=flow_c1_c2 / 80000, color=color),
                        showlegend=False,
                    ))



def plot_mig(mig, countries, title, day=horizon-1):
    """
    Function creating the europe map
    """
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        locationmode='USA-states',
        lon=df_countries['Longitude'],
        lat=df_countries['Latitude'],
        text=df_countries['ISO 3166 Country Code'],
        textfont={"color": 'black',
                  "family": 'Times New Roman',
                  "size": 14},
        textposition="top center",
        name="Country",
        showlegend=False,
        mode="markers+text",
        marker=dict(
            size=10,
            color="black",
            line_color='black',
            line_width=0.5,
            sizemode='area')))

    fig.update_layout(
        # geo_scope='europe',
        ###ZOOM part, but doesn't work ###
        geo=go.layout.Geo(
            scope='europe',
            projection=go.layout.geo.Projection(
                type='azimuthal equal area',
                scale=1.7
            ),
            center={'lat': 52, 'lon': 7},
            showland=True,
            landcolor='rgb(243, 243, 243)',
            countrycolor='rgb(204, 204, 204)', )
    )

    fig.update_layout(template="plotly_white", margin=dict(l=0, r=0, t=40, b=0))

    flow_arrows(fig, mig, countries, title, day)
    return fig

def continuous_to_discrete(x):
    if x < 5:
        return '< 5'
    elif x < 10:
        return '[5,10['
    elif x < 15:
        return '[10,15['
    elif x < 25:
        return '[15,25['
    elif x < 35:
        return '[25,35['
    elif x < 50:
        return '[35,50['
    else:
        return '>= 50'


def add_I_map_day(base_fig,I,countries,origin='united kingdom',max_t=60):
    """
    Function adding the colors of each country in the europe map depending on their date of the peak of the infection
    """
    t_baseline = I[countries.index(origin)].index(max(I[countries.index(origin)]))
    data = [[countries[i],df_countries['iso_code'].loc[countries[i]],I[i].index(max(I[i]))-t_baseline,max(I[i]),df_countries['population'].loc[countries[i]]] for i in range(len(I))]
    df = pd.DataFrame(data,columns=['location','ISO3','t','I','pop'])
    df['I_prop'] = df['I'] / df['pop']
    df['t_discrete'] = df['t'].apply(continuous_to_discrete)
    fig = px.choropleth(df,
                       locations="ISO3",
                       color='t_discrete',
                       color_discrete_map={
                                    '< 5': '#990000',
                                    '[5,10[' : '#d7301f',
                                    '[10,15[' : '#ef6548',
                                    '[15,25[' : '#fc8d59',
                                    '[25,35[' : '#fdbb84',
                                    '[35,50[' : '#fdd49e',
                                    '>= 50' : '#fef0d9'},
                       category_orders={'t_discrete': ['< 5','[5,10[','[10,15[','[15,25[','[25,35[','[35,50[', '>= 50']},
                       center={"lat": 48.50855119, "lon": 13.0},
                       hover_name='t',
                       hover_data=["location", "I","pop","I_prop"],
                       height=900)
    fig.update_geos(fitbounds="locations",visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},width=1600)
    fig.layout.coloraxis.colorbar.title = 'peak day'
    for i in range(len(fig.data)):
        base_fig.add_trace(fig.data[i])
    return base_fig


def plot_heatmap(countries,I,order_countries,title):
    """
    Function ploting the heatmap with the evoluation of the rate of infected individuals in each country for the requested time period
    """
    data = [[countries[i],j,I[i][j],df_countries['population'].loc[countries[i]]] for i in range(len(I)) for j in range(len(I[0]))]
    df = pd.DataFrame(data,columns=['location','t','I','pop'])
    df['I_prop'] = df['I'] / df['pop']
    df = df.pivot('location','t','I_prop')
    df = df.loc[order_countries,:]
    fig = px.imshow(df,labels=dict(x="Time (in days)", y="Country", color="% infected population"),
                   width=1200, height=600,color_continuous_scale='YlOrRd')
    fig.update_layout(font=dict(size=20),yaxis = dict(tickfont = dict(size=18)))#,xaxis = dict(tickfont = dict(size=20)))
    return fig


def discrete_background_color_bins(df, n_bins=5, columns='all'):
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if isinstance(columns,str) and columns == 'all':
        if 'id' in df:
            df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
        else:
            df_numeric_columns = df.select_dtypes('number')
    else:
        df_numeric_columns = df[columns]
    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    styles = []
    legend = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colorlover.scales[str(n_bins)]['seq']['Reds'][i - 1]
        color = 'white' if i > len(bounds) / 2. else 'inherit'

        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            })
        legend.append(
            html.Div(style={'display': 'inline-block', 'width': '60px'}, children=[
                html.Div(
                    style={
                        'backgroundColor': backgroundColor,
                        'borderLeft': '1px rgb(50, 50, 50) solid',
                        'height': '10px'
                    }
                ),
                html.Small(round(min_bound, 2), style={'paddingLeft': '2px'})
            ])
        )

    return (styles, html.Div(legend, style={'padding': '5px 0 5px 0'}))