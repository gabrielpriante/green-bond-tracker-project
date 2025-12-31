"""
Unit tests for the analytics module.
"""

import pandas as pd
import pytest

from src.analytics.metrics import (
    aggregation_by_category,
    aggregation_by_country,
    aggregation_by_year,
    concentration_index,
    data_coverage_report,
    issuance_overview,
    portfolio_summary_table,
    top_n_concentration,
)


@pytest.fixture
def sample_bond_data():
    """Fixture providing sample bond data for testing."""
    return pd.DataFrame(
        {
            "bond_id": ["GB001", "GB002", "GB003", "GB004", "GB005"],
            "issuer": ["Bank A", "Bank B", "Bank C", "Bank A", "Bank D"],
            "country_code": ["USA", "USA", "GBR", "USA", "DEU"],
            "amount_usd_millions": [500.0, 1000.0, 750.0, 300.0, 450.0],
            "issue_date": pd.to_datetime(
                ["2021-01-15", "2022-03-20", "2022-02-10", "2023-04-05", "2023-06-15"]
            ),
            "maturity_date": pd.to_datetime(
                ["2031-01-15", "2027-03-20", "2030-02-10", "2033-04-05", "2035-06-15"]
            ),
            "currency": ["USD", "USD", "GBP", "USD", "EUR"],
            "use_of_proceeds": [
                "Renewable Energy",
                "Clean Transportation",
                "Energy Efficiency",
                "Renewable Energy",
                "Green Buildings",
            ],
            "certification": [
                "Climate Bonds Initiative",
                "Green Bond Principles",
                "Climate Bonds Initiative",
                "Green Bond Principles",
                None,
            ],
        }
    )


@pytest.fixture
def minimal_bond_data():
    """Fixture providing minimal bond data (required fields only)."""
    return pd.DataFrame(
        {
            "bond_id": ["GB001", "GB002", "GB003"],
            "issuer": ["Bank A", "Bank B", "Bank C"],
            "country_code": ["USA", "GBR", "DEU"],
            "amount_usd_millions": [500.0, 1000.0, 750.0],
        }
    )


class TestIssuanceOverview:
    """Tests for issuance_overview function."""

    def test_overview_with_full_data(self, sample_bond_data):
        """Test overview with complete data."""
        result = issuance_overview(sample_bond_data)

        assert result["total_bonds"] == 5
        assert result["total_issuance_usd_millions"] == 3000.0
        assert result["year_range"] == (2021, 2023)
        assert result["unique_issuers"] == 4
        assert result["pct_missing_country"] == 0.0
        assert result["pct_missing_year"] == 0.0
        assert result["pct_missing_amount"] == 0.0

    def test_overview_with_minimal_data(self, minimal_bond_data):
        """Test overview with only required fields."""
        result = issuance_overview(minimal_bond_data)

        assert result["total_bonds"] == 3
        assert result["total_issuance_usd_millions"] == 2250.0
        assert result["year_range"] is None  # No issue_date column
        assert result["unique_issuers"] == 3
        assert result["pct_missing_year"] is None

    def test_overview_with_missing_values(self, sample_bond_data):
        """Test overview with some missing values."""
        df = sample_bond_data.copy()
        df.loc[0, "country_code"] = None
        df.loc[1, "amount_usd_millions"] = None

        result = issuance_overview(df)

        assert result["total_bonds"] == 5
        assert result["pct_missing_country"] == 20.0  # 1 out of 5
        assert result["pct_missing_amount"] == 20.0  # 1 out of 5


class TestAggregationByCountry:
    """Tests for aggregation_by_country function."""

    def test_country_aggregation(self, sample_bond_data):
        """Test basic country aggregation."""
        result = aggregation_by_country(sample_bond_data)

        assert len(result) == 3  # USA, GBR, DEU
        assert "country_code" in result.columns
        assert "bond_count" in result.columns
        assert "total_issuance_usd_millions" in result.columns
        assert "share_of_total_pct" in result.columns

        # Check USA (should be first - highest amount)
        usa_row = result[result["country_code"] == "USA"].iloc[0]
        assert usa_row["bond_count"] == 3
        assert usa_row["total_issuance_usd_millions"] == 1800.0
        assert usa_row["share_of_total_pct"] == 60.0  # 1800/3000

    def test_country_aggregation_sorted(self, sample_bond_data):
        """Test that results are sorted by total issuance descending."""
        result = aggregation_by_country(sample_bond_data)

        # First row should be USA with highest amount
        assert result.iloc[0]["country_code"] == "USA"
        assert result.iloc[0]["total_issuance_usd_millions"] == 1800.0

    def test_country_aggregation_shares_sum_to_100(self, sample_bond_data):
        """Test that shares sum to approximately 100%."""
        result = aggregation_by_country(sample_bond_data)
        total_share = result["share_of_total_pct"].sum()

        assert abs(total_share - 100.0) < 0.01  # Allow for rounding

    def test_country_aggregation_without_amount(self):
        """Test country aggregation when amount column is missing."""
        df = pd.DataFrame(
            {
                "bond_id": ["GB001", "GB002", "GB003"],
                "country_code": ["USA", "USA", "GBR"],
            }
        )

        result = aggregation_by_country(df)

        assert len(result) == 2
        assert result.iloc[0]["bond_count"] == 2  # USA
        assert pd.isna(result.iloc[0]["total_issuance_usd_millions"])


