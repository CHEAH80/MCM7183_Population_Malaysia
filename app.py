import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
data = pd.read_csv('https://raw.githubusercontent.com/CHEAH80/MCM7183_Population_Malaysia/refs/heads/main/assets/population_malaysia.csv')

# Filter data for home page
home_data = data[(data['sex'] == 'both') & (data['age'] == 'overall') & (data['ethnicity'] == 'overall')]

# Filter data for Page 1
sex_data = data[(data['year'] >= 1970) & (data['sex'].isin(['male', 'female'])) & 
                (data['age'] == 'overall') & (data['ethnicity'] == 'overall')]

# Filter data for Page 2
ethnicity_data = data[data['ethnicity'] != 'overall']
years = ethnicity_data['year'].unique()

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Malaysia Population By Cheah Yew Chung"
server = app.server

# Sidebar layout with logo
side_nav = dbc.Nav(
    [    
        html.H5("Navigation", className="my-3"),
        dbc.NavLink("Home Page", href="/", active="exact"),
        dbc.NavLink("By Sex", href="/page-1", active="exact"),
        dbc.NavLink("By Ethnicity", href="/page-2", active="exact"),
        dbc.NavLink("By Age", href="/page-3", active="exact"),  # New Page Link
    ],
    vertical=True,
    pills=True,
    style={"backgroundColor": "#ede8ff"}  # Light blue background color
)

# Title style
title_style = {'fontSize': '24px', 'textAlign': 'center', 'marginTop': '20px'}

# Reusable function to add image with the Summary button and text on top
def add_image_with_summary(image_url, button_id, text_id, summary_text):
    return html.Div([ 
        html.Button("Summary", id=button_id, n_clicks=0, style={'display': 'block', 'margin': '20px auto'}),
        html.Div(summary_text, id=text_id, style={'textAlign': 'center', 'display': 'none', 'marginTop': '10px'}),
        html.Div(style={'height': '20px'}),  
        html.Img(src=image_url, style={'width': '300px', 'display': 'block', 'margin': 'auto'}),
    ], style={'textAlign': 'center', 'marginTop': '20px'})

# Home Page
def create_home_page():
    fig = px.scatter(
        home_data, 
        x='year', 
        y='population', 
        color='population',  
        size='population',
        labels={'year': 'Year', 'population': 'Population'}
    )

    fig.add_traces(go.Scatter(
        x=home_data['year'], 
        y=home_data['population'], 
        mode='lines', 
        name='Trendline',
        line=dict(color='red', width=2),
        showlegend=True
    ))

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Population",
        title_x=0.5,
        plot_bgcolor='rgba(0,0,255,0.1)',  
        xaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor='LightGray',
            rangeslider=dict(visible=True),  
            rangeselector=dict(               
                buttons=list([
                    dict(count=10, label="Last 10 Years", step="year", stepmode="backward"),
                    dict(count=20, label="Last 20 Years", step="year", stepmode="backward"),
                    dict(step="all", label="All Time")
                ])
            )
        ),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='LightGray'),
        font=dict(size=14)
    )

    fig.add_annotation(
        x=2020,
        y=home_data[home_data['year'] == 2020]['population'].values[0],
        text="Population drop due to COVID-19",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        font=dict(color='black', size=12)
    )

    image_url = "https://raw.githubusercontent.com/CHEAH80/MCM7183_Population_Malaysia/main/assets/malaysia.jpg"
    summary_text = ("The Malaysian population exhibited a consistent growth trajectory from 1970 to 2024. "
                    "However, a unique demographic anomaly occurred in 2020, marked by a decline in population "
                    "due to the unprecedented impact of the COVID-19 pandemic. Subsequent to this temporary downturn, "
                    "the population gradually rebounded in 2021, and by 2023, the growth rate had returned to its historical norm.")
    
    return html.Div([
        html.H1("Population in Millions over the Years", style=title_style),
        dcc.Graph(figure=fig),
        add_image_with_summary(image_url, "summary-button-home", "summary-text-home", summary_text)
    ])

