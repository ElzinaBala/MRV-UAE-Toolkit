import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Prepare data
OUTPUT_DIR = 'outputs'
CSV_FILE = os.path.join(OUTPUT_DIR, 'emissions_by_sector.csv')

def ensure_sample_data():
    if not os.path.exists(CSV_FILE):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        sample_data = pd.DataFrame({
            'Sector': ['Energy', 'Agriculture', 'Waste', 'IPPU'] * 3,
            'Year': [2020, 2020, 2020, 2020, 2021, 2021, 2021, 2021, 2022, 2022, 2022, 2022],
            'Emissions': [500, 200, 100, 150, 520, 210, 110, 160, 530, 215, 120, 170]
        })
        sample_data.to_csv(CSV_FILE, index=False)
        print(f"Sample data created at: {CSV_FILE}")

ensure_sample_data()
df = pd.read_csv(CSV_FILE)

external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(className='container mt-4', children=[
    html.H1('GHG Emissions Analytics Dashboard', className='text-center text-primary mb-4'),

    html.Div(className='row', children=[
        html.Div(className='col-md-6', children=[
            html.Label('Select Sector:', className='font-weight-bold'),
            dcc.Dropdown(
                id='sector-dropdown',
                options=[{'label': sector, 'value': sector} for sector in df['Sector'].unique()],
                value=df['Sector'].unique()[0],
                className='mb-4'
            )
        ]),
        html.Div(className='col-md-6', children=[
            html.Label('Select Year:', className='font-weight-bold'),
            dcc.Slider(
                id='year-slider',
                min=df['Year'].min(),
                max=df['Year'].max(),
                step=1,
                value=df['Year'].min(),
                marks={str(year): str(year) for year in df['Year'].unique()},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ])
    ]),

    html.Div(className='row', children=[
        html.Div(className='col-md-6', children=[dcc.Graph(id='line-plot')]),
        html.Div(className='col-md-6', children=[dcc.Graph(id='bar-chart')])
    ]),

    html.Div(className='row mt-4', children=[
        html.Div(className='col-md-6', children=[dcc.Graph(id='pie-chart')]),
        html.Div(className='col-md-6', children=[dcc.Graph(id='scatter-plot')])
    ]),

    html.Div(className='row mt-4', children=[
        html.Div(className='col-md-6', children=[dcc.Graph(id='heatmap')]),
        html.Div(className='col-md-6', children=[dcc.Graph(id='box-plot')])
    ]),

    html.Div(id='summary-stats', className='mt-4 p-3 bg-light border rounded')
])

@app.callback(
    [Output('line-plot', 'figure'),
     Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure'),
     Output('scatter-plot', 'figure'),
     Output('heatmap', 'figure'),
     Output('box-plot', 'figure'),
     Output('summary-stats', 'children')],
    [Input('sector-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_dashboard(selected_sector, selected_year):
    filtered_df = df[df['Sector'] == selected_sector]
    year_df = df[df['Year'] == selected_year]

    # Line Plot
    line_fig = px.line(
        filtered_df, x='Year', y='Emissions',
        title=f'Emissions Trend for {selected_sector}',
        markers=True,
        color_discrete_sequence=px.colors.sequential.Viridis
    )

    # Bar Chart
    bar_fig = px.bar(
        year_df, x='Sector', y='Emissions',
        title=f'Emissions by Sector in {selected_year}',
        color='Sector',
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    # Pie Chart
    pie_fig = px.pie(
        year_df, names='Sector', values='Emissions',
        title=f'Sectoral Contribution in {selected_year}',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Scatter Plot
    scatter_fig = px.scatter(
        df, x='Year', y='Emissions',
        color='Sector',
        symbol='Sector',
        title='Scatter of Emissions across Years and Sectors',
        color_discrete_sequence=px.colors.qualitative.Prism
    )

    # Heatmap
    heatmap_data = df.pivot_table(index='Sector', columns='Year', values='Emissions')
    heatmap_fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Viridis'
        )
    )
    heatmap_fig.update_layout(title='Emissions Intensity Heatmap', xaxis_title='Year', yaxis_title='Sector')

    # Box Plot
    box_fig = px.box(
        df, x='Sector', y='Emissions',
        title='Emissions Distribution by Sector',
        color='Sector',
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Summary Stats
    total_emissions = filtered_df['Emissions'].sum()
    max_year = filtered_df.loc[filtered_df['Emissions'].idxmax()]['Year']
    max_emissions = filtered_df['Emissions'].max()

    stats = html.Div([
        html.H5(f'Total Emissions for {selected_sector}: {total_emissions:.2f} MtCO2e', className='text-success'),
        html.H5(f'Peak Emissions in {max_year}: {max_emissions:.2f} MtCO2e', className='text-warning'),
        html.H5(f'Selected Year: {selected_year}', className='text-info')
    ])

    return line_fig, bar_fig, pie_fig, scatter_fig, heatmap_fig, box_fig, stats

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