class TestAggregationByYear:
    """Tests for aggregation_by_year function."""

    def test_year_aggregation(self, sample_bond_data):
        """Test basic year aggregation."""
        result = aggregation_by_year(sample_bond_data)

        assert len(result) == 3  # 2021, 2022, 2023
        assert "year" in result.columns
        assert "bond_count" in result.columns
        assert "issuance_amount_usd_millions" in result.columns
        assert "yoy_growth_pct" in result.columns

        # Check 2022
        year_2022 = result[result["year"] == 2022].iloc[0]
        assert year_2022["bond_count"] == 2
        assert year_2022["issuance_amount_usd_millions"] == 1750.0

    def test_year_aggregation_yoy_growth(self, sample_bond_data):
        """Test YoY growth calculation."""
        result = aggregation_by_year(sample_bond_data)

        # First year should have NaN growth
        assert pd.isna(result.iloc[0]["yoy_growth_pct"])

        # Second year should have calculated growth
        # 2021: 500, 2022: 1750 -> growth = (1750-500)/500 * 100 = 250%
        year_2022 = result[result["year"] == 2022].iloc[0]
        assert year_2022["yoy_growth_pct"] == 250.0

    def test_year_aggregation_without_date(self, minimal_bond_data):
        """Test year aggregation when issue_date column is missing."""
        result = aggregation_by_year(minimal_bond_data)

        assert len(result) == 0  # Empty DataFrame


class TestAggregationByCategory:
    """Tests for aggregation_by_category function."""

    def test_category_aggregation_use_of_proceeds(self, sample_bond_data):
        """Test aggregation by use_of_proceeds."""
        result = aggregation_by_category(sample_bond_data, "use_of_proceeds")

        assert len(result) == 4  # 4 unique categories
        assert "use_of_proceeds" in result.columns
        assert "bond_count" in result.columns

        # Renewable Energy should have 2 bonds
        renewable = result[result["use_of_proceeds"] == "Renewable Energy"].iloc[0]
        assert renewable["bond_count"] == 2
        assert renewable["total_issuance_usd_millions"] == 800.0

    def test_category_aggregation_with_nulls(self, sample_bond_data):
        """Test that null values are excluded."""
        result = aggregation_by_category(sample_bond_data, "certification")

        # Should only have 2 certifications (one bond has None)
        assert len(result) == 2

    def test_category_aggregation_nonexistent_column(self, sample_bond_data):
        """Test aggregation with non-existent column."""
        result = aggregation_by_category(sample_bond_data, "nonexistent_column")

        assert len(result) == 0
        assert "nonexistent_column" in result.columns


class TestTopNConcentration:
    """Tests for top_n_concentration function."""

    def test_top_n_concentration_default(self, sample_bond_data):
        """Test top-N concentration with default parameters."""
        result = top_n_concentration(sample_bond_data)

        assert result["n"] == 5
        assert isinstance(result["top_n_entries"], list)
        assert isinstance(result["top_n_share_pct"], float)

        # With only 3 countries, should return all 3
        assert len(result["top_n_entries"]) == 3
        assert result["top_n_share_pct"] == 100.0

    def test_top_n_concentration_top_2(self, sample_bond_data):
        """Test top-2 concentration."""
        result = top_n_concentration(sample_bond_data, "country_code", n=2)

        assert result["n"] == 2
        assert len(result["top_n_entries"]) == 2

        # USA (60%) + GBR (25%) = 85%
        assert result["top_n_share_pct"] == 85.0

    def test_top_n_concentration_invalid_column(self, sample_bond_data):
        """Test with non-existent column."""
        result = top_n_concentration(sample_bond_data, "invalid_column", n=5)

        assert result["top_n_entries"] == []
        assert result["top_n_share_pct"] == 0.0


