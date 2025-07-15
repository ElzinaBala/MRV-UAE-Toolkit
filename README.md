# UAE GHG MRV Toolkit

This project provides a comprehensive Measurement, Reporting, and Verification (MRV) toolkit for greenhouse gas (GHG) inventory management, reporting, and visualization. It is designed to support the UAE's climate action commitments and tracking under Article 6 of the Paris Agreement.

## Live Dashboard

Access the live dashboard here:
https://mrv-uae-toolkit.onrender.com

## Features

- GHG Inventory Builder using Tier 1 methodology
- Aggregation and reporting of emissions by sector, gas, and year
- Year-over-year change analysis
- Interactive dashboard built with Dash (Plotly)
- Optional user data upload with validation (planned feature)
- Exportable reports in CSV, Excel, and PDF formats

## Project Structure

MRV-UAE-Toolkit/
│
├── data/ # Raw and mock input data
├── outputs/ # Generated reports
├── scripts/ # Processing scripts
│ ├── ghg_inventory_builder.py
│ └── generate_mock_inventory.py
├── dashboard/ # Dash application
│ └── app.py
├── requirements.txt # Python dependencies
├── .gitignore # Git ignore rules
└── README.md # Project documentation


