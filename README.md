# Green Bond Project Tracker

> **⚠️ IMPORTANT DISCLAIMER**  
> **This is an educational project for learning purposes only.**  
> **NOT intended for investment advice or financial decision-making.**  
> **Always consult qualified financial advisors before making investment decisions.**

A lightweight, open-source tracker for green bonds and sustainability-linked projects with GIS (Geographic Information System) support. Designed for learning, transparency, and portfolio-level insights.

## Features

- 📊 **Data Management**: Load and validate green bond data with comprehensive schema validation
- 🗺️ **GIS Integration**: Visualize bond data on static and interactive choropleth maps
- 📈 **Analytics**: Generate summary statistics and comparative analysis
- 📓 **Demo Notebook**: Comprehensive Jupyter notebook with examples
- ✅ **Data Validation**: Rigorous validation with row-level error reporting
- 🖥️ **Command Line Interface**: Easy-to-use CLI for validation, analysis, and visualization
- 🌐 **Interactive Maps**: Optional Folium-based interactive visualizations
- 🧪 **Well-Tested**: Comprehensive test suite with >80% code coverage

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/gabrielpriante/green-bond-tracker-project.git
cd green-bond-tracker-project

# Install the package in editable mode (recommended for development)
pip install -e .

# OR install with all optional features (interactive maps, notebooks, dev tools)
pip install -e ".[all]"

# OR use the Makefile
make install
```

### Command Line Interface (Recommended)

After installation, use the `gbt` command to work with green bond data:

```bash
# Show version
gbt --version

# Validate your bond data
gbt validate --input data/green_bonds.csv

# Get detailed validation report
gbt validate --input data/green_bonds.csv --output validation_report.csv --verbose

# Generate portfolio summary statistics
gbt summary --input data/green_bonds.csv --output-dir outputs/

# Get summary as JSON
gbt summary --input data/green_bonds.csv --json

# Generate interactive map (requires folium: pip install green-bond-tracker[interactive])
gbt map --input data/green_bonds.csv --output outputs/bonds_map.html

# Generate all static visualizations
gbt viz --input data/green_bonds.csv --output-dir outputs/

# Show help for any command
gbt --help
gbt validate --help
```

**Outputs:**
- `gbt validate`: Validates data quality, prints summary, optional CSV report with row-level flags
- `gbt summary`: Portfolio metrics (console table + CSV files in `outputs/`)
- `gbt map`: Interactive HTML choropleth map saved to specified file
- `gbt viz`: Static PNG visualizations saved to specified directory

## Logging and Error Handling

The Green Bond Tracker includes structured logging to help you understand what the tool is doing and diagnose issues when they occur.

### Logging Levels

By default, the tool runs in **INFO** mode, which shows informative progress messages:

```bash
# Normal operation with INFO logging
gbt validate --input data/green_bonds.csv
```

Output:
```
Validating: data/green_bonds.csv
17:34:06 [INFO] Starting validation of data/green_bonds.csv
17:34:06 [INFO] Loading bond data...
✓ Loaded 20 records
17:34:06 [INFO] Loaded 20 records from data/green_bonds.csv
17:34:06 [INFO] Running validation checks...
✓ Validation PASSED
```

### Global CLI Flags

Use these flags with any command to control logging behavior:

**`--verbose`** - Enable DEBUG logging for detailed execution steps:
```bash
# See detailed debug information
gbt --verbose validate --input data/green_bonds.csv
```

Output includes detailed steps:
```
2026-01-07 17:34:14 [DEBUG] green_bond_tracker: Logging initialized in DEBUG mode
2026-01-07 17:34:14 [DEBUG] green_bond_tracker: Loading green bonds from data/green_bonds.csv
2026-01-07 17:34:14 [DEBUG] green_bond_tracker: Successfully loaded 20 bonds from data/green_bonds.csv
...
```

**`--quiet`** - Suppress INFO logs (show WARN/ERROR only):
```bash
# Minimal output - only warnings and errors
gbt --quiet validate --input data/green_bonds.csv
```

Output shows only errors and warnings:
```
Validating: data/green_bonds.csv
✓ Loaded 20 records
✓ Validation PASSED
```

### When to Use Each Mode

- **Normal (INFO)**: Default for most users. Shows what the tool is doing without overwhelming detail.
- **Verbose (DEBUG)**: Use when debugging issues or wanting to understand internal operations. Includes full stack traces for errors.
- **Quiet (WARNING)**: Use in automated scripts or when you only want to see problems.

### Error Messages

The tool provides clear, actionable error messages:

#### File Not Found
```bash
gbt validate --input missing.csv
```
```
File Not Found: Green bonds data file not found: missing.csv
→ Check that the input file path is correct
```

#### Invalid Data Format
```bash
gbt validate --input bad_format.csv
```
```
Invalid Data: Missing required columns: bond_id, amount_usd_millions
→ Verify the CSV has required columns (bond_id, issuer, country_code, amount_usd_millions)
```

#### Empty Dataset
```bash
gbt summary --input empty.csv
```
```
⚠ Warning: Dataset is empty
→ Check that the input file contains valid bond data
```

#### Feature Not Available
```bash
gbt map --input data.csv  # without folium installed
```
```
Feature Not Available: Interactive maps require folium.
Install with: pip install 'green-bond-tracker[interactive]'
```

### Exit Codes

Commands exit with standard codes for easy scripting:

| Code | Meaning | Example |
|------|---------|---------|
| `0` | Success | Validation passed, data processed successfully |
| `1` | User/Input Error | File not found, invalid data, missing columns |
| `2` | Feature Not Implemented | Map command without folium installed |
| `3` | Unexpected Internal Error | Programming error, unexpected exception |

Example usage in a script:
```bash
#!/bin/bash
gbt validate --input data/green_bonds.csv
if [ $? -eq 0 ]; then
    echo "Validation passed, continuing..."
    gbt summary --input data/green_bonds.csv