class TestConcentrationIndex:
    """Tests for concentration_index function."""

    def test_concentration_index_calculation(self, sample_bond_data):
        """Test HHI calculation."""
        hhi = concentration_index(sample_bond_data, "country_code")

        # USA: 60%, GBR: 25%, DEU: 15%
        # HHI = 60^2 + 25^2 + 15^2 = 3600 + 625 + 225 = 4450
        assert hhi == 4450.0

    def test_concentration_index_single_entity(self):
        """Test HHI with single entity (maximum concentration)."""
        df = pd.DataFrame(
            {
                "bond_id": ["GB001", "GB002"],
                "country_code": ["USA", "USA"],
                "amount_usd_millions": [500.0, 500.0],
            }
        )

        hhi = concentration_index(df, "country_code")

        # Single entity = 100% share -> HHI = 10000
        assert hhi == 10000.0

    def test_concentration_index_invalid_column(self, sample_bond_data):
        """Test HHI with non-existent column."""
        hhi = concentration_index(sample_bond_data, "invalid_column")

        assert hhi == 0.0


class TestDataCoverageReport:
    """Tests for data_coverage_report function."""

    def test_coverage_report_full_data(self, sample_bond_data):
        """Test coverage report with complete data."""
        result = data_coverage_report(sample_bond_data)

        assert len(result) > 0
        assert "column_name" in result.columns
        assert "non_null_count" in result.columns
        assert "pct_non_null" in result.columns
        assert "coverage_note" in result.columns

        # Check a column with full data
        bond_id_row = result[result["column_name"] == "bond_id"].iloc[0]
        assert bond_id_row["non_null_count"] == 5
        assert bond_id_row["pct_non_null"] == 100.0
        assert "✓" in bond_id_row["coverage_note"]

    def test_coverage_report_with_missing_data(self, sample_bond_data):
        """Test coverage report with missing values."""
        df = sample_bond_data.copy()
        # certification already has 1 None, add 2 more
        df.loc[0, "certification"] = None
        df.loc[1, "certification"] = None

        result = data_coverage_report(df)

        # certification column should have 40% coverage (2 out of 5)
        cert_row = result[result["column_name"] == "certification"].iloc[0]
        assert cert_row["non_null_count"] == 2
        assert cert_row["pct_non_null"] == 40.0
        assert "⚠" in cert_row["coverage_note"]  # Low coverage warning

    def test_coverage_report_sorted(self, sample_bond_data):
        """Test that coverage report is sorted by pct_non_null descending."""
        result = data_coverage_report(sample_bond_data)

        # First row should have highest coverage
        assert result.iloc[0]["pct_non_null"] >= result.iloc[-1]["pct_non_null"]


class TestPortfolioSummaryTable:
    """Tests for portfolio_summary_table function."""

    def test_portfolio_summary_structure(self, sample_bond_data):
        """Test portfolio summary table structure."""
        result = portfolio_summary_table(sample_bond_data)

        assert "metric" in result.columns
        assert "value" in result.columns
        assert len(result) > 0

    def test_portfolio_summary_contains_key_metrics(self, sample_bond_data):
        """Test that summary contains expected metrics."""
        result = portfolio_summary_table(sample_bond_data)

        metrics = result["metric"].tolist()

        # Check for essential metrics
        assert "Total Bonds" in metrics
        assert "Total Issuance (USD Millions)" in metrics
        assert "Unique Issuers" in metrics
        assert "Top 5 Countries Share (%)" in metrics
        assert "Country Concentration (HHI)" in metrics

    def test_portfolio_summary_values_are_strings(self, sample_bond_data):
        """Test that all values are formatted as strings."""
        result = portfolio_summary_table(sample_bond_data)

        for value in result["value"]:
            assert isinstance(value, str)

    def test_portfolio_summary_with_minimal_data(self, minimal_bond_data):
        """Test portfolio summary with minimal data."""
        result = portfolio_summary_table(minimal_bond_data)

        # Should still produce a table even without optional fields
        assert len(result) > 0
        assert "Total Bonds" in result["metric"].values


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_dataframe(self):
        """Test functions with empty DataFrame."""
        df = pd.DataFrame()

        overview = issuance_overview(df)
        assert overview["total_bonds"] == 0

        coverage = data_coverage_report(df)
        assert len(coverage) == 0

    def test_single_row_dataframe(self):
        """Test functions with single-row DataFrame."""
        df = pd.DataFrame(
            {
                "bond_id": ["GB001"],
                "issuer": ["Bank A"],
                "country_code": ["USA"],
                "amount_usd_millions": [500.0],
            }
        )

        overview = issuance_overview(df)
        assert overview["total_bonds"] == 1

        countries = aggregation_by_country(df)
        assert len(countries) == 1

    def test_all_null_column(self):
        """Test with a column that has all null values."""
        df = pd.DataFrame(
            {
                "bond_id": ["GB001", "GB002"],
                "country_code": ["USA", "GBR"],
                "amount_usd_millions": [500.0, 1000.0],
                "use_of_proceeds": [None, None],
            }
        )

        result = aggregation_by_category(df, "use_of_proceeds")
        assert len(result) == 0

        coverage = data_coverage_report(df)
        proceeds_row = coverage[coverage["column_name"] == "use_of_proceeds"].iloc[0]
        assert proceeds_row["pct_non_null"] == 0.0
