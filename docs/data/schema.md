# Green Bonds Data Schema

This document defines the expected structure and validation rules for the green bonds CSV data.

## Overview

The green bonds dataset tracks sustainability-linked financial instruments with geographic and temporal data. All data is for **educational purposes only** and should not be used for investment decisions.

## File Format

- **Format**: CSV (Comma-Separated Values)
- **Encoding**: UTF-8
- **Header Row**: Required (first non-comment line)
- **Comments**: Lines starting with `#` are treated as comments

## Schema Definition

### Required Fields

| Column Name | Type | Description | Constraints | Example |
|-------------|------|-------------|-------------|---------|
| `bond_id` | String | Unique identifier for each bond | Required, Unique, Non-empty | `GB001` |
| `issuer` | String | Name of the organization issuing the bond | Required, Non-empty | `European Investment Bank` |
| `country_code` | String | ISO 3166-1 alpha-3 country code | Required, Exactly 3 uppercase letters | `USA`, `CHN`, `DEU` |
| `amount_usd_millions` | Float | Bond amount in millions of USD | Required, >= 0 | `500.0` |

### Optional Fields

| Column Name | Type | Description | Constraints | Example |
|-------------|------|-------------|-------------|---------|
| `issue_date` | Date | Date when the bond was issued | ISO 8601 format (YYYY-MM-DD) | `2023-01-15` |
| `maturity_date` | Date | Date when the bond matures | ISO 8601 format (YYYY-MM-DD), >= issue_date | `2033-01-15` |
| `currency` | String | Original currency denomination | 3-letter ISO 4217 code | `EUR`, `USD`, `CNY` |
| `coupon_rate` | Float | Annual coupon rate as a percentage | >= 0, <= 100 | `2.5` |
| `use_of_proceeds` | String | Category of green project funded | One of predefined categories | `Renewable Energy` |
| `certification` | String | Green bond certification standard | One of recognized standards | `Climate Bonds Initiative` |

## Field Details

### bond_id

**Purpose**: Unique identifier for each bond in the dataset.

**Validation Rules**:
- Must be unique across the entire dataset
- Cannot be null or empty
- Recommended format: Alphanumeric string (e.g., `GB001`, `BOND_2023_001`)

### issuer

**Purpose**: The organization or entity issuing the green bond.

**Validation Rules**:
- Cannot be null or empty
- Should be the full legal name or commonly recognized name

**Examples**: `World Bank`, `European Investment Bank`, `Bank of China`

### country_code

**Purpose**: The country of the issuer, using standardized ISO codes.

**Validation Rules**:
- Must be exactly 3 characters
- Must be a valid ISO 3166-1 alpha-3 code
- Must be uppercase
- Cannot be null

**Common Valid Codes**:
- `USA` - United States
- `CHN` - China
- `DEU` - Germany
- `GBR` - United Kingdom
- `FRA` - France
- `JPN` - Japan
- `BRA` - Brazil
- `IND` - India

**Reference**: [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)

### amount_usd_millions

**Purpose**: The principal amount of the bond in millions of USD.

**Validation Rules**:
- Must be a positive number (>= 0)
- Cannot be null
- Precision: Up to 2 decimal places recommended

**Examples**: `500.0`, `1000.5`, `750.25`

### issue_date

**Purpose**: The date the bond was issued to the market.

**Validation Rules**:
- Format: ISO 8601 date (YYYY-MM-DD)
- Must be a valid calendar date
- Should be <= current date (no future dates for issued bonds)
- Should be <= maturity_date if both are present

**Example**: `2023-01-15`

### maturity_date

**Purpose**: The date when the bond reaches maturity and principal is repaid.

**Validation Rules**:
- Format: ISO 8601 date (YYYY-MM-DD)
- Must be a valid calendar date
- Should be >= issue_date if both are present
- Typically 5-30 years from issue date for green bonds

**Example**: `2033-01-15`

### currency

**Purpose**: The original currency in which the bond was denominated.