else
    echo "Validation failed, stopping pipeline"
    exit 1
fi
```

### Troubleshooting Tips

1. **Run with `--verbose` first**: When encountering an error, rerun with `--verbose` to see detailed information.
   ```bash
   gbt --verbose validate --input data.csv
   ```

2. **Check error suggestions**: Error messages include `→` arrows with actionable suggestions.

3. **Validate exit codes**: In scripts, check exit codes to handle different failure modes appropriately.

4. **Review log output**: All logs go to stdout, so you can redirect them to a file:
   ```bash
   gbt validate --input data.csv > validation.log 2>&1
   ```

## Configuration

The Green Bond Tracker uses a centralized YAML configuration system that allows you to adapt the tool to new datasets, paths, and environments without editing source code.

### Configuration File

The default configuration file is `config.yaml` in the repository root. This file contains:

- **Paths**: Data input/output locations
- **Schema**: Expected columns, data types, and validation rules
- **Normalization**: How to process currency, date, and numeric fields
- **Map**: Visualization settings and defaults
- **Analytics**: Portfolio analysis parameters
- **Output**: Filenames for generated reports

### Using Custom Configuration

You can override the default configuration by providing a custom YAML file:

```bash
# Use a custom configuration file
gbt --config path/to/custom_config.yaml validate --input data.csv

# All subcommands respect the --config option
gbt --config custom.yaml summary
gbt --config custom.yaml map --output my_map.html
```

### Example Configuration

Here's a minimal example configuration:

```yaml
# Paths configuration
paths:
  raw_data: "data/green_bonds.csv"
  geo_data: "data/countries_geo.json"
  outputs: "outputs"
  maps: "maps"

# Schema configuration
schema:
  required_columns:
    - bond_id
    - issuer
    - country_code
    - amount_usd_millions
  
  optional_columns:
    - issue_date
    - maturity_date
    - currency
    - coupon_rate
    - use_of_proceeds
    - certification

# Analytics configuration
analytics:
  top_n: 5  # Number of top items in concentration analysis
  coverage_threshold: 80  # Minimum data coverage (%) for warnings

# Output filenames
output:
  portfolio_summary: "portfolio_summary.csv"
  data_coverage_report: "data_coverage_report.csv"
