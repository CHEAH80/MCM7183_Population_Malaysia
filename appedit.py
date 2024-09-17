import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data (replace with your actual data path)
data = pd.read_csv('https://raw.githubusercontent.com/CHEAH80/MCM7183_Project/refs/heads/main/population_malaysia_2024.csv')

# Filter data for first page (Home Page)
filtered_data = data[(data['sex'] == 'both') & (data['ethnicity'] == 'overall')]

# Filter data for second page (Page 1)
df_filtered = data[(data['ethnicity'] == 'overall') & (data['sex'] != 'both')]

# Filter data for third page (Page 2)
df_filtered_ethnicity = data[data['ethnicity'] != 'overall']
years = df_filtered_ethnicity['year'].unique()

# Initialize the app with suppress_callback_exceptions=True
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Side navigation layout with "Navigation" title
side_nav = dbc.Nav(
    [
        html.H5("Navigation", className="my-3"),  # Title added above the navigation links
        dbc.NavLink("Home Page", href="/", active="exact"),
        dbc.NavLink("Page 1", href="/page-1", active="exact"),
        dbc.NavLink("Page 2", href="/page-2", active="exact"),
    ],
    vertical=True,
    pills=True,
    className="bg-light"
)

# Content for Home Page (Page 1)
def create_home_page():
    fig1 = px.scatter(filtered_data, x='year', y='population',
                      color='population', size='population',
                      title='Population in Millions Over The Years')
    fig1.add_scatter(x=filtered_data['year'], y=filtered_data['population'],
                     mode='lines', name='Trendline', line=dict(color='red'))
    
    # Add annotation for the year 2020
    fig1.add_annotation(
        x=2020,  # Year 2020 on the x-axis
        y=filtered_data[filtered_data['year'] == 2020]['population'].values[0],  # Population value for 2020 on the y-axis
        text="Population drop due to COVID-19",  # Annotation text
        showarrow=True,
        arrowhead=2,
        ax=0,  # X position of the annotation's arrow
        ay=-40,  # Y position of the annotation's arrow (shift the text above)
        bgcolor="rgba(255, 255, 255, 0.8)",  # Background color of the annotation
        bordercolor="black",  # Border color of the annotation
        borderwidth=1,  # Border width of the annotation
        font=dict(size=12)
    )

    fig1.update_layout(title={'text': "Population in Millions Over The Years", 'x': 0.5, 'font': {'size': 24}})
    
    return html.Div([dcc.Graph(figure=fig1)])

# Content for Page 1
def create_page_1():
    df_combined = df_filtered.groupby('year', as_index=False).agg({'population': 'sum'})
    df_combined['sex'] = 'Combined'
    df_final = pd.concat([df_filtered, df_combined])
    fig2 = px.bar(df_final, x='sex', y='population', color='sex', animation_frame='year',
                  title="Population by Sex and Year")
    fig2.update_layout(title={'text': "Population in Millions by Sex and Year", 'x': 0.5, 'font': {'size': 24}})
    return html.Div([dcc.Graph(figure=fig2)])

# Content for Page 2
def create_page_2():
    fig3 = go.Figure()
    df_year = df_filtered_ethnicity[df_filtered_ethnicity['year'] == years[0]]
    fig3.add_trace(go.Pie(labels=df_year['ethnicity'], values=df_year['population'], textinfo='label+percent'))
    fig3.update_layout(title={'text': "Population Distribution by Ethnicity", 'x': 0.5, 'font': {'size': 24}})
    
    frames = [go.Frame(data=[go.Pie(labels=df_filtered_ethnicity[df_filtered_ethnicity['year'] == year]['ethnicity'],
                                    values=df_filtered_ethnicity[df_filtered_ethnicity['year'] == year]['population'],
                                    textinfo='label+percent')],
                       name=str(year)) for year in years]
    fig3.frames = frames
    
    fig3.update_layout(updatemenus=[{'buttons': [{'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}], 'label': 'Play', 'method': 'animate'}]}],
                       sliders=[{'steps': [{'args': [[str(year)], {'frame': {'duration': 500, 'redraw': True}, 'mode': 'immediate'}], 'label': str(year), 'method': 'animate'} for year in years]}])
    
    return html.Div([dcc.Graph(figure=fig3)])

# Main layout with side navigation and content
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),  # Track URL changes
    
    # Centered header with additional top margin and subtitle
    dbc.Row([
        dbc.Col(html.H1("The Population of Malaysia", className="text-center"), width=12),
    ], className="mt-5"),  # Add top margin
    
    # Subtitle "(1980 - 2024)"
    dbc.Row([
        dbc.Col(html.H1("(1980 - 2024)", className="text-center"), width=12)
    ], className="mb-4"),  # Add bottom margin for spacing

    dbc.Row([
        dbc.Col(side_nav, width=2),  # Sidebar with "Navigation" title
        dbc.Col(html.Div(id='page-content'), width=10)
    ])
])

# Callback to update page content based on selected tab
@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return create_home_page()
    elif pathname == '/page-1':
        return create_page_1()
    elif pathname == '/page-2':
        return create_page_2()
    return "404 - Page Not Found"

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
