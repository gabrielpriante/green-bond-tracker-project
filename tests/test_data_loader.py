"""
Unit tests for the Green Bond Tracker data loader module.
"""

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loader import (
    get_summary_statistics,
    join_bonds_with_geo,
    load_country_geometries,
    load_green_bonds,
    validate_bond_data,
)


class TestLoadGreenBonds:
    """Tests for load_green_bonds function."""

    def test_load_default_data(self):
        """Test loading green bonds with default path."""
        df = load_green_bonds()
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_required_columns_exist(self):
        """Test that required columns are present."""
        df = load_green_bonds()
        required_cols = ["bond_id", "issuer", "country_code", "amount_usd_millions"]
        for col in required_cols:
            assert col in df.columns

    def test_date_columns_are_datetime(self):
        """Test that date columns are converted to datetime."""
        df = load_green_bonds()
        assert pd.api.types.is_datetime64_any_dtype(df["issue_date"])
        assert pd.api.types.is_datetime64_any_dtype(df["maturity_date"])

    def test_invalid_file_raises_error(self):
        """Test that invalid file path raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_green_bonds("/invalid/path/file.csv")


class TestLoadCountryGeometries:
    """Tests for load_country_geometries function."""

    def test_load_default_geometries(self):
        """Test loading country geometries with default path."""
        gdf = load_country_geometries()
        assert isinstance(gdf, gpd.GeoDataFrame)
        assert len(gdf) > 0

    def test_has_iso_codes(self):
        """Test that GeoDataFrame has ISO code column."""
        gdf = load_country_geometries()
        assert "iso_a3" in gdf.columns

    def test_has_geometry(self):
        """Test that GeoDataFrame has geometry column."""
        gdf = load_country_geometries()
        assert "geometry" in gdf.columns
        assert gdf.geometry.notna().all()

    def test_invalid_file_raises_error(self):
        """Test that invalid file path raises an error."""
        with pytest.raises(Exception):  # GeoDataFrame may raise different error types
            load_country_geometries("/invalid/path/file.json")


class TestValidateBondData:
    """Tests for validate_bond_data function."""

    def test_valid_data(self):
        """Test validation with valid data."""
        df = load_green_bonds()
        is_valid, issues = validate_bond_data(df)
        assert is_valid
        assert len(issues) == 0

    def test_detect_null_values(self):
        """Test detection of null values in critical columns."""
        df = pd.DataFrame(
            {
                "bond_id": ["B1", None, "B3"],
                "issuer": ["Issuer1", "Issuer2", "Issuer3"],
                "country_code": ["USA", "GBR", "DEU"],
                "amount_usd_millions": [100, 200, 300],
            }
        )
        is_valid, issues = validate_bond_data(df)
        assert not is_valid
        assert any("bond_id" in issue for issue in issues)

    def test_detect_duplicate_ids(self):
        """Test detection of duplicate bond IDs."""
        df = pd.DataFrame(
            {
                "bond_id": ["B1", "B1", "B3"],
                "issuer": ["Issuer1", "Issuer2", "Issuer3"],
                "country_code": ["USA", "GBR", "DEU"],
                "amount_usd_millions": [100, 200, 300],
            }
        )
        is_valid, issues = validate_bond_data(df)
        assert not is_valid
        assert any("duplicate" in issue.lower() for issue in issues)

    def test_detect_negative_amounts(self):
        """Test detection of negative amounts."""
        df = pd.DataFrame(
            {
                "bond_id": ["B1", "B2", "B3"],
                "issuer": ["Issuer1", "Issuer2", "Issuer3"],
                "country_code": ["USA", "GBR", "DEU"],
                "amount_usd_millions": [100, -200, 300],
            }
        )
        is_valid, issues = validate_bond_data(df)
        assert not is_valid
        assert any("negative" in issue.lower() for issue in issues)

    def test_detect_invalid_country_codes(self):
        """Test detection of invalid country codes."""
        df = pd.DataFrame(
            {
                "bond_id": ["B1", "B2", "B3"],
                "issuer": ["Issuer1", "Issuer2", "Issuer3"],
                "country_code": ["USA", "GB", "DEU"],  # GB is only 2 chars
                "amount_usd_millions": [100, 200, 300],
            }
        )
        is_valid, issues = validate_bond_data(df)
        assert not is_valid
        assert any("country code" in issue.lower() for issue in issues)

    def test_detect_null_issuer(self):
        """Test detection of null issuer values."""
        df = pd.DataFrame(
            {
                "bond_id": ["B1", "B2", "B3"],
                "issuer": ["Issuer1", None, "Issuer3"],
                "country_code": ["USA", "GBR", "DEU"],
                "amount_usd_millions": [100, 200, 300],
            }
        )
        is_valid, issues = validate_bond_data(df)
        assert not is_valid
        assert any("issuer" in issue.lower() for issue in issues)

    def test_detect_invalid_iso_code_length(self):
        """Test detection of ISO codes with incorrect length."""
        df = pd.DataFrame(
            {
                "bond_id": ["B1", "B2", "B3", "B4"],
                "issuer": ["Issuer1", "Issuer2", "Issuer3", "Issuer4"],
                "country_code": ["USA", "ABCD", "X", "DEU"],  # ABCD is 4 chars, X is 1 char
                "amount_usd_millions": [100, 200, 300, 400],
            }
        )
        is_valid, issues = validate_bond_data(df)
        assert not is_valid
        assert any("country code" in issue.lower() and "3 characters" in issue for issue in issues)


class TestJoinBondsWithGeo:
    """Tests for join_bonds_with_geo function."""

    def test_join_creates_geodataframe(self):
        """Test that join creates a GeoDataFrame."""
        bonds = load_green_bonds()
        countries = load_country_geometries()
        result = join_bonds_with_geo(bonds, countries)
        assert isinstance(result, gpd.GeoDataFrame)

    def test_join_aggregates_by_country(self):
        """Test that bonds are aggregated by country."""
        bonds = load_green_bonds()
        countries = load_country_geometries()
        result = join_bonds_with_geo(bonds, countries)

        # Check that aggregation columns exist
        assert "total_amount_usd_millions" in result.columns
        assert "bond_count" in result.columns
        assert "avg_amount_usd_millions" in result.columns

    def test_join_preserves_all_countries(self):
        """Test that all countries are preserved in result."""
        bonds = load_green_bonds()
        countries = load_country_geometries()
        result = join_bonds_with_geo(bonds, countries)

        # Result should have same number of rows as countries
        assert len(result) == len(countries)

    def test_join_fills_missing_values(self):
        """Test that missing values are filled for countries with no bonds."""
        bonds = load_green_bonds()
        countries = load_country_geometries()
        result = join_bonds_with_geo(bonds, countries)

        # Countries with no bonds should have 0 values
        no_bonds = result[result["bond_count"] == 0]
        assert (no_bonds["total_amount_usd_millions"] == 0).all()


class TestGetSummaryStatistics:
    """Tests for get_summary_statistics function."""

    def test_basic_statistics(self):
        """Test that basic statistics are calculated."""
        df = load_green_bonds()
        stats = get_summary_statistics(df)

        assert "total_bonds" in stats
        assert "total_amount_usd_millions" in stats
        assert "average_bond_size_usd_millions" in stats
        assert "median_bond_size_usd_millions" in stats
        assert "unique_issuers" in stats
        assert "unique_countries" in stats

    def test_statistics_values_correct(self):
        """Test that calculated statistics are correct."""
        df = load_green_bonds()
        stats = get_summary_statistics(df)

        assert stats["total_bonds"] == len(df)
        assert stats["total_amount_usd_millions"] == df["amount_usd_millions"].sum()
        assert stats["unique_issuers"] == df["issuer"].nunique()
        assert stats["unique_countries"] == df["country_code"].nunique()

    def test_date_range_included(self):
        """Test that date range is included when dates are available."""
        df = load_green_bonds()
        stats = get_summary_statistics(df)

        assert "earliest_issue" in stats
        assert "latest_issue" in stats

    def test_top_countries_included(self):
        """Test that top countries by amount are included."""
        df = load_green_bonds()
        stats = get_summary_statistics(df)

        assert "top_5_countries" in stats
        assert isinstance(stats["top_5_countries"], dict)
        assert len(stats["top_5_countries"]) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
