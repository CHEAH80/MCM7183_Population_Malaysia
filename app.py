import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
data = pd.read_csv('https://raw.githubusercontent.com/CHEAH80/Project_Population_Malaysia/refs/heads/main/assets/population_malaysia.csv')

# Filter data for home page
filtered_data = data[(data['sex'] == 'both') & (data['age'] == 'overall') & (data['ethnicity'] == 'overall')]

# Filter data for Page 1
df_filtered = data[(data['year'] >= 1970) & (data['sex'].isin(['male', 'female'])) & 
                   (data['age'] == 'overall') & 
                   (data['ethnicity'] == 'overall')]

# Filter data for Page 2
df_filtered_ethnicity = data[data['ethnicity'] != 'overall']
years = df_filtered_ethnicity['year'].unique()

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Malaysia Population By Cheah Yew Chung"
server = app.server

# Sidebar layout with logo
side_nav = dbc.Nav(
    [
        html.Div(
            html.Img(src="https://raw.githubusercontent.com/CHEAH80/Project_Population_Malaysia/refs/heads/main/assets/logo-mmu.png", 
                     style={'width': '100%', 'marginBottom': '10px'}), 
            style={'textAlign': 'center'}
        ),
        html.H5("Navigation", className="my-3"),
        dbc.NavLink("Home Page", href="/", active="exact"),
        dbc.NavLink("By Sex", href="/page-1", active="exact"),
        dbc.NavLink("By Ethnicity", href="/page-2", active="exact"),
    ],
    vertical=True,
    pills=True,
    className="bg-light"
)

# Title style
title_style = {'fontSize': '24px', 'textAlign': 'center', 'marginTop': '20px'}

# Content for Home Page
def create_home_page():
    # Create the scatter plot
    fig = px.scatter(
        filtered_data, 
        x='year', 
        y='population', 
        color='population',  # Color based on population
        size='population',   # Size based on population
        title='',  # Set title as empty since we will add it below
        labels={'year': 'Year', 'population': 'Population'}
    )

    # Add a trendline to the scatter plot
    fig.add_traces(go.Scatter(
        x=filtered_data['year'], 
        y=filtered_data['population'], 
        mode='lines', 
        name='Trendline',
        line=dict(color='red', width=2),
        showlegend=True
    ))

    # Customize the layout to have the same blue background as Page 1
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Population",
        title_x=0.5,
        plot_bgcolor='rgba(0,0,255,0.1)',  # Set background to light blue
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
        font=dict(size=14)
    )

    # Add annotation for the year 2020
    fig.add_annotation(
        x=2020,
        y=filtered_data[filtered_data['year'] == 2020]['population'].values[0],  # Get population for 2020
        text="Population drop due to COVID-19",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        font=dict(color='black', size=12)
    )

    # Add image
    image_url = "https://raw.githubusercontent.com/CHEAH80/MCM7183_Population_Malaysia/main/assets/malaysia.jpg"
    image = html.Div([
        html.Img(src=image_url, style={'width': '300px', 'display': 'block', 'margin': 'auto'}),
    ], style={'textAlign': 'center', 'marginTop': '20px'})

    return html.Div([
        html.H1("Population in Millions over the Years", style=title_style),  # Main title
        dcc.Graph(figure=fig), 
        image
    ])

# Content for Page 1
def create_page_1():
    # Calculate combined population for "Both"
    df_combined = df_filtered.groupby('year').agg({'population': 'sum'}).reset_index()
    df_combined['sex'] = 'Both'

    # Append the combined data to the existing filtered DataFrame
    df_combined_full = pd.concat([df_filtered, df_combined], ignore_index=True)

    # Create the bar chart with the combined value included
    fig2 = px.bar(df_combined_full, x='sex', y='population', color='sex', 
                  animation_frame='year',
                  title="Population by Sex and Year")
    
    # Add population labels on top of bars
    fig2.update_traces(texttemplate='%{y}', textposition='outside')

    fig2.update_layout(
        title={'text': "Population in Millions by Sex and Year", 'x': 0.5, 'font': {'size': 24}},
        plot_bgcolor='rgba(0,0,255,0.1)'  # Blue background
    )

    # Add image
    image_url = "https://raw.githubusercontent.com/CHEAH80/MCM7183_Population_Malaysia/main/assets/malaysia.jpg"
    image = html.Div([
        html.Img(src=image_url, style={'width': '300px', 'display': 'block', 'margin': 'auto'}),
    ], style={'textAlign': 'center', 'marginTop': '20px'})

    return html.Div([
        dcc.Graph(figure=fig2),  # Only keep the figure and image
        image
    ])

# Content for Page 2
def create_page_2():
    fig3 = go.Figure()
    df_year = df_filtered_ethnicity[df_filtered_ethnicity['year'] == years[0]]
    fig3.add_trace(go.Pie(labels=df_year['ethnicity'], values=df_year['population'], textinfo='label+percent'))
    fig3.update_layout(title={'text': "Population Distribution by Ethnicity and Year", 'x': 0.5, 'font': {'size': 24}})

    frames = [go.Frame(data=[go.Pie(labels=df_filtered_ethnicity[df_filtered_ethnicity['year'] == year]['ethnicity'],
                                    values=df_filtered_ethnicity[df_filtered_ethnicity['year'] == year]['population'],
                                    textinfo='label+percent')],
                       name=str(year)) for year in years]
    fig3.frames = frames

    fig3.update_layout(
        updatemenus=[{'buttons': [{'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}], 'label': 'Play', 'method': 'animate'}]}],
        sliders=[{'steps': [{'args': [[str(year)], {'frame': {'duration': 500, 'redraw': True}, 'mode': 'immediate'}], 'label': str(year), 'method': 'animate'} for year in years]}],
        plot_bgcolor='rgba(0,0,255,0.1)'  # Set background to light blue
    )

    # Add image
    image_url = "https://raw.githubusercontent.com/CHEAH80/MCM7183_Population_Malaysia/main/assets/malaysia.jpg"
    image = html.Div([
        html.Img(src=image_url, style={'width': '300px', 'display': 'block', 'margin': 'auto'}),
    ], style={'textAlign': 'center', 'marginTop': '20px'})

    return html.Div([
        dcc.Graph(figure=fig3),  # Only keep the figure and image
        image
    ])

# Main layout with side navigation and content
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.Row([dbc.Col(html.H1("The Population of Malaysia", className="text-center"), width=12)], className="mt-5"),
    dbc.Row([dbc.Col(html.H1("(1970 - 2024)", className="text-center"), width=12)], className="mb-4"),
    dbc.Row([dbc.Col(side_nav, width=2), dbc.Col(html.Div(id='page-content'), width=10)])
])

# Callback to update page content based on selected tab
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
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