# Page 1 - Population by Sex with Summary Button and Image
def create_page_1():
    combined_data = sex_data.groupby('year').agg({'population': 'sum'}).reset_index()
    combined_data['sex'] = 'Both'
    all_sex_data = pd.concat([sex_data, combined_data], ignore_index=True)
    
    fig = px.bar(all_sex_data, x='sex', y='population', color='sex', animation_frame='year',
                 title="Population by Sex and Year")
    
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    
    # Set fixed y-axis range to 35,000
    fig.update_layout(
        title={'text': "Population in Millions by Sex and Year", 'x': 0.5, 'font': {'size': 24}},
        plot_bgcolor='rgba(0,0,255,0.1)',
        yaxis=dict(range=[0, 35000])  # Fixed y-axis range
    )
    
    # Add the image and summary text for Page 1
    image_url = "https://raw.githubusercontent.com/CHEAH80/MCM7183_Population_Malaysia/main/assets/malaysia.jpg"
    summary_text = ("According to the bar chart, Malaysia has consistently exhibited a male-dominant population structure. "
                    "This trend is further substantiated by data indicating a significant increase in the male population compared to females from 1970 to 2024. "
                    "The disparity is particularly noteworthy, with males outnumbering females by a margin ranging from 2.85% to 10.55% during this period. "
                    "For a deeper exploration of this phenomenon, you can refer to the UPM research portal link"
                    " (https://myageing.upm.edu.my/artikel/interactive_malaysias_skewed_sex_ratio_what_it_means_and_what_must_be_done-67695).")

    return html.Div([
        html.H1("Population by Sex", style=title_style),
        dcc.Graph(figure=fig),
        add_image_with_summary(image_url, "summary-button-page-1", "summary-text-page-1", summary_text)
    ])

# Page 2 - Population by Ethnicity with Slider and Summary Button
def create_page_2():
    fig = go.Figure()
    df_year = ethnicity_data[ethnicity_data['year'] == years[0]]
    fig.add_trace(go.Pie(labels=df_year['ethnicity'], values=df_year['population'], textinfo='label+percent'))
    
    fig.update_layout(title={'text': "Population Distribution by Ethnicity and Year", 'x': 0.5, 'font': {'size': 24}})

    frames = [go.Frame(data=[go.Pie(labels=ethnicity_data[ethnicity_data['year'] == year]['ethnicity'],
                                    values=ethnicity_data[ethnicity_data['year'] == year]['population'],
                                    textinfo='label+percent')], 
                       name=str(year)) for year in years]
    
    fig.frames = frames

    fig.update_layout(
        updatemenus=[{'buttons': [{'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}], 
                                    'label': 'Play', 'method': 'animate'}]}],
        sliders=[{'steps': [{'args': [[str(year)], {'frame': {'duration': 500, 'redraw': True}, 'mode': 'immediate'}], 
                            'label': str(year), 'method': 'animate'} for year in years]}],
        plot_bgcolor='rgba(0,0,255,0.1)'
    )

    image_url = "https://raw.githubusercontent.com/CHEAH80/MCM7183_Population_Malaysia/main/assets/malaysia.jpg"
    summary_text = ("The pie chart reveals a significant evolution in Malaysia's ethnic composition between 1980 and 2024. "
                    "Notably, the relative proportions of the Chinese and Indian populations have decreased during this period. "
                    "Additionally, the Bumiputera category has transformed, expanding from a single classification to encompass both Malay Bumiputera "
                    "and Other Bumiputera, including indigenous groups such as Orang Asli, Siam, Sabahan, and Sarawakian. "
                    "A particularly noteworthy trend is the substantial growth in the Other non-citizens category,"
                    "increasing from 2.18% in 1980 to 9.97% in 2024. This demographic shift can be attributed in part to Malaysia's government "
                    "policy of accepting refugees from conflict-ridden regions and the allure of Malaysia's lower cost of living, "
                    "which has attracted migrants from developed countries such as China, Japan, and Korea.")

    return html.Div([
        html.H1("Population by Ethnicity", style=title_style),
        dcc.Graph(figure=fig),
        add_image_with_summary(image_url, "summary-button-page-2", "summary-text-page-2", summary_text)
    ])

# Page 3 - Population Pyramid by Age and Summary Button
def create_page_3():
    years = data['year'].unique()
    initial_year = years[-1]  # Set to the most recent year available

    fig = create_pyramid_chart(data, initial_year)

    image_url = "https://raw.githubusercontent.com/CHEAH80/MCM7183_Population_Malaysia/main/assets/malaysia.jpg"
    summary_text = ("The population pyramid for Malaysia has undergone a significant transformation from 1970 to 2024, "
                    "transitioning from a classic triangular shape to a more columnar structure. This shift is characterized by "
                    "a narrowing of the base, representing the younger age groups, and a corresponding expansion of the middle-aged cohort. "
                    "This demographic evolution suggests a growing proportion of individuals within the productive age range, "
                    "coupled with a rising elderly population as the number of younger generations diminishes. "
                    "The data indicates that Malaysian life expectancy has increased significantly over the past few decades, "
                    "rising from an average of 70+ years in 1970 to 84 years in 2024.")


    return html.Div([
        html.H1("Population Pyramid by Age", style=title_style),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in years],
            value=initial_year,
            clearable=False,
            style={'marginBottom': '20px', 'backgroundColor': '#ede8ff'}  # Light blue background color
        ),
        dcc.Graph(id='population-pyramid', figure=fig),
        add_image_with_summary(image_url, "summary-button-page-3", "summary-text-page-3", summary_text)
    ])