```

See `config.yaml` in the repository root for the complete default configuration with all available options and documentation.

### Command-Line Overrides

You can override configuration settings using command-line options:

```bash
# Override input path from config
gbt validate --input custom_data.csv

# Override output directory
gbt summary --output-dir custom_outputs/

# Override map output location
gbt map --output custom_map.html

# Override geographic data source
gbt viz --geo custom_countries.json
```

### Backward Compatibility

- If no configuration file is provided, the tool uses sensible defaults that match the current repository layout
- All CLI commands work without a configuration file
- Missing configuration values fall back to defaults with warning messages
- Command-line options always take precedence over configuration file settings

### Python API

For programmatic access, use the Python API:

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

## Visualizations

The project includes a dedicated `visuals.py` module with beginner-friendly functions for creating publication-quality charts. All functions are well-documented and easy to use.

### Available Visualizations

**1. Project Type Bar Chart**
- Shows the distribution of bonds across different green project categories (e.g., Renewable Energy, Clean Transportation)
- Helps identify which project types receive the most funding
- Creates a horizontal bar chart for easy reading of category names

```python
from src.visuals import create_project_type_bar_chart

fig = create_project_type_bar_chart(bonds)
plt.show()
```

**2. Choropleth Maps**
- Geographic visualizations showing bond data by country
- Uses color intensity to represent values (darker = higher)
- Can display total bond amounts or number of bonds per country
- Built on GeoJSON data with ISO country codes

```python
from src.visuals import create_choropleth_map

# Map showing total bond amounts
fig = create_choropleth_map(geo_bonds, column='total_amount_usd_millions')
plt.show()

# Map showing bond counts
fig = create_choropleth_map(geo_bonds, column='bond_count')
plt.show()
```

**3. Saving Charts**
- All charts can be saved to the `outputs/` directory as high-resolution PNG files
- Useful for reports, presentations, and sharing

```python
from src.visuals import save_figure, create_and_save_all_visuals

# Save a single chart
save_figure(fig, 'my_chart.png')

# Or generate and save all standard visualizations at once
saved_files = create_and_save_all_visuals(bonds, geo_bonds)
```

### Run the Demo Notebook

```bash
jupyter notebook notebooks/green_bond_demo.ipynb
```

The demo notebook includes:
- Data loading and validation
- Summary statistics
- Use of proceeds analysis
- Project type visualizations using the `visuals.py` module
- Geographic choropleth maps
- Time series analysis
- Certification standard analysis
- Automated generation of all visualizations

## Data Validation

The toolkit includes comprehensive data validation:

```bash
# Validate your data
python -m src.cli validate data/green_bonds.csv

# Get detailed validation report
python -m src.cli validate data/green_bonds.csv --output report.csv --verbose
```

Validation checks include:
- ✅ Required field completeness
- ✅ ISO 3166-1 alpha-3 country codes
- ✅ Numeric ranges and bounds
- ✅ Date format and consistency
- ✅ Duplicate detection
- ✅ Data type verification

See [`docs/data/schema.md`](docs/data/schema.md) for complete schema documentation.

## Portfolio Analytics

The toolkit includes a comprehensive **analytics module** for portfolio-style metrics and insights:

```bash
# Generate portfolio summary with metrics and diagnostics
python -m src.cli summary data/green_bonds.csv

# Specify custom output directory
python -m src.cli summary data/green_bonds.csv --output-dir reports/

# Get JSON output
python -m src.cli summary data/green_bonds.csv --json
```

**What you get:**

- **Console Output:** Human-readable summary table with:
  - Headline totals (bonds, issuance, issuers, countries, year range)
  - Data quality metrics (% missing values per field)
  - Concentration metrics (top 5 countries share, HHI index)
  - Top categories (top country, year, project type)

- **CSV Exports:**
  - `outputs/portfolio_summary.csv` - Key metrics for reports
  - `outputs/data_coverage_report.csv` - Field-level data quality

**Key Metrics:**

- `issuance_overview()` - Total bonds, amounts, year range, unique issuers, data quality
- `aggregation_by_country()` - Bond counts and totals by country with market share
- `aggregation_by_year()` - Year-over-year growth analysis
- `aggregation_by_category()` - Generic aggregation for any dimension (project type, certification, etc.)
- `top_n_concentration()` - Top-N concentration analysis
- `concentration_index()` - Herfindahl-Hirschman Index for market concentration
- `data_coverage_report()` - Field-level completeness diagnostics

**Python API:**

```python
from src.data_loader import load_green_bonds
from src.analytics.metrics import (
    issuance_overview,
    aggregation_by_country,
    portfolio_summary_table,
)

