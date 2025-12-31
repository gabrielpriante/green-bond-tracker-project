"""
Green Bond Tracker - Portfolio Metrics Module

This module provides portfolio-style analytics functions for green bond data.
All functions consume validated, canonical DataFrames and return DataFrames or dicts.
No file I/O is performed in core functions.

Note: This is an educational project and should not be used for investment advice.
"""

import pandas as pd


def issuance_overview(df: pd.DataFrame) -> dict:
    """
    Calculate high-level issuance overview statistics.
    
    Parameters
    ----------
    df : pd.DataFrame
        Validated green bond dataframe with canonical schema
        
    Returns
    -------
    dict
        Dictionary containing:
        - total_bonds: Total number of bonds
        - total_issuance_usd_millions: Total issuance amount (if amount column exists)
        - year_range: Tuple of (earliest_year, latest_year) if dates available
        - unique_issuers: Count of unique issuers (if available)
        - pct_missing_country: Percentage of missing country values
        - pct_missing_year: Percentage of missing year/date values
        - pct_missing_amount: Percentage of missing amount values
        
    Notes
    -----
    Percentages are calculated as (null_count / total_rows) * 100.
    Missing optional columns are handled gracefully.
    """
    total_bonds = len(df)
    overview = {"total_bonds": total_bonds}
    
    # Total issuance amount
    if "amount_usd_millions" in df.columns:
        total_issuance = df["amount_usd_millions"].sum()
        overview["total_issuance_usd_millions"] = total_issuance
        pct_missing_amount = (df["amount_usd_millions"].isnull().sum() / total_bonds) * 100
        overview["pct_missing_amount"] = round(pct_missing_amount, 2)
    else:
        overview["total_issuance_usd_millions"] = None
        overview["pct_missing_amount"] = None
    
    # Year range from issue_date
    if "issue_date" in df.columns:
        df_with_dates = df.dropna(subset=["issue_date"])
        if len(df_with_dates) > 0:
            earliest = df_with_dates["issue_date"].min()
            latest = df_with_dates["issue_date"].max()
            overview["year_range"] = (earliest.year, latest.year)
        else:
            overview["year_range"] = None
        pct_missing_year = (df["issue_date"].isnull().sum() / total_bonds) * 100
        overview["pct_missing_year"] = round(pct_missing_year, 2)
    else:
        overview["year_range"] = None
        overview["pct_missing_year"] = None
    
    # Unique issuers
    if "issuer" in df.columns:
        overview["unique_issuers"] = df["issuer"].nunique()
    else:
        overview["unique_issuers"] = None
    
    # Missing country
    if "country_code" in df.columns:
        pct_missing_country = (df["country_code"].isnull().sum() / total_bonds) * 100
        overview["pct_missing_country"] = round(pct_missing_country, 2)
    else:
        overview["pct_missing_country"] = None
    
    return overview


