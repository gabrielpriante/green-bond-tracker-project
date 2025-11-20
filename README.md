# Green Bond Project Tracker

> **⚠️ IMPORTANT DISCLAIMER**  
> **This is an educational project for learning purposes only.**  
> **NOT intended for investment advice or financial decision-making.**  
> **Always consult qualified financial advisors before making investment decisions.**

A lightweight, open-source tracker for green bonds and sustainability-linked projects with GIS (Geographic Information System) support. Designed for learning, transparency, and portfolio-level insights.

## Features

- 📊 **Data Management**: Load and validate green bond data with ISO country codes
- 🗺️ **GIS Integration**: Visualize bond data on interactive choropleth maps
- 📈 **Analytics**: Generate summary statistics and time series analysis
- 📓 **Demo Notebook**: Comprehensive Jupyter notebook with examples
- ✅ **Data Validation**: Ensure data quality and completeness

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/gabrielpriante/green-bond-tracker-project.git
cd green-bond-tracker-project

# Install dependencies
pip install -r requirements.txt
```

### Usage

```python
from src.data_loader import (
    load_green_bonds,
    load_country_geometries,
    join_bonds_with_geo,
    get_summary_statistics
)
import matplotlib.pyplot as plt

# Load data from data/ folder
bonds = load_green_bonds()  # Loads data/green_bonds.csv
countries = load_country_geometries()  # Loads data/countries_geo.json

# Get statistics
stats = get_summary_statistics(bonds)
print(f"Total bonds: {stats['total_bonds']}")
print(f"Total amount: ${stats['total_amount_usd_millions']:.2f}M USD")

# Create geographic dataset and visualize
geo_bonds = join_bonds_with_geo(bonds, countries)

# Generate choropleth map (saved to maps/ folder)
fig, ax = plt.subplots(1, 1, figsize=(14, 8))
geo_bonds.plot(
    column='total_amount_usd_millions',
    ax=ax,
    legend=True,
    cmap='YlGn',
    edgecolor='black'
)
ax.set_title('Green Bonds by Country')
plt.savefig('maps/green_bonds_map.png', dpi=300, bbox_inches='tight')
plt.show()
```

**Note:** The `maps/` folder is a placeholder for storing generated geographic visualizations and map outputs from the analysis.

### Run the Demo Notebook

```bash
jupyter notebook notebooks/green_bond_demo.ipynb
```

The demo notebook includes:
- Data loading and validation
- Summary statistics
- Use of proceeds analysis
- Geographic choropleth maps
- Time series analysis
- Certification standard analysis

## Project Structure

```
green-bond-tracker-project/
├── data/               # Sample data files
│   ├── green_bonds.csv         # Green bond data with field descriptions
│   └── countries_geo.json      # Country geometries with ISO codes
├── src/                # Python source code
│   ├── __init__.py
│   └── data_loader.py          # Data loading and validation
├── notebooks/          # Jupyter notebooks
│   └── green_bond_demo.ipynb   # Demo with visualizations
├── docs/               # Documentation
│   └── README.md
├── tests/              # Unit tests
│   └── test_data_loader.py
├── maps/               # Output folder for generated maps and visualizations
└── requirements.txt    # Python dependencies
```

## Data Schema

### Green Bonds CSV
- `bond_id`: Unique bond identifier
- `issuer`: Bond issuer name
- `country_code`: ISO 3166-1 alpha-3 country code
- `issue_date`, `maturity_date`: Bond dates
- `amount_usd_millions`: Bond amount in USD millions
- `currency`: Original currency
- `coupon_rate`: Annual coupon rate (%)
- `use_of_proceeds`: Green project category
- `certification`: Certification standard

### Country Geometries GeoJSON
- `name`: Country name
- `iso_a3`: ISO 3166-1 alpha-3 code
- `iso_a2`: ISO 3166-1 alpha-2 code
- `continent`: Continent name
- `geometry`: GeoJSON polygon coordinates

## Documentation

Detailed documentation is available in the [`docs/`](docs/README.md) directory, including:
- API reference
- Data schema details
- Usage examples
- Contributing guidelines

## Requirements

- Python 3.8+
- pandas >= 2.0.0
- geopandas >= 0.14.0
- matplotlib >= 3.7.0
- jupyter >= 1.0.0

See [`requirements.txt`](requirements.txt) for the complete list.

## Testing

```bash
# Run tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=src
```

## Contributing

Contributions are welcome! This is an educational project aimed at helping people learn about green bonds and GIS data visualization. Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the terms specified in the LICENSE file.

## Disclaimer

**IMPORTANT LEGAL NOTICE:**

This project is for **educational and informational purposes only**. It is designed to help users learn about green bonds, data analysis, and geographic visualization.

This project:
- ❌ Is NOT investment advice
- ❌ Should NOT be used for making financial decisions
- ❌ Does NOT constitute professional financial guidance
- ❌ Makes NO guarantees about data accuracy or completeness
- ❌ Is NOT affiliated with any financial institution

The sample data provided may be simplified, outdated, or fictional. Always:
- ✅ Consult qualified financial advisors
- ✅ Verify data from official sources
- ✅ Conduct your own due diligence
- ✅ Understand the risks before making any investment

## Acknowledgments

- Green bond data structure inspired by industry standards
- GIS functionality powered by GeoPandas
- Built for educational purposes with transparency in mind

## Contact

For questions, feedback, or contributions, please open an issue on GitHub.

---

**Remember:** This is a learning tool, not a financial tool. Use responsibly! 📚🌱
