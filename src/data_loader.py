"""
Green Bond Tracker - Data Loading and Validation Module

This module provides functions to load and validate green bond data
and geographic information for educational and analytical purposes.

Note: This is an educational project and should not be used for investment advice.
"""

import warnings
from pathlib import Path

import geopandas as gpd
import pandas as pd

from src.config import Config, get_config


def load_green_bonds(filepath: str | Path | None = None, config: Config | None = None) -> pd.DataFrame:
    """
    Load green bond data from CSV file.

    Parameters:
    -----------
    filepath : str or Path, optional
        Path to the green bonds CSV file. Can be absolute or relative to repository root.
        If None, uses path from config (or default if config not provided).
    config : Config, optional
        Configuration object. If None and filepath is None, uses global config.

    Returns:
    --------
    pd.DataFrame
        DataFrame containing green bond data

    Raises:
    -------
    FileNotFoundError
        If the CSV file is not found at the specified or configured path.
        Error message includes the full path that was attempted.
    ValueError
        If required columns are missing from the loaded data.
    """
    # Determine repository root (parent of src directory)
    repo_root = Path(__file__).parent.parent

    if filepath is None:
        # Get config and use its raw_data_path
        if config is None:
            config = get_config()
        filepath = config.raw_data_path

    # Convert to Path and resolve relative to repo root
    filepath = Path(filepath)
    if not filepath.is_absolute():
        filepath = repo_root / filepath

    # Load the CSV file
    try:
        df = pd.read_csv(filepath, comment="#")
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Green bonds data file not found at '{filepath}'. "
            f"Please ensure the file exists or update the path in config.yaml."
        ) from e

    # Validate required columns
    required_cols = ["bond_id", "issuer", "country_code", "amount_usd_millions"]
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Convert date columns to datetime
    date_columns = ["issue_date", "maturity_date"]
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def load_country_geometries(filepath: str | Path | None = None, config: Config | None = None) -> gpd.GeoDataFrame:
    """
    Load country geometry data from GeoJSON file.

    Parameters:
    -----------
    filepath : str or Path, optional
        Path to the countries GeoJSON file. Can be absolute or relative to repository root.
        If None, uses path from config (or default if config not provided).
    config : Config, optional
        Configuration object. If None and filepath is None, uses global config.

    Returns:
    --------
    gpd.GeoDataFrame
        GeoDataFrame containing country geometries with ISO codes

    Raises:
    -------
    FileNotFoundError
        If the GeoJSON file is not found at the specified or configured path.
        Error message includes the full path that was attempted.
    """
    # Determine repository root (parent of src directory)
    repo_root = Path(__file__).parent.parent

    if filepath is None:
        # Get config and use its geo_data_path
        if config is None:
            config = get_config()
        filepath = config.geo_data_path

    # Convert to Path and resolve relative to repo root
    filepath = Path(filepath)
    if not filepath.is_absolute():
        filepath = repo_root / filepath

    # Load the GeoJSON file
    try:
        gdf = gpd.read_file(filepath)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Country geometries file not found at '{filepath}'. "
            f"Please ensure the file exists or update the path in config.yaml."
        ) from e
    except Exception as e:
        # GeoPandas may raise various errors for file not found (e.g., DataSourceError from pyogrio)
        # Check if it's a file-not-found scenario and convert to FileNotFoundError
        error_type = type(e).__name__
        error_msg = str(e)
        if error_type == "DataSourceError" or "No such file" in error_msg or "does not exist" in error_msg:
            raise FileNotFoundError(
                f"Country geometries file not found at '{filepath}'. "
                f"Please ensure the file exists or update the path in config.yaml."
            ) from e
        # Re-raise other exceptions as-is
        raise

    # Ensure ISO code column exists
    if "iso_a3" not in gdf.columns:
        warnings.warn("GeoJSON missing 'iso_a3' column for ISO country codes", stacklevel=2)

    return gdf


