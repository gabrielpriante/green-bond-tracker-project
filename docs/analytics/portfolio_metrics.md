# Portfolio Metrics Documentation

> **⚠️ EDUCATIONAL USE ONLY**
> This document explains portfolio analytics metrics for learning purposes.
> **NOT intended for investment advice or financial decision-making.**

## Overview

The Green Bond Tracker includes a comprehensive analytics module that provides portfolio-style metrics and diagnostics. These tools help understand the composition, concentration, and quality of green bond datasets in an educational context.

All metrics are designed to be **transparent, interpretable, and educational** rather than production-ready investment tools.

## Core Metrics

### 1. Issuance Overview

**Function:** `issuance_overview(df)`

**What it does:**
Provides high-level summary statistics about the bond portfolio.

**Returns:**
- `total_bonds`: Count of bonds in the dataset
- `total_issuance_usd_millions`: Sum of all bond amounts (if available)
- `year_range`: Tuple of (earliest_year, latest_year) from issue dates
- `unique_issuers`: Count of distinct issuers
- `pct_missing_country`: Percentage of records with missing country codes
- `pct_missing_year`: Percentage of records with missing issue dates
- `pct_missing_amount`: Percentage of records with missing amounts

**Plain English:**
This tells you the basic size and scope of your dataset: how many bonds, how much money, what time period, and how many different issuers are represented.

**Limitations:**
- Totals assume all amounts are in USD millions (currency conversion not handled)
- Missing data percentages flag data quality issues but don't indicate *why* data is missing
- Does not account for bond maturity or current status

### 2. Aggregation by Country

**Function:** `aggregation_by_country(df)`

**What it does:**
Groups bonds by country and calculates totals and shares.

**Returns DataFrame with:**
- `country_code`: ISO 3166-1 alpha-3 country code
- `bond_count`: Number of bonds from this country
- `total_issuance_usd_millions`: Sum of bond amounts
- `share_of_total_pct`: This country's percentage of global total

**Plain English:**
Shows which countries are issuing the most green bonds in your dataset, both by count and by dollar amount.

**Limitations:**
- Country assignment based on issuer location (may not reflect where projects are located)
- Does not account for supranational issuers (e.g., World Bank)
- Currency conversion assumes all amounts already in USD
- Sorted by issuance amount, which may differ from environmental impact

### 3. Aggregation by Year

**Function:** `aggregation_by_year(df)`

**What it does:**
Groups bonds by issue year and shows year-over-year growth.

**Returns DataFrame with:**
- `year`: Issue year
- `bond_count`: Number of bonds issued that year
- `issuance_amount_usd_millions`: Total issuance that year
- `yoy_growth_pct`: Year-over-year growth rate (%)

**Plain English:**
Shows how the green bond market has grown (or shrunk) over time in your dataset.

