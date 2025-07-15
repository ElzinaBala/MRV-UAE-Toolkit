import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Initialize the Dash app
app = Dash(__name__)
app.title = "UAE GHG MRV Dashboard"

# Load data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outputs_dir = os.path.join(base_dir, 'outputs')
    df_sector = pd.read_csv(os.path.join(outputs_dir, 'emissions_by_sector.csv'))
    df_gas = pd.read_csv(os.path.join(outputs_dir, 'emissions_by_gas.csv'))
    df_yearly = pd.read_csv(os.path.join(outputs_dir, 'yearly_emissions_changes.csv'))
    return df_sector, df_gas, df_yearly

df_sector, df_gas, df_yearly = load_data()

# Dropdown options
sector_options = [{'label': sector, 'value': sector} for sector in df_sector.columns if sector != 'Year']
gas_options = [{'label': gas, 'value': gas} for gas in df_gas.columns if gas != 'Year']

# App layout
app.layout = html.Div(style={'font-family': 'Arial, sans-serif', 'margin': '20px'}, children=[
    html.H1("UAE GHG Emissions Monitoring", style={'textAlign': 'center', 'color': '#003366'}),

    html.Div([
        html.Div([
            html.H3("Emissions by Sector", style={'color': '#006699'}),
            dcc.Dropdown(
                id='sector-dropdown',
                options=sector_options,
                value=sector_options[0]['value'] if sector_options else None,
                style={'marginBottom': '20px'}
            ),
            dcc.Graph(id='sector-graph')
        ], className='six columns', style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div([
            html.H3("Emissions by Gas", style={'color': '#006699'}),
            dcc.Dropdown(
                id='gas-dropdown',
                options=gas_options,
                value=gas_options[0]['value'] if gas_options else None,
                style={'marginBottom': '20px'}
            ),
            dcc.Graph(id='gas-graph')
        ], className='six columns', style={'width': '48%', 'display': 'inline-block', 'marginLeft': '4%'})
    ]),

    html.H2("Total Annual GHG Emissions", style={'textAlign': 'center', 'color': '#003366', 'marginTop': '40px'}),
    dcc.Graph(
        id='total-emissions-graph',
        figure=px.bar(df_yearly, x='Year', y='Emissions (kg)', color='Emissions (kg)',
                      title='Total Emissions by Year',
                      color_continuous_scale='Viridis')
    ),

    html.H2("Year-over-Year Change (%)", style={'textAlign': 'center', 'color': '#003366', 'marginTop': '40px'}),
    dcc.Graph(
        id='change-percentage-graph',
        figure=px.line(df_yearly, x='Year', y='Change (%)', markers=True,
                       title='Year-over-Year Percentage Change',
                       line_shape='spline', render_mode='svg',
                       color_discrete_sequence=['#FF5733'])
    )
])

# Callback to update sector emissions graph
@app.callback(
    Output('sector-graph', 'figure'),
    Input('sector-dropdown', 'value')
)
def update_sector_graph(selected_sector):
    if selected_sector:
        fig = px.line(df_sector, x='Year', y=selected_sector,
                      title=f'{selected_sector} Emissions Over Time',
                      markers=True, color_discrete_sequence=['#1f77b4'])
        return fig
    return {}

# Callback to update gas emissions graph
@app.callback(
    Output('gas-graph', 'figure'),
    Input('gas-dropdown', 'value')
)
def update_gas_graph(selected_gas):
    if selected_gas:
        fig = px.line(df_gas, x='Year', y=selected_gas,
                      title=f'{selected_gas} Emissions Over Time',
                      markers=True, color_discrete_sequence=['#2ca02c'])
        return fig
    return {}

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
