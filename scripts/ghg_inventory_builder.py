"""
GHG Inventory Builder Script
Author: Elzina Salah
Description: Calculates GHG emissions from activity data and emission factors using Tier 1 methodology.
"""

import pandas as pd
import os

# 🌍 Setup base paths relative to this script's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'uae_ghg_inventory_mock.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')

# 📥 Step 1: Load data
def load_data(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ File not found: {filepath}")
    print(f"📥 Loading data from {filepath}")
    return pd.read_csv(filepath)

# 🧮 Step 2: Calculate emissions using IPCC Tier 1 method
def calculate_emissions(df):
    df['Emissions (kg)'] = df['Activity'] * df['Emission Factor']
    return df

# 📊 Step 3: Aggregate emissions
def aggregate_data(df):
    sector_summary = df.groupby(['Year', 'Sector'])['Emissions (kg)'].sum().unstack()
    gas_summary = df.groupby(['Year', 'Gas'])['Emissions (kg)'].sum().unstack()
    yearly_total = df.groupby('Year')['Emissions (kg)'].sum().reset_index()
    yearly_total['Change (%)'] = yearly_total['Emissions (kg)'].pct_change() * 100
    return sector_summary, gas_summary, yearly_total

# 📤 Step 4: Export results
def export_results(sector_summary, gas_summary, yearly_total, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    sector_summary.to_csv(os.path.join(output_dir, 'emissions_by_sector.csv'))
    gas_summary.to_csv(os.path.join(output_dir, 'emissions_by_gas.csv'))
    yearly_total.to_csv(os.path.join(output_dir, 'yearly_emissions_changes.csv'), index=False)
    print(f"✅ Emission summaries exported to: {output_dir}")

# 🚀 Master pipeline
def run_inventory_pipeline():
    print("🔁 Running GHG Inventory Builder...\n")
    df = load_data(DATA_PATH)
    df = calculate_emissions(df)
    sector_summary, gas_summary, yearly_total = aggregate_data(df)
    export_results(sector_summary, gas_summary, yearly_total, OUTPUT_DIR)
    print("\n🏁 Finished: Inventory process complete.\n")

# 📌 Entry point
if __name__ == "__main__":
    run_inventory_pipeline()