**Limitations:**
- YoY growth is calculated as simple percentage change (doesn't account for market conditions)
- Missing years in the dataset will break continuity
- First year always has NaN growth (no previous year to compare)
- Does not adjust for inflation or market size

### 4. Aggregation by Category

**Function:** `aggregation_by_category(df, column_name)`

**What it does:**
Generic aggregation for any categorical column (e.g., project type, certification, currency).

**Returns DataFrame with:**
- `{column_name}`: Category value
- `bond_count`: Number of bonds in this category
- `total_issuance_usd_millions`: Total amount
- `share_of_total_pct`: Percentage of total

**Plain English:**
Flexible tool to break down your portfolio by any dimension: what types of projects are funded, which certification standards are used, etc.

**Limitations:**
- Excludes null/missing values from aggregation
- Categories must be exact text matches (no fuzzy matching)
- Share percentages only reflect bonds with non-null category values

## Concentration & Diversification Metrics

### 5. Top-N Concentration

**Function:** `top_n_concentration(df, column_name='country_code', n=5)`

**What it does:**
Calculates what percentage of total issuance comes from the top N entities in a category.

**Returns dict with:**
- `n`: Number of top entries analyzed
- `top_n_entries`: List of the top N entity names
- `top_n_share_pct`: Their combined share of total (%)

**Plain English:**
Answers questions like "Do the top 5 countries account for 80% of all issuance?" High concentration may indicate market dominance or reporting bias.

**Limitations:**
- High concentration isn't inherently good or bad (depends on context)
- Does not indicate whether concentration is increasing or decreasing
- May be influenced by incomplete data from smaller issuers

### 6. Herfindahl-Hirschman Index (HHI)

**Function:** `concentration_index(df, column_name='country_code')`

**What it does:**
Calculates the Herfindahl-Hirschman Index, a standard measure of market concentration.

**Returns:**
Single float value (0-10,000)

**Interpretation:**
- **0-1,500**: Low concentration (competitive/diverse market)
- **1,500-2,500**: Moderate concentration
- **2,500+**: High concentration (dominated by few entities)

**Formula:**
HHI = sum of squared market shares (as percentages)

**Plain English:**
A single number that tells you how concentrated or diversified your portfolio is. Lower = more diversified, higher = more concentrated.

**Limitations:**
- Standard HHI is designed for market analysis, not environmental impact
- Doesn't tell you *which* entities are dominant (just that they exist)
- Sensitive to how you define categories (country vs. issuer type vs. project type)
- Interpretation thresholds (1500, 2500) are from antitrust economics, may not apply to green bonds

## Data Quality Metrics

### 7. Data Coverage Report

**Function:** `data_coverage_report(df)`

**What it does:**
Analyzes each column to show how complete the data is.

**Returns DataFrame with:**
- `column_name`: Field name
- `non_null_count`: Number of non-null values
- `pct_non_null`: Percentage of non-null values
- `coverage_note`: Warning if below 80% threshold

**Plain English:**
Shows which fields have good data and which have lots of missing values. Helps identify data quality issues and reporting gaps.

**Limitations:**
- 80% threshold is arbitrary (not based on statistical significance)
- Non-null doesn't mean *correct* (a field can be filled with wrong data)
- Doesn't explain *why* data is missing (reporting requirements vary by region/time)
- Low coverage may reflect genuine unavailability rather than poor data collection

## Portfolio Summary Table

### 8. Portfolio Summary Table

**Function:** `portfolio_summary_table(df)`

**What it does:**
Combines headline metrics, concentration measures, and top categories into a single export-ready table.

**Includes:**
- Total bonds, issuance, issuers
- Year range
- Data quality percentages (missing fields)
- Top 5 countries share
- Country concentration (HHI)
- Top country, year, and project type

**Plain English:**
A "dashboard" table that gives you the essential portfolio facts at a glance. Designed to be saved as CSV for reports.

**Limitations:**
- Combines multiple metrics that may have different data coverage
- "Top" categories depend on your dataset's completeness
- Snapshot in time (doesn't show trends)

## Known Limitations & Warnings

### Reporting Bias

Green bond data is **self-reported** and subject to:
- Voluntary disclosure (smaller issuers may not report)
- Geographic reporting bias (better data from developed markets)
- Certification bias (certified bonds easier to track than uncertified)

**Implication:** Your dataset may over-represent large, certified, developed-market bonds.

### Currency Issues

All metrics assume amounts are in **USD millions**. If your source data mixes currencies:
- Convert all to USD before analysis
- Document exchange rates and conversion date
- Note that currency fluctuations affect historical comparisons

### Coverage Gaps

Missing optional fields (e.g., project type, certification) are common:
- Aggregations exclude null values
- Percentages and shares calculated only on available data
- Low coverage fields may not be representative

### No Investment Advice

These metrics are **educational tools**, not investment analysis:
- Do not indicate bond quality, creditworthiness, or environmental impact
- Do not account for financial risk, default probability, or returns
- Do not validate green credentials or environmental outcomes

**Always consult qualified professionals before making investment decisions.**

## Example Interpretation

Let's say you run analytics on a dataset and get:

- **Total bonds:** 1,000
- **Total issuance:** $500,000 million
- **Top 5 countries share:** 75%
- **HHI (country):** 2,200
- **Missing project type:** 40%

**What this tells you:**

- You have a substantial dataset (1,000 bonds, $500B)
- The market is **moderately concentrated** (HHI = 2,200)
- **Three-quarters of issuance** comes from just 5 countries (high geographic concentration)
- **40% of bonds lack project type data** (reporting gaps may bias project-level analysis)

**What it does NOT tell you:**

- Whether these bonds are actually "green" (would need verification)
- Whether issuers are meeting commitments (would need impact reports)
- Whether this represents global reality (may be sample bias)
- Whether to invest in any specific bond

## Usage Recommendations

1. **Always check data coverage first**
   Run `data_coverage_report()` before other metrics to understand data quality.

2. **Interpret concentration in context**
   High concentration may reflect market reality OR reporting bias.

3. **Document assumptions**
   Note currency, date range, source, and any data cleaning done.

4. **Combine multiple views**
   Look at country, year, AND project type to get full picture.

5. **State limitations**
   When sharing results, always note data gaps and interpretation limits.

## CLI Usage

```bash
# Generate full portfolio summary with CSV exports
python -m src.cli summary data/green_bonds.csv

# Specify output directory
python -m src.cli summary data/green_bonds.csv --output-dir reports/

# Get JSON output instead of tables
python -m src.cli summary data/green_bonds.csv --json
```

**Output files:**
- `outputs/portfolio_summary.csv` - Key metrics table
- `outputs/data_coverage_report.csv` - Field-level coverage

## Python API Usage

```python
from src.data_loader import load_green_bonds
from src.analytics.metrics import (
    issuance_overview,
    aggregation_by_country,
    concentration_index,
    data_coverage_report,
    portfolio_summary_table,
)

# Load data
df = load_green_bonds("data/green_bonds.csv")

# Get overview
overview = issuance_overview(df)
print(f"Total bonds: {overview['total_bonds']}")
print(f"Total issuance: ${overview['total_issuance_usd_millions']:.2f}M")

# Check concentration
hhi = concentration_index(df, "country_code")
print(f"Country concentration (HHI): {hhi:.2f}")

# Analyze by project type
if "use_of_proceeds" in df.columns:
    projects = aggregation_by_category(df, "use_of_proceeds")
    print(projects.head())

# Generate export-ready summary
summary = portfolio_summary_table(df)
summary.to_csv("my_portfolio_summary.csv", index=False)

# Check data quality
coverage = data_coverage_report(df)
print(coverage)
```

## Further Reading

- **Data Schema:** See `docs/data/schema.md` for field definitions
- **Validation:** See `src/validation.py` for data quality checks
- **Green Bond Standards:** [Climate Bonds Initiative](https://www.climatebonds.net/), [ICMA Green Bond Principles](https://www.icmagroup.org/sustainable-finance/the-principles-guidelines-and-handbooks/green-bond-principles-gbp/)

---

**Remember:** This is a learning toolkit for educational purposes. Always verify data, understand limitations, and consult professionals for financial decisions. 📚🌱