def aggregation_by_country(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate bond data by country.
    
    Parameters
    ----------
    df : pd.DataFrame
        Validated green bond dataframe
        
    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - country_code: Country ISO code
        - bond_count: Number of bonds
        - total_issuance_usd_millions: Total issuance amount
        - share_of_total_pct: Share of global total issuance (%)
        Sorted by total_issuance descending
        
    Notes
    -----
    If amount_usd_millions column is missing, totals will be NaN.
    Share is calculated only when amounts are available.
    """
    if "country_code" not in df.columns:
        return pd.DataFrame(columns=["country_code", "bond_count", "total_issuance_usd_millions", "share_of_total_pct"])
    
    # Group by country
    agg_dict = {"bond_id": "count"}
    if "amount_usd_millions" in df.columns:
        agg_dict["amount_usd_millions"] = "sum"
    
    grouped = df.groupby("country_code").agg(agg_dict).reset_index()
    
    # Rename columns
    grouped.columns = ["country_code", "bond_count"]
    if "amount_usd_millions" in df.columns:
        grouped.columns = ["country_code", "bond_count", "total_issuance_usd_millions"]
        
        # Calculate share of total
        global_total = grouped["total_issuance_usd_millions"].sum()
        if global_total > 0:
            grouped["share_of_total_pct"] = (grouped["total_issuance_usd_millions"] / global_total) * 100
        else:
            grouped["share_of_total_pct"] = 0.0
        
        # Round percentages
        grouped["share_of_total_pct"] = grouped["share_of_total_pct"].round(2)
        
        # Sort by total issuance descending
        grouped = grouped.sort_values("total_issuance_usd_millions", ascending=False)
    else:
        grouped["total_issuance_usd_millions"] = pd.NA
        grouped["share_of_total_pct"] = pd.NA
        # Sort by count descending
        grouped = grouped.sort_values("bond_count", ascending=False)
    
    return grouped.reset_index(drop=True)


def aggregation_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate bond data by year with YoY growth rates.
    
    Parameters
    ----------
    df : pd.DataFrame
        Validated green bond dataframe
        
    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - year: Issue year
        - bond_count: Number of bonds issued
        - issuance_amount_usd_millions: Total issuance amount
        - yoy_growth_pct: Year-over-year growth rate (%)
        Sorted by year ascending
        
    Notes
    -----
    YoY growth is calculated as ((current - previous) / previous) * 100.
    First year and missing years will have NaN for yoy_growth_pct.
    Requires issue_date column.
    """
    if "issue_date" not in df.columns:
        return pd.DataFrame(columns=["year", "bond_count", "issuance_amount_usd_millions", "yoy_growth_pct"])
    
    # Extract year from issue_date
    df_with_year = df.dropna(subset=["issue_date"]).copy()
    df_with_year["year"] = df_with_year["issue_date"].dt.year
    
    # Group by year
    agg_dict = {"bond_id": "count"}
    if "amount_usd_millions" in df.columns:
        agg_dict["amount_usd_millions"] = "sum"
    
    grouped = df_with_year.groupby("year").agg(agg_dict).reset_index()
    
    # Rename columns
    grouped.columns = ["year", "bond_count"]
    if "amount_usd_millions" in df.columns:
        grouped.columns = ["year", "bond_count", "issuance_amount_usd_millions"]
    else:
        grouped["issuance_amount_usd_millions"] = pd.NA
    
    # Sort by year
    grouped = grouped.sort_values("year")
    
    # Calculate YoY growth
    if "issuance_amount_usd_millions" in grouped.columns and grouped["issuance_amount_usd_millions"].notna().any():
        grouped["yoy_growth_pct"] = grouped["issuance_amount_usd_millions"].pct_change() * 100
        grouped["yoy_growth_pct"] = grouped["yoy_growth_pct"].round(2)
    else:
        grouped["yoy_growth_pct"] = pd.NA
    
    return grouped.reset_index(drop=True)


def aggregation_by_category(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Generic aggregation helper for any categorical column.
    
    Parameters
    ----------
    df : pd.DataFrame
        Validated green bond dataframe
    column_name : str
        Name of the column to aggregate by (e.g., 'use_of_proceeds', 'certification', 'currency')
        
    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - {column_name}: Category value
        - bond_count: Number of bonds
        - total_issuance_usd_millions: Total issuance amount
        - share_of_total_pct: Share of global total (%)
        Sorted by total_issuance descending
        
    Notes
    -----
    Returns empty DataFrame if column doesn't exist.
    Handles missing values by excluding them from aggregation.
    """
    if column_name not in df.columns:
        return pd.DataFrame(columns=[column_name, "bond_count", "total_issuance_usd_millions", "share_of_total_pct"])
    
    # Filter out null values for the category
    df_valid = df.dropna(subset=[column_name])
    
    if len(df_valid) == 0:
        return pd.DataFrame(columns=[column_name, "bond_count", "total_issuance_usd_millions", "share_of_total_pct"])
    
    # Group by category
    agg_dict = {"bond_id": "count"}
    if "amount_usd_millions" in df.columns:
        agg_dict["amount_usd_millions"] = "sum"
    
    grouped = df_valid.groupby(column_name).agg(agg_dict).reset_index()
    
    # Rename columns
    grouped.columns = [column_name, "bond_count"]
    if "amount_usd_millions" in df.columns:
        grouped.columns = [column_name, "bond_count", "total_issuance_usd_millions"]
        
        # Calculate share of total
        global_total = grouped["total_issuance_usd_millions"].sum()
        if global_total > 0:
            grouped["share_of_total_pct"] = (grouped["total_issuance_usd_millions"] / global_total) * 100
        else:
            grouped["share_of_total_pct"] = 0.0
        
        # Round percentages
        grouped["share_of_total_pct"] = grouped["share_of_total_pct"].round(2)
        
        # Sort by total issuance descending
        grouped = grouped.sort_values("total_issuance_usd_millions", ascending=False)
    else:
        grouped["total_issuance_usd_millions"] = pd.NA
        grouped["share_of_total_pct"] = pd.NA
        # Sort by count descending
        grouped = grouped.sort_values("bond_count", ascending=False)
    
    return grouped.reset_index(drop=True)


def top_n_concentration(df: pd.DataFrame, column_name: str = "country_code", n: int = 5) -> dict:
    """
    Calculate top-N concentration metric.
    
    Parameters
    ----------
    df : pd.DataFrame
        Validated green bond dataframe
    column_name : str
        Column to calculate concentration for (default: 'country_code')
    n : int
        Number of top entries to include (default: 5)
        
    Returns
    -------
    dict
        Dictionary containing:
        - top_n_share_pct: Share of total issuance by top N entries
        - top_n_entries: List of top N entry names
        - n: Value of N used
        
    Notes
    -----
    Concentration shows how much of total issuance comes from top N entities.
    Useful for understanding market concentration and diversification.
    Returns 0.0 if amount column is missing or no data available.
    """
    result = {"n": n, "top_n_entries": [], "top_n_share_pct": 0.0}
    
    if column_name not in df.columns or "amount_usd_millions" not in df.columns:
        return result
    
    # Aggregate by column
    agg = aggregation_by_category(df, column_name)
    
    if len(agg) == 0:
        return result
    
    # Get top N
    top_n = agg.head(n)
    result["top_n_entries"] = top_n[column_name].tolist()
    result["top_n_share_pct"] = round(top_n["share_of_total_pct"].sum(), 2)
    
    return result


def concentration_index(df: pd.DataFrame, column_name: str = "country_code") -> float:
    """
    Calculate Herfindahl-Hirschman Index (HHI) for concentration.
    
    Parameters
    ----------
    df : pd.DataFrame
        Validated green bond dataframe
    column_name : str
        Column to calculate HHI for (default: 'country_code')
        
    Returns
    -------
    float
        HHI value (0-10000). Higher values indicate higher concentration.
        - 0-1500: Low concentration (competitive)
        - 1500-2500: Moderate concentration
        - 2500+: High concentration
        
    Notes
    -----
    HHI = sum of squared market shares (as percentages).
    Standard interpretation:
    - HHI < 1500: competitive market
    - 1500 <= HHI < 2500: moderately concentrated
    - HHI >= 2500: highly concentrated
    
    Returns 0.0 if amount column is missing or insufficient data.
    """
    if column_name not in df.columns or "amount_usd_millions" not in df.columns:
        return 0.0
    
    # Aggregate by column
    agg = aggregation_by_category(df, column_name)
    
    if len(agg) == 0:
        return 0.0
    
    # Calculate HHI: sum of squared market shares
    hhi = (agg["share_of_total_pct"] ** 2).sum()
    
    return round(hhi, 2)


def data_coverage_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate field-level data coverage report.
    
    Parameters
    ----------
    df : pd.DataFrame
        Validated green bond dataframe
        
    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - column_name: Field name
        - non_null_count: Number of non-null values
        - pct_non_null: Percentage of non-null values
        - coverage_note: Note if below 80% threshold
        Sorted by pct_non_null descending
        
    Notes
    -----
    Coverage below 80% is flagged with a warning note.
    Helps identify data quality issues and reporting bias.
    """
    total_rows = len(df)
    
    if total_rows == 0:
        return pd.DataFrame(columns=["column_name", "non_null_count", "pct_non_null", "coverage_note"])
    
    coverage_data = []
    
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        pct_non_null = (non_null_count / total_rows) * 100
        
        # Add note if coverage is below 80%
        if pct_non_null < 80:
            note = "⚠ Low coverage (<80%)"
        else:
            note = "✓ Good coverage"
        
        coverage_data.append({
            "column_name": col,
            "non_null_count": non_null_count,
            "pct_non_null": round(pct_non_null, 2),
            "coverage_note": note
        })
    
    result = pd.DataFrame(coverage_data)
    result = result.sort_values("pct_non_null", ascending=False)
    
    return result.reset_index(drop=True)


def portfolio_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create export-ready portfolio summary table combining key metrics.
    
    Parameters
    ----------
    df : pd.DataFrame
        Validated green bond dataframe
        
    Returns
    -------
    pd.DataFrame
        Clean, presentation-ready DataFrame with:
        - Headline totals (bonds, issuance, issuers, countries)
        - Concentration metrics (top 5 share, HHI)
        - Top categories (top country, year, project type if present)
        
    Notes
    -----
    This is a consolidated view for quick portfolio assessment.
    Returns table with metric names and values for easy export to CSV/Excel.
    Handles missing optional columns gracefully.
    """
    overview = issuance_overview(df)
    
    # Build summary rows
    summary_data = []
    
    # Headline metrics
    summary_data.append({"metric": "Total Bonds", "value": str(overview["total_bonds"])})
    
    if overview["total_issuance_usd_millions"] is not None:
        summary_data.append({
            "metric": "Total Issuance (USD Millions)",
            "value": f"${overview['total_issuance_usd_millions']:,.2f}"
        })
    
    if overview["unique_issuers"] is not None:
        summary_data.append({"metric": "Unique Issuers", "value": str(overview["unique_issuers"])})
    
    if overview["year_range"] is not None:
        summary_data.append({
            "metric": "Year Range",
            "value": f"{overview['year_range'][0]}-{overview['year_range'][1]}"
        })
    
    # Data quality metrics
    if overview["pct_missing_country"] is not None:
        summary_data.append({
            "metric": "Missing Country (%)",
            "value": f"{overview['pct_missing_country']}%"
        })
    if overview["pct_missing_year"] is not None:
        summary_data.append({
            "metric": "Missing Year (%)",
            "value": f"{overview['pct_missing_year']}%"
        })
    if overview["pct_missing_amount"] is not None:
        summary_data.append({
            "metric": "Missing Amount (%)",
            "value": f"{overview['pct_missing_amount']}%"
        })
    
    # Concentration metrics
    top_5_country = top_n_concentration(df, "country_code", n=5)
    summary_data.append({
        "metric": "Top 5 Countries Share (%)",
        "value": f"{top_5_country['top_n_share_pct']}%"
    })
    
    hhi_country = concentration_index(df, "country_code")
    summary_data.append({
        "metric": "Country Concentration (HHI)",
        "value": f"{hhi_country:.2f}"
    })
    
    # Top categories
    if "country_code" in df.columns and "amount_usd_millions" in df.columns:
        country_agg = aggregation_by_country(df)
        if len(country_agg) > 0:
            top_country = country_agg.iloc[0]
            summary_data.append({
                "metric": "Top Country",
                "value": f"{top_country['country_code']} (${top_country['total_issuance_usd_millions']:,.2f}M)"
            })
    
    if "issue_date" in df.columns:
        year_agg = aggregation_by_year(df)
        if len(year_agg) > 0:
            # Find year with highest issuance
            if "issuance_amount_usd_millions" in year_agg.columns and year_agg["issuance_amount_usd_millions"].notna().any():
                top_year = year_agg.sort_values("issuance_amount_usd_millions", ascending=False).iloc[0]
                summary_data.append({
                    "metric": "Top Year",
                    "value": f"{int(top_year['year'])} (${top_year['issuance_amount_usd_millions']:,.2f}M)"
                })
    
    if "use_of_proceeds" in df.columns:
        proceeds_agg = aggregation_by_category(df, "use_of_proceeds")
        if len(proceeds_agg) > 0 and "total_issuance_usd_millions" in proceeds_agg.columns:
            top_proceeds = proceeds_agg.iloc[0]
            if pd.notna(top_proceeds["total_issuance_usd_millions"]):
                summary_data.append({
                    "metric": "Top Project Type",
                    "value": f"{top_proceeds['use_of_proceeds']} (${top_proceeds['total_issuance_usd_millions']:,.2f}M)"
                })
    
    return pd.DataFrame(summary_data)