df = load_green_bonds("data/green_bonds.csv")

# Get overview
overview = issuance_overview(df)
print(f"Total bonds: {overview['total_bonds']}")
print(f"Year range: {overview['year_range']}")

# Analyze by country
countries = aggregation_by_country(df)
print(countries.head())

# Generate export-ready summary
summary = portfolio_summary_table(df)
summary.to_csv("my_summary.csv", index=False)
```

See [`docs/analytics/portfolio_metrics.md`](docs/analytics/portfolio_metrics.md) for detailed metric definitions, interpretations, and limitations.

## Project Structure

```
green-bond-tracker-project/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD
├── data/                       # Sample data files
│   ├── green_bonds.csv         # Green bond data with field descriptions
│   └── countries_geo.json      # Country geometries with ISO codes
├── src/                        # Python source code
│   ├── __init__.py
│   ├── analytics/              # Portfolio analytics module
│   │   ├── __init__.py
│   │   └── metrics.py          # Portfolio metrics and diagnostics
│   ├── data_loader.py          # Data loading and basic validation
│   ├── schema.py               # Schema definitions (single source of truth)
│   ├── validation.py           # Enhanced validation with row-level flags
│   ├── visuals.py              # Static visualization functions
│   ├── interactive.py          # Interactive maps with Folium
│   ├── cli.py                  # Command-line interface
│   └── arcgis_publisher.py     # ArcGIS integration (stub)
├── notebooks/                  # Jupyter notebooks
│   └── green_bond_demo.ipynb   # Demo with visualizations
├── docs/                       # Documentation
│   ├── README.md
│   ├── CONTRIBUTING.md         # Contributing guidelines
│   ├── ROADMAP.md              # Project roadmap
│   ├── analytics/
│   │   └── portfolio_metrics.md # Portfolio metrics documentation
│   ├── data/
│   │   └── schema.md           # Data schema documentation
│   └── arcgis/
│       └── arcgis_integration_plan.md  # ArcGIS integration plan
├── tests/                      # Unit tests
│   ├── fixtures/               # Test data
│   ├── test_data_loader.py
│   ├── test_schema.py
│   ├── test_validation.py
│   └── test_visuals.py
├── outputs/                    # Generated charts and visualizations
├── maps/                       # Placeholder for map outputs
├── pyproject.toml              # Project configuration and dependencies
├── .editorconfig               # Editor configuration
├── .pre-commit-config.yaml     # Pre-commit hooks
└── requirements.txt            # Python dependencies (runtime)
```

## Data Schema

Complete schema documentation is available in [`docs/data/schema.md`](docs/data/schema.md).

### Green Bonds CSV (Required Fields)
- `bond_id`: Unique bond identifier (string, required)
- `issuer`: Bond issuer name (string, required)
- `country_code`: ISO 3166-1 alpha-3 country code (3-letter, required)
- `amount_usd_millions`: Bond amount in USD millions (float >= 0, required)

### Green Bonds CSV (Optional Fields)
- `issue_date`, `maturity_date`: Bond dates (ISO 8601 format: YYYY-MM-DD)
- `currency`: Original currency (ISO 4217 code)
- `coupon_rate`: Annual coupon rate in % (0-100)
- `use_of_proceeds`: Green project category
- `certification`: Certification standard

### Country Geometries GeoJSON
- `name`: Country name
- `iso_a3`: ISO 3166-1 alpha-3 code
- `iso_a2`: ISO 3166-1 alpha-2 code
- `continent`: Continent name
- `geometry`: GeoJSON polygon coordinates

## Documentation

Detailed documentation is available in the [`docs/`](docs/) directory:

- 📖 **[Data Schema](docs/data/schema.md)**: Complete field definitions and validation rules
- 🤝 **[Contributing](docs/CONTRIBUTING.md)**: Guidelines for contributors
- 🗺️ **[Roadmap](docs/ROADMAP.md)**: Project roadmap and future plans
- 🌐 **[ArcGIS Integration Plan](docs/arcgis/arcgis_integration_plan.md)**: Planned GIS publishing features

## Requirements

### Core Dependencies

- Python 3.10+ (tested on 3.10, 3.11, 3.12)
- pandas >= 2.0.0
- geopandas >= 0.14.0
- matplotlib >= 3.7.0
- typer >= 0.9.0 (for CLI)
- rich >= 13.0.0 (for CLI output)

### Optional Dependencies

```bash
# For interactive maps
pip install -e ".[interactive]"  # Adds folium

