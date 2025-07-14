"""
GHG Inventory Mock Data Generator
Author: Elzina Salah
Description:
Generates a realistic mock GHG inventory dataset aligned with UNFCCC Tier 1 sectors for showcase purposes.

- Sectors: Energy, IPPU, AFOLU, Waste
- Gases: CO2, CH4, N2O, HFCs, PFCs, SF6
- Years: 2015 - 2021
- Includes sector-specific activity units and gas-specific emission factors.

Output:
- data/uae_ghg_inventory_mock.csv
"""

import pandas as pd
import numpy as np
import os

years = list(range(2015, 2022))
sectors = ['Energy', 'IPPU', 'AFOLU', 'Waste']
gases = ['CO2', 'CH4', 'N2O', 'HFCs', 'PFCs', 'SF6']

sector_units = {
    'Energy': 'Terajoules (TJ)',
    'IPPU': 'Tonnes of Product',
    'AFOLU': 'Head of Cattle / Hectares',
    'Waste': 'Tonnes of Waste'
}

emission_factors = {
    'Energy':    {'CO2': 2.8, 'CH4': 0.035, 'N2O': 0.01,  'HFCs': 0.0003, 'PFCs': 0.00003, 'SF6': 0.000003},
    'IPPU':      {'CO2': 1.9, 'CH4': 0.02,  'N2O': 0.005, 'HFCs': 0.0002, 'PFCs': 0.00002, 'SF6': 0.000002},
    'AFOLU':     {'CO2': 1.5, 'CH4': 0.04,  'N2O': 0.015, 'HFCs': 0.0001, 'PFCs': 0.00001, 'SF6': 0.000001},
    'Waste':     {'CO2': 2.0, 'CH4': 0.045, 'N2O': 0.012, 'HFCs': 0.00025,'PFCs': 0.000025,'SF6': 0.0000025}
}

activity_ranges = {
    'Energy': (40000, 70000), 
    'IPPU': (20000, 40000),
    'AFOLU': (10000, 25000),
    'Waste': (5000, 15000)
}

data = []

for year in years:
    for sector in sectors:
        activity = np.random.randint(*activity_ranges[sector])
        unit = sector_units[sector]
        for gas in gases:
            ef = emission_factors[sector][gas]
            data.append({
                'Year': year,
                'Sector': sector,
                'Gas': gas,
                'Activity': activity,
                'Emission Factor': ef,
                'Unit': unit
            })

df = pd.DataFrame(data)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'uae_ghg_inventory_mock.csv')
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
df.to_csv(DATA_PATH, index=False)

print(f"Mock inventory data generated and saved to: {DATA_PATH}")