**Validation Rules**:
- Should be a 3-letter ISO 4217 currency code
- Uppercase recommended

**Common Currencies**:
- `USD` - US Dollar
- `EUR` - Euro
- `CNY` - Chinese Yuan
- `GBP` - British Pound
- `JPY` - Japanese Yen

### coupon_rate

**Purpose**: The annual interest rate paid to bondholders as a percentage.

**Validation Rules**:
- Must be >= 0
- Must be <= 100 (percentage)
- Precision: Up to 2 decimal places typical

**Examples**: `2.5`, `3.0`, `4.25`

### use_of_proceeds

**Purpose**: The category of green/sustainable project funded by the bond.

**Validation Rules**:
- Should be one of the recognized green project categories
- Free text if category doesn't match predefined list

**Recognized Categories**:
- `Renewable Energy` - Solar, wind, hydro, geothermal
- `Energy Efficiency` - Building retrofits, efficient equipment
- `Clean Transportation` - Electric vehicles, public transit
- `Sustainable Water Management` - Water treatment, conservation
- `Pollution Prevention and Control` - Waste management, recycling
- `Sustainable Agriculture` - Organic farming, conservation
- `Green Buildings` - LEED certified, sustainable construction
- `Climate Adaptation` - Resilience, flood protection
- `Biodiversity Conservation` - Habitat protection, restoration

### certification

**Purpose**: The green bond framework or certification standard used.

**Validation Rules**:
- Should be one of the recognized certification standards
- Free text if standard doesn't match predefined list

**Recognized Standards**:
- `Green Bond Principles` - ICMA voluntary guidelines
- `Climate Bonds Initiative` - Climate Bonds Standard
- `EU Green Bond Standard` - European Union framework
- `ASEAN Green Bond Standards` - ASEAN Capital Markets Forum
- `China Green Bond Guidelines` - PBoC/NDRC guidelines

## Validation Rules Summary

### Critical Validations (Must Pass)

1. **No null values** in required fields: `bond_id`, `issuer`, `country_code`, `amount_usd_millions`
2. **Unique bond_id** across all records
3. **Valid country codes**: Exactly 3 characters, uppercase
4. **Non-negative amounts**: `amount_usd_millions` >= 0
5. **Valid date formats**: ISO 8601 (YYYY-MM-DD) for date fields

### Warning-Level Validations (Should Pass)

1. **Date consistency**: `issue_date` <= `maturity_date`
2. **Reasonable coupon rates**: 0 <= `coupon_rate` <= 100
3. **Valid ISO currency codes**: 3-letter codes for `currency`
4. **Recognized categories**: `use_of_proceeds` matches known green categories
5. **Issue dates not in future**: `issue_date` <= current date

## Data Quality Guidelines

1. **Completeness**: Aim for >90% completeness on optional fields
2. **Consistency**: Use standardized terminology across records
3. **Accuracy**: Verify ISO codes and dates before import
4. **Timeliness**: Update dataset regularly with new bond issuances

## Example Record

```csv
bond_id,issuer,country_code,issue_date,maturity_date,amount_usd_millions,currency,coupon_rate,use_of_proceeds,certification
GB001,European Investment Bank,LUX,2023-01-15,2033-01-15,500.0,EUR,2.5,Renewable Energy,Climate Bonds Initiative
```

## Versioning

- **Schema Version**: 1.0
- **Last Updated**: 2024-12-30
- **Maintained by**: Green Bond Tracker Project

## References

- [ISO 3166-1 Country Codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3)
- [ISO 4217 Currency Codes](https://en.wikipedia.org/wiki/ISO_4217)
- [ISO 8601 Date Format](https://en.wikipedia.org/wiki/ISO_8601)
- [Green Bond Principles](https://www.icmagroup.org/sustainable-finance/the-principles-guidelines-and-handbooks/green-bond-principles-gbp/)
- [Climate Bonds Standard](https://www.climatebonds.net/standard)