# For Jupyter notebooks
pip install -e ".[notebook]"     # Adds jupyter, notebook

# For development
pip install -e ".[dev]"          # Adds pytest, ruff, pre-commit

# Install everything
pip install -e ".[all]"
```

See [`pyproject.toml`](pyproject.toml) for dependency management.

## Testing

```bash
# Using Makefile (recommended)
make test        # Run tests with coverage
make lint        # Run linter checks
make format      # Format code

# Or manually
pytest tests/                                    # Run tests
pytest tests/ --cov=src --cov-report=term-missing  # With coverage
ruff check src/ tests/                           # Lint
ruff format src/ tests/                          # Format
pre-commit run --all-files                       # Run pre-commit hooks
```

## CLI Reference

### Global Flags

These flags work with any command:

```bash
--verbose    Enable DEBUG logging (detailed execution steps)
--quiet      Suppress INFO logs (show WARN/ERROR only)
--config     Path to custom configuration YAML file
--version    Show version and exit
--help       Show help message
```

### Commands

```bash
# Show version
gbt --version

# Validate data
gbt [--verbose|--quiet] validate --input <path> [--output report.csv] [--verbose]

# Show statistics
gbt [--verbose|--quiet] summary [--input <path>] [--output-dir <dir>] [--json]

# Generate interactive map
gbt [--verbose|--quiet] map --input <path> --output <file.html>

# Generate visualizations
gbt [--verbose|--quiet] viz [--input <path>] [--output-dir <dir>] [--interactive]

# Show version (alternative)
gbt version
```

### Examples

```bash
# Show version
gbt --version

# Validate with detailed debug logging
gbt --verbose validate --input data/green_bonds.csv

# Validate in quiet mode (errors/warnings only)
gbt --quiet validate --input data/green_bonds.csv

# Validate with detailed report
gbt validate --input data/green_bonds.csv --output validation_report.csv -v

# Get summary as JSON with debug logging
gbt --verbose summary --input data/green_bonds.csv --json

# Generate interactive map
gbt map --input data/green_bonds.csv --output outputs/map.html

# Generate all static visualizations with verbose logging
gbt --verbose viz --input data/green_bonds.csv --output-dir outputs/
```

### Legacy Commands (still supported)

For backward compatibility, you can also use:
```bash
# Legacy greenbond command (deprecated, use gbt instead)
greenbond validate --input <path>

# Python module invocation
python -m src.cli validate <csv_path> [--output report.csv] [--verbose]
python -m src.cli summary [csv_path] [--json]
python -m src.cli viz [csv_path] [--output-dir DIR] [--interactive]
```

## Contributing

Contributions are welcome! This is an educational project aimed at helping people learn about green bonds and GIS data visualization.

Please see **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** for detailed guidelines on:
- Setting up development environment
- Code style and standards
- Testing requirements
- Pull request process

Quick start for contributors:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install dev dependencies (`pip install -e ".[dev]"`)
4. Make your changes and add tests
5. Run tests and linting (`pytest tests/ && ruff check src/ tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

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
