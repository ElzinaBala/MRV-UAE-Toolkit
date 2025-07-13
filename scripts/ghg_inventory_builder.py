import pandas as pd
import os

def load_data(filepath):
    """
    Load GHG inventory data CSV file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_csv(filepath)

def aggregate_emissions_by_sector(df):
    """
    Aggregate emissions by sector and year.
    Emissions calculated as Activity * Emission Factor.
    """
    df['Emissions (kg)'] = df['Activity'] * df['Emission Factor']
    grouped = df.groupby(['Year', 'Sector'])['Emissions (kg)'].sum().unstack()
    return grouped

def aggregate_emissions_by_gas(df):
    """
    Aggregate emissions by gas and year.
    """
    df['Emissions (kg)'] = df['Activity'] * df['Emission Factor']
    grouped = df.groupby(['Year', 'Gas'])['Emissions (kg)'].sum().unstack()
    return grouped

def calculate_yearly_changes(df):
    """
    Calculate total emissions per year and year-over-year percent changes.
    """
    df['Emissions (kg)'] = df['Activity'] * df['Emission Factor']
    total = df.groupby('Year')['Emissions (kg)'].sum().reset_index()
    total['Change (%)'] = total['Emissions (kg)'].pct_change() * 100
    total.fillna(0, inplace=True)
    return total

def save_reports(df_sector, df_gas, df_yearly, output_dir):
    """
    Save aggregated data to CSV and Excel files.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    sector_csv = os.path.join(output_dir, 'emissions_by_sector.csv')
    df_sector.to_csv(sector_csv)
    
    gas_csv = os.path.join(output_dir, 'emissions_by_gas.csv')
    df_gas.to_csv(gas_csv)
    
    yearly_csv = os.path.join(output_dir, 'yearly_emissions_changes.csv')
    df_yearly.to_csv(yearly_csv, index=False)

    excel_path = os.path.join(output_dir, 'ghg_inventory_report.xlsx')
    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        df_sector.to_excel(writer, sheet_name='By Sector')
        df_gas.to_excel(writer, sheet_name='By Gas')
        df_yearly.to_excel(writer, sheet_name='Yearly Changes', index=False)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'uae_ghg_inventory_mock.csv')
    output_dir = os.path.join(base_dir, 'outputs')
    
    print(f"Loading data from: {data_path}")
    df = load_data(data_path)
    
    print("Aggregating emissions by sector...")
    df_sector = aggregate_emissions_by_sector(df)
    
    print("Aggregating emissions by gas...")
    df_gas = aggregate_emissions_by_gas(df)
    
    print("Calculating yearly emission changes...")
    df_yearly = calculate_yearly_changes(df)
    
    print(f"Saving reports to: {output_dir}")
    save_reports(df_sector, df_gas, df_yearly, output_dir)
    
    print("GHG inventory reports generated successfully.")

if __name__ == "__main__":
    main()