def validate_bond_data(df: pd.DataFrame) -> tuple[bool, list]:
    """
    Validate green bond data for completeness and correctness.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing green bond data

    Returns:
    --------
    Tuple[bool, list]
        (is_valid, list_of_issues)
        is_valid: True if data passes all validation checks
        list_of_issues: List of validation issues found (empty if valid)
    """
    issues = []

    # Check for null values in critical columns
    critical_cols = ["bond_id", "issuer", "country_code", "amount_usd_millions"]
    for col in critical_cols:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                issues.append(f"Column '{col}' has {null_count} null values")

    # Check for duplicate bond IDs
    if "bond_id" in df.columns:
        duplicates = df["bond_id"].duplicated().sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates} duplicate bond IDs")

    # Check for negative amounts
    if "amount_usd_millions" in df.columns:
        negative = (df["amount_usd_millions"] < 0).sum()
        if negative > 0:
            issues.append(f"Found {negative} bonds with negative amounts")

    # Check for valid ISO codes (3 characters)
    if "country_code" in df.columns:
        invalid_codes = df[df["country_code"].str.len() != 3]
        if len(invalid_codes) > 0:
            issues.append(f"Found {len(invalid_codes)} invalid country codes (not 3 characters)")

    is_valid = len(issues) == 0
    return is_valid, issues


def join_bonds_with_geo(bonds_df: pd.DataFrame, geo_df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Join green bond data with country geometries.

    Parameters:
    -----------
    bonds_df : pd.DataFrame
        DataFrame containing green bond data
    geo_df : gpd.GeoDataFrame
        GeoDataFrame containing country geometries

    Returns:
    --------
    gpd.GeoDataFrame
        GeoDataFrame with bond data joined to country geometries
    """
    # Aggregate bonds by country
    country_summary = (
        bonds_df.groupby("country_code")
        .agg({"amount_usd_millions": ["sum", "count", "mean"], "bond_id": "count"})
        .reset_index()
    )

    # Flatten column names
    country_summary.columns = [
        "country_code",
        "total_amount_usd_millions",
        "bond_count",
        "avg_amount_usd_millions",
        "num_bonds",
    ]
    # Remove duplicate column (bond_count and num_bonds are the same)
    country_summary = country_summary.drop("num_bonds", axis=1)

    # Join with geometries
    result = geo_df.merge(country_summary, left_on="iso_a3", right_on="country_code", how="left")

    # Fill NaN values for countries with no bonds
    result["total_amount_usd_millions"] = result["total_amount_usd_millions"].fillna(0)
    result["bond_count"] = result["bond_count"].fillna(0)
    result["avg_amount_usd_millions"] = result["avg_amount_usd_millions"].fillna(0)

    return result


def get_summary_statistics(df: pd.DataFrame) -> dict:
    """
    Calculate summary statistics for green bond data.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing green bond data

    Returns:
    --------
    dict
        Dictionary containing summary statistics
    """
    stats = {
        "total_bonds": len(df),
        "total_amount_usd_millions": df["amount_usd_millions"].sum(),
        "average_bond_size_usd_millions": df["amount_usd_millions"].mean(),
        "median_bond_size_usd_millions": df["amount_usd_millions"].median(),
        "unique_issuers": df["issuer"].nunique(),
        "unique_countries": df["country_code"].nunique(),
    }

    # Add date range if available
    if "issue_date" in df.columns:
        df_with_dates = df.dropna(subset=["issue_date"])
        if len(df_with_dates) > 0:
            stats["earliest_issue"] = df_with_dates["issue_date"].min()
            stats["latest_issue"] = df_with_dates["issue_date"].max()

    # Top countries by amount
    if "country_code" in df.columns:
        top_countries = df.groupby("country_code")["amount_usd_millions"].sum().nlargest(5)
        stats["top_5_countries"] = top_countries.to_dict()

    return stats
