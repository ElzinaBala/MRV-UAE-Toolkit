import os
import io
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table
import plotly.express as px
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import zipfile

app = Dash(__name__)
app.title = "UAE GHG MRV Dashboard"
server = app.server

REQUIRED_COLUMNS = ['Year', 'Sector', 'Gas', 'Activity', 'Emission Factor', 'Unit']
processed_data = None

def load_default_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    outputs_dir = os.path.join(base_dir, 'outputs')
    df_sector = pd.read_csv(os.path.join(outputs_dir, 'emissions_by_sector.csv'))
    df_gas = pd.read_csv(os.path.join(outputs_dir, 'emissions_by_gas.csv'))
    df_yearly = pd.read_csv(os.path.join(outputs_dir, 'yearly_emissions_changes.csv'))
    return df_sector, df_gas, df_yearly

default_sector, default_gas, default_yearly = load_default_data()

app.layout = html.Div([
    html.H1("UAE GHG Emissions Dashboard"),

    html.H2("Upload Custom GHG Inventory Data (CSV)"),
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or Select a CSV File']),
        style={
            'width': '50%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
        },
        multiple=False
    ),
    html.Div(id='upload-status'),

    html.H2("Uploaded Data Preview"),
    dash_table.DataTable(id='data-preview', page_size=5),

    html.Button("Download Reports (ZIP: Excel + PDF)", id='download-btn', n_clicks=0),
    dcc.Download(id='download-data'),

    html.H2("Emissions by Sector"),
    dcc.Graph(id='sector-graph'),

    html.H2("Emissions by Gas"),
    dcc.Graph(id='gas-graph'),

    html.H2("Total Annual Emissions"),
    dcc.Graph(id='total-emissions-graph'),

    html.H2("Year-over-Year Change (%)"),
    dcc.Graph(id='change-percentage-graph')
])

def validate_uploaded_data(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    return missing

def process_data(df):
    df['Emissions (kg)'] = df['Activity'] * df['Emission Factor']
    sector = df.groupby(['Year', 'Sector'])['Emissions (kg)'].sum().reset_index()
    gas = df.groupby(['Year', 'Gas'])['Emissions (kg)'].sum().reset_index()
    yearly = df.groupby('Year')['Emissions (kg)'].sum().reset_index()
    yearly['Change (%)'] = yearly['Emissions (kg)'].pct_change().fillna(0) * 100
    return sector, gas, yearly

@app.callback(
    Output('upload-status', 'children'),
    Output('data-preview', 'data'),
    Output('data-preview', 'columns'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_file_upload(contents, filename):
    global processed_data
    if contents is None:
        return '', [], []

    content_type, content_string = contents.split(',')
    decoded = pd.read_csv(io.StringIO(content_string))
    
    missing = validate_uploaded_data(decoded)
    if missing:
        return f"Upload failed. Missing columns: {', '.join(missing)}", [], []

    sector, gas, yearly = process_data(decoded)
    processed_data = {'sector': sector, 'gas': gas, 'yearly': yearly}
    preview_data = decoded.head().to_dict('records')
    preview_columns = [{"name": i, "id": i} for i in decoded.columns]
    return f"File '{filename}' uploaded and processed successfully.", preview_data, preview_columns

def generate_pdf_report(yearly_data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 12)
    text.textLine("UAE GHG Inventory - Yearly Summary Report")
    text.textLine("")

    for index, row in yearly_data.iterrows():
        line = f"Year: {row['Year']}, Emissions (kg): {row['Emissions (kg)']:.2f}, Change (%): {row['Change (%)']:.2f}"
        text.textLine(line)

    c.drawText(text)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

@app.callback(
    Output('download-data', 'data'),
    Input('download-btn', 'n_clicks')
)
def download_reports(n_clicks):
    if n_clicks == 0 or not processed_data:
        return None

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        processed_data['sector'].to_excel(writer, sheet_name='By Sector', index=False)
        processed_data['gas'].to_excel(writer, sheet_name='By Gas', index=False)
        processed_data['yearly'].to_excel(writer, sheet_name='Yearly Changes', index=False)
    excel_buffer.seek(0)

    pdf_buffer = generate_pdf_report(processed_data['yearly'])

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode='w') as zf:
        zf.writestr('ghg_inventory_report.xlsx', excel_buffer.read())
        pdf_buffer.seek(0)
        zf.writestr('ghg_yearly_summary.pdf', pdf_buffer.read())
    zip_buffer.seek(0)

    return dcc.send_bytes(zip_buffer.read(), "processed_reports.zip")

@app.callback(Output('sector-graph', 'figure'), Input('upload-data', 'contents'))
def update_sector_graph(contents):
    data = processed_data['sector'] if processed_data else default_sector
    return px.line(data, x='Year', y='Emissions (kg)', color='Sector', title='Emissions by Sector')

@app.callback(Output('gas-graph', 'figure'), Input('upload-data', 'contents'))
def update_gas_graph(contents):
    data = processed_data['gas'] if processed_data else default_gas
    return px.line(data, x='Year', y='Emissions (kg)', color='Gas', title='Emissions by Gas')

@app.callback(Output('total-emissions-graph', 'figure'), Input('upload-data', 'contents'))
def update_total_emissions_graph(contents):
    data = processed_data['yearly'] if processed_data else default_yearly
    return px.bar(data, x='Year', y='Emissions (kg)', title='Total Annual Emissions')

@app.callback(Output('change-percentage-graph', 'figure'), Input('upload-data', 'contents'))
def update_change_percentage_graph(contents):
    data = processed_data['yearly'] if processed_data else default_yearly
    return px.line(data, x='Year', y='Change (%)', markers=True, title='Year-over-Year Emissions Change')

if __name__ == '__main__':
    app.run(debug=True)
