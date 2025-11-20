# Green Bond Tracker Documentation

## Overview

The Green Bond Tracker is an educational project designed to demonstrate how to track, analyze, and visualize green bond data with geographic information system (GIS) capabilities.

**Important:** This project is for educational and analytical purposes only. It is not intended for investment advice or financial decision-making.

## Project Structure

```
green-bond-tracker-project/
├── data/               # Data files
│   ├── green_bonds.csv         # Sample green bond data
│   └── countries_geo.json      # Country geometries with ISO codes
├── src/                # Source code
│   ├── __init__.py             # Package initialization
│   └── data_loader.py          # Data loading and validation functions
├── notebooks/          # Jupyter notebooks
│   └── green_bond_demo.ipynb   # Demo notebook with visualizations
├── docs/               # Documentation
│   └── README.md               # This file
├── tests/              # Test files
│   └── test_data_loader.py     # Tests for data loading functions
├── maps/               # Generated map outputs
├── requirements.txt    # Python dependencies
└── README.md           # Project README
```

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/gabrielpriante/green-bond-tracker-project.git
cd green-bond-tracker-project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Usage

#### Loading Data

```python
from src.data_loader import load_green_bonds, load_country_geometries

# Load green bond data
bonds = load_green_bonds()

# Load country geometries
countries = load_country_geometries()
```

#### Validating Data

```python
from src.data_loader import validate_bond_data

is_valid, issues = validate_bond_data(bonds)
if is_valid:
    print("Data is valid!")
else:
    print("Issues found:", issues)
```

#### Joining Data with Geography

```python
from src.data_loader import join_bonds_with_geo

# Create geographic dataset
geo_bonds = join_bonds_with_geo(bonds, countries)
```

#### Getting Summary Statistics

```python
from src.data_loader import get_summary_statistics

stats = get_summary_statistics(bonds)
print(f"Total bonds: {stats['total_bonds']}")
print(f"Total amount: ${stats['total_amount_usd_millions']:.2f}M")
```

## Data Schema

### Green Bonds CSV

| Column | Type | Description |
|--------|------|-------------|
| bond_id | string | Unique identifier for the bond |
| issuer | string | Name of the bond issuer |
| country_code | string | ISO 3166-1 alpha-3 country code |
| issue_date | date | Date the bond was issued |
| maturity_date | date | Date the bond matures |
| amount_usd_millions | float | Bond amount in USD millions |
| currency | string | Original currency of the bond |
| coupon_rate | float | Annual coupon rate (%) |
| use_of_proceeds | string | Category of green project funded |
| certification | string | Certification standard (e.g., Climate Bonds Initiative) |

### Country Geometries GeoJSON

| Property | Type | Description |
|----------|------|-------------|
| name | string | Country name |
| iso_a3 | string | ISO 3166-1 alpha-3 code |
| iso_a2 | string | ISO 3166-1 alpha-2 code |
| continent | string | Continent name |
| geometry | object | GeoJSON geometry (Polygon/MultiPolygon) |

## Features

### Data Loading and Validation
- Load green bond data from CSV
- Load country geometries from GeoJSON
- Validate data completeness and correctness
- Check for duplicate bond IDs
- Validate ISO country codes

### Geographic Analysis
- Join bond data with country geometries
- Aggregate bonds by country
- Create choropleth maps
- Visualize geographic distribution

### Statistical Analysis
- Calculate summary statistics
- Analyze use of proceeds
- Time series analysis
- Certification standard analysis

## Demo Notebook

The `notebooks/green_bond_demo.ipynb` notebook provides a comprehensive demonstration including:

1. Loading and validating data
2. Summary statistics
3. Use of proceeds analysis with visualizations
4. Geographic choropleth maps
5. Time series analysis
6. Certification analysis

To run the notebook:
```bash
jupyter notebook notebooks/green_bond_demo.ipynb
```

## API Reference

### `load_green_bonds(filepath=None)`
Load green bond data from CSV file.

**Parameters:**
- `filepath` (str, optional): Path to CSV file. Uses default if None.

**Returns:**
- `pd.DataFrame`: Green bond data

**Raises:**
- `FileNotFoundError`: If file not found
- `ValueError`: If required columns missing

### `load_country_geometries(filepath=None)`
Load country geometry data from GeoJSON.

**Parameters:**
- `filepath` (str, optional): Path to GeoJSON file. Uses default if None.

**Returns:**
- `gpd.GeoDataFrame`: Country geometries with ISO codes

### `validate_bond_data(df)`
Validate green bond data.

**Parameters:**
- `df` (pd.DataFrame): Bond data to validate

**Returns:**
- `tuple`: (is_valid: bool, issues: list)

### `join_bonds_with_geo(bonds_df, geo_df)`
Join bond data with country geometries.

**Parameters:**
- `bonds_df` (pd.DataFrame): Bond data
- `geo_df` (gpd.GeoDataFrame): Country geometries

**Returns:**
- `gpd.GeoDataFrame`: Joined data with aggregated bond statistics

### `get_summary_statistics(df)`
Calculate summary statistics.

**Parameters:**
- `df` (pd.DataFrame): Bond data

**Returns:**
- `dict`: Summary statistics

## Contributing

This is an educational project. Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See LICENSE file for details.

## Disclaimer

**IMPORTANT:** This project is for educational purposes only. The data, analysis, and visualizations provided are for learning and demonstration purposes. This project:

- Is NOT intended for investment advice
- Should NOT be used for financial decision-making
- Does NOT constitute professional financial guidance
- May contain simplified or sample data

Always consult qualified financial advisors before making investment decisions.

## Contact

For questions or feedback, please open an issue on GitHub.