# Function to create population pyramid chart
def create_pyramid_chart(df, year):
    filtered_data = filter_data(df, year)
    
    males = filtered_data[filtered_data['sex'] == 'male']
    females = filtered_data[filtered_data['sex'] == 'female']
    
    fig = go.Figure()

    # Add male trace (left side, population negative)
    fig.add_trace(go.Bar(
        x=-males['population'],
        y=males['age'],
        name=f'Male {year}',
        orientation='h',
        marker_color='rgba(0, 123, 255, 0.8)',
        hoverinfo='x+y+text',
    ))

    # Add female trace (right side, population positive)
    fig.add_trace(go.Bar(
        x=females['population'],
        y=females['age'],
        name=f'Female {year}',
        orientation='h',
        marker_color='rgba(255, 99, 132, 0.8)',
        hoverinfo='x+y+text',
    ))

    # Update layout
    fig.update_layout(
        title=f'Population Pyramid for {year}',
        xaxis=dict(
            title='Population',
            tickfont_size=12,
            zeroline=True,
            zerolinecolor='gray'
        ),
        yaxis=dict(
            title='Age Group',
            tickfont_size=12,
        ),
        barmode='overlay',
        bargap=0.1,
        paper_bgcolor='white',
        plot_bgcolor='whitesmoke',
        margin=dict(l=100, r=100, t=100, b=100),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
    )

    return fig

# Filter data for population pyramid
def filter_data(df, year):
    filtered_df = df[(df['sex'].isin(['male', 'female'])) & 
                     (df['year'] == year) & 
                     (df['age'] != 'overall') & 
                     (df['ethnicity'] == 'overall')]  # Exclude 'overall' age group and focus on overall ethnicity
    return filtered_df

# App callback to update the pyramid chart based on selected year
@app.callback(
    Output('population-pyramid', 'figure'),
    Input('year-dropdown', 'value')
)
def update_pyramid_chart(selected_year):
    return create_pyramid_chart(data, selected_year)

# Individual callbacks for toggling the summary text visibility for each page
@app.callback(
    Output('summary-text-home', 'style'),
    Input('summary-button-home', 'n_clicks')
)
def toggle_home_summary_text(n_clicks_home):
    if n_clicks_home and n_clicks_home % 2 == 1:
        return {'display': 'block'}
    return {'display': 'none'}

@app.callback(
    Output('summary-text-page-1', 'style'),
    Input('summary-button-page-1', 'n_clicks')
)
def toggle_page_1_summary_text(n_clicks_page_1):
    if n_clicks_page_1 and n_clicks_page_1 % 2 == 1:
        return {'display': 'block'}
    return {'display': 'none'}

@app.callback(
    Output('summary-text-page-2', 'style'),
    Input('summary-button-page-2', 'n_clicks')
)
def toggle_page_2_summary_text(n_clicks_page_2):
    if n_clicks_page_2 and n_clicks_page_2 % 2 == 1:
        return {'display': 'block'}
    return {'display': 'none'}

@app.callback(
    Output('summary-text-page-3', 'style'),
    Input('summary-button-page-3', 'n_clicks')
)
def toggle_page_3_summary_text(n_clicks_page_3):
    if n_clicks_page_3 and n_clicks_page_3 % 2 == 1:
        return {'display': 'block'}
    return {'display': 'none'}

# Main Layout
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.Row([dbc.Col(html.H1("The Population of Malaysia", className="text-center"), width=12)], className="mt-5"),
    dbc.Row([dbc.Col(html.H1("(1970 - 2024)", className="text-center"), width=12)], className="mb-4"),
    dbc.Row([
        dbc.Col(side_nav, width=1),  # Sidebar
        dbc.Col(html.Div(id='page-content', className="a4-margin"), width=7, className="offset-")  # Main content centered
    ], justify="center")  # Center the row content
], fluid=True)

# Update the page content based on the current URL path
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/page-1":
        return create_page_1()
    elif pathname == "/page-2":
        return create_page_2()
    elif pathname == "/page-3":
        return create_page_3()
    else:
        return create_home_page()

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True) 
