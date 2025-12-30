"""
Unit tests for the validation module.
"""

from pathlib import Path

import pandas as pd
import pytest

from src.validation import (
    ValidationResult,
    validate_bond_data_enhanced,
)


@pytest.fixture
def valid_bond_data():
    """Fixture providing valid bond data."""
    return pd.DataFrame(
        {
            "bond_id": ["GB001", "GB002", "GB003"],
            "issuer": ["Test Bank A", "Test Bank B", "Test Bank C"],
            "country_code": ["USA", "GBR", "DEU"],
            "amount_usd_millions": [500.0, 1000.0, 750.0],
            "issue_date": ["2023-01-15", "2023-03-20", "2023-02-10"],
            "maturity_date": ["2033-01-15", "2028-03-20", "2030-02-10"],
            "currency": ["USD", "GBP", "EUR"],
            "coupon_rate": [2.5, 3.0, 3.2],
            "use_of_proceeds": [
                "Renewable Energy",
                "Clean Transportation",
                "Energy Efficiency",
            ],
            "certification": [
                "Climate Bonds Initiative",
                "Green Bond Principles",
                "Climate Bonds Initiative",
            ],
        }
    )


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_create_empty_result(self):
        """Test creating an empty validation result."""
        result = ValidationResult()
        assert result.is_valid
        assert not result.has_warnings
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_add_error(self):
        """Test adding an error."""
        result = ValidationResult()
        result.add_error("Test error")

        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0] == "Test error"

    def test_add_warning(self):
        """Test adding a warning."""
        result = ValidationResult()
        result.add_warning("Test warning")

        assert result.is_valid  # Warnings don't affect validity
        assert result.has_warnings
        assert len(result.warnings) == 1

    def test_add_error_with_row_index(self):
        """Test adding an error with row index."""
        result = ValidationResult()
        result.add_error("Row error", row_idx=5)

        assert 5 in result.row_flags
        assert len(result.row_flags[5]) == 1

    def test_get_summary(self):
        """Test getting validation summary."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_warning("Warning 1")

        summary = result.get_summary()
        assert "FAILED" in summary
        assert "Errors: 1" in summary
        assert "Warnings: 1" in summary


class TestValidateBondDataEnhanced:
    """Tests for validate_bond_data_enhanced function."""

    def test_valid_data_passes(self, valid_bond_data):
        """Test that valid data passes validation."""
        result = validate_bond_data_enhanced(valid_bond_data)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_required_column_fails(self, valid_bond_data):
        """Test that missing required column fails validation."""
        df = valid_bond_data.drop(columns=["bond_id"])
        result = validate_bond_data_enhanced(df)

        assert not result.is_valid
        assert any("bond_id" in error.lower() for error in result.errors)

    def test_null_in_required_field_fails(self, valid_bond_data):
        """Test that null values in required fields fail validation."""
        df = valid_bond_data.copy()
        df.loc[0, "bond_id"] = None

        result = validate_bond_data_enhanced(df)

        assert not result.is_valid
        assert any("null" in error.lower() for error in result.errors)

    def test_duplicate_bond_ids_fails(self, valid_bond_data):
        """Test that duplicate bond IDs fail validation."""
        df = valid_bond_data.copy()
        df.loc[1, "bond_id"] = df.loc[0, "bond_id"]  # Create duplicate

        result = validate_bond_data_enhanced(df)

        assert not result.is_valid
        assert any("duplicate" in error.lower() for error in result.errors)

    def test_negative_amount_fails(self, valid_bond_data):
        """Test that negative amounts fail validation."""
        df = valid_bond_data.copy()
        df.loc[0, "amount_usd_millions"] = -100.0

        result = validate_bond_data_enhanced(df)

        assert not result.is_valid
        assert any("below minimum" in error.lower() for error in result.errors)

    def test_invalid_country_code_length_fails(self, valid_bond_data):
        """Test that invalid country code length fails validation."""
        df = valid_bond_data.copy()
        df.loc[0, "country_code"] = "US"  # Only 2 characters

        result = validate_bond_data_enhanced(df)

        assert not result.is_valid
        assert any("country_code" in error.lower() for error in result.errors)

    def test_invalid_country_code_pattern_fails(self, valid_bond_data):
        """Test that country codes not matching pattern fail validation."""
        df = valid_bond_data.copy()
        df.loc[0, "country_code"] = "us1"  # Lowercase and number

        result = validate_bond_data_enhanced(df)

        assert not result.is_valid

    def test_invalid_date_format_fails(self, valid_bond_data):
        """Test that invalid date format fails validation."""
        df = valid_bond_data.copy()
        df.loc[0, "issue_date"] = "not-a-date"

        result = validate_bond_data_enhanced(df)

        assert not result.is_valid
        assert any("invalid date" in error.lower() for error in result.errors)

    def test_maturity_before_issue_fails(self, valid_bond_data):
        """Test that maturity_date before issue_date fails validation."""
        df = valid_bond_data.copy()
        df.loc[0, "issue_date"] = "2030-01-01"
        df.loc[0, "maturity_date"] = "2020-01-01"

        result = validate_bond_data_enhanced(df)

        assert not result.is_valid
        assert any("maturity" in error.lower() for error in result.errors)

    def test_unrecognized_use_of_proceeds_warns(self, valid_bond_data):
        """Test that unrecognized use of proceeds generates warning."""
        df = valid_bond_data.copy()
        df.loc[0, "use_of_proceeds"] = "Unknown Category"

        result = validate_bond_data_enhanced(df)

        # Should be valid but have warnings
        assert result.is_valid
        assert result.has_warnings
        assert any("use_of_proceeds" in warning.lower() for warning in result.warnings)

    def test_coupon_rate_above_100_fails(self, valid_bond_data):
        """Test that coupon rate above 100% fails validation."""
        df = valid_bond_data.copy()
        df.loc[0, "coupon_rate"] = 150.0

        result = validate_bond_data_enhanced(df)

        assert not result.is_valid
        assert any("above maximum" in error.lower() for error in result.errors)

    def test_row_flags_populated(self, valid_bond_data):
        """Test that row flags are populated for invalid rows."""
        df = valid_bond_data.copy()
        df.loc[0, "bond_id"] = None  # Invalid
        df.loc[1, "amount_usd_millions"] = -100  # Invalid

        result = validate_bond_data_enhanced(df)

        assert not result.is_valid
        assert 0 in result.row_flags
        assert 1 in result.row_flags
        assert 2 not in result.row_flags  # Row 2 should be valid


class TestValidationWithFixtures:
    """Tests using fixture files."""

    def test_validate_fixture_data(self):
        """Test validation using fixture data file."""
        from src.data_loader import load_green_bonds

        fixture_path = Path(__file__).parent / "fixtures" / "test_bonds.csv"
        df = load_green_bonds(str(fixture_path))

        result = validate_bond_data_enhanced(df)

        # Fixture data should be valid
        assert result.is_valid or result.has_warnings  # Allow warnings


class TestEdgeCases:
    """Tests for edge cases in validation."""

    def test_empty_dataframe(self):
        """Test validation of empty dataframe."""
        df = pd.DataFrame()
        result = validate_bond_data_enhanced(df)

        assert not result.is_valid  # Should fail due to missing required columns

    def test_single_row(self):
        """Test validation of single row dataframe."""
        df = pd.DataFrame(
            {
                "bond_id": ["GB001"],
                "issuer": ["Test"],
                "country_code": ["USA"],
                "amount_usd_millions": [500.0],
            }
        )

        result = validate_bond_data_enhanced(df)
        assert result.is_valid

    def test_all_optional_fields_null(self):
        """Test validation when all optional fields are null."""
        df = pd.DataFrame(
            {
                "bond_id": ["GB001"],
                "issuer": ["Test"],
                "country_code": ["USA"],
                "amount_usd_millions": [500.0],
                "issue_date": [None],
                "maturity_date": [None],
                "currency": [None],
                "coupon_rate": [None],
                "use_of_proceeds": [None],
                "certification": [None],
            }
        )

        result = validate_bond_data_enhanced(df)
        # Should be valid but may have warnings
        assert result.is_valid
