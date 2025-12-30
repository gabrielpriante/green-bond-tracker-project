"""
Green Bond Tracker - Enhanced Validation Module

This module provides comprehensive validation for green bond data
using the schema definitions from schema.py.

Note: This is an educational project and should not be used for investment advice.
"""

import re
from datetime import datetime
from typing import Any

import pandas as pd

from .schema import SCHEMA, CertificationStandard, FieldType, UseOfProceeds


class ValidationResult:
    """Container for validation results."""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.row_flags: dict[int, list[str]] = {}

    def add_error(self, message: str, row_idx: int | None = None):
        """Add a validation error."""
        self.errors.append(message)
        if row_idx is not None:
            if row_idx not in self.row_flags:
                self.row_flags[row_idx] = []
            self.row_flags[row_idx].append(f"ERROR: {message}")

    def add_warning(self, message: str, row_idx: int | None = None):
        """Add a validation warning."""
        self.warnings.append(message)
        if row_idx is not None:
            if row_idx not in self.row_flags:
                self.row_flags[row_idx] = []
            self.row_flags[row_idx].append(f"WARNING: {message}")

    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0

    def get_summary(self) -> str:
        """Get a summary of validation results."""
        lines = []
        if self.is_valid:
            lines.append("✓ Validation PASSED")
        else:
            lines.append("✗ Validation FAILED")

        lines.append(f"  Errors: {len(self.errors)}")
        lines.append(f"  Warnings: {len(self.warnings)}")

        if self.errors:
            lines.append("\nErrors:")
            for error in self.errors:
                lines.append(f"  - {error}")

        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)


def validate_bond_data_enhanced(df: pd.DataFrame) -> ValidationResult:
    """
    Comprehensive validation of green bond data using schema definitions.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing green bond data

    Returns
    -------
    ValidationResult
        Object containing validation errors, warnings, and row-level flags
    """
    result = ValidationResult()

    # Check for missing required columns
    missing_cols = set(SCHEMA.get_required_field_names()) - set(df.columns)
    if missing_cols:
        result.add_error(f"Missing required columns: {', '.join(sorted(missing_cols))}")
        return result  # Cannot continue without required columns

    # Validate each field according to schema
    for field_def in SCHEMA.fields:
        if field_def.name not in df.columns:
            if field_def.required:
                result.add_error(f"Required field '{field_def.name}' is missing")
            continue

        _validate_field(df, field_def, result)

    # Cross-field validations
    _validate_date_consistency(df, result)
    _validate_duplicate_ids(df, result)

    return result


def _validate_field(df: pd.DataFrame, field_def: Any, result: ValidationResult):
    """Validate a single field according to its definition."""
    col = field_def.name
    series = df[col]

    # Check for null values
    null_mask = series.isnull()
    null_count = null_mask.sum()

    if null_count > 0:
        if field_def.required:
            result.add_error(f"Field '{col}' has {null_count} null values (required field)")
            for idx in df[null_mask].index:
                result.add_error(f"Null value in required field '{col}'", row_idx=idx)
        else:
            result.add_warning(f"Field '{col}' has {null_count} null values")

    # Validate non-null values
    valid_mask = ~null_mask

    if field_def.type == FieldType.FLOAT or field_def.type == FieldType.INTEGER:
        _validate_numeric_field(df, col, field_def, valid_mask, result)
    elif field_def.type == FieldType.STRING:
        _validate_string_field(df, col, field_def, valid_mask, result)
    elif field_def.type == FieldType.DATE:
        _validate_date_field(df, col, field_def, valid_mask, result)


def _validate_numeric_field(
    df: pd.DataFrame, col: str, field_def: Any, valid_mask: pd.Series, result: ValidationResult
):
    """Validate numeric field values."""
    series = df.loc[valid_mask, col]

    # Check if values are numeric
    try:
        numeric_series = pd.to_numeric(series, errors="coerce")
        non_numeric_mask = numeric_series.isnull() & valid_mask
        non_numeric_count = non_numeric_mask.sum()

        if non_numeric_count > 0:
            result.add_error(f"Field '{col}' has {non_numeric_count} non-numeric values")
            for idx in df[non_numeric_mask].index:
                value = df.loc[idx, col]
                result.add_error(f"Non-numeric value '{value}' in field '{col}'", row_idx=idx)
            return

        # Check min/max bounds
        if field_def.min_value is not None:
            below_min = numeric_series < field_def.min_value
            below_min_count = below_min.sum()
            if below_min_count > 0:
                result.add_error(
                    f"Field '{col}' has {below_min_count} values below minimum {field_def.min_value}"
                )
                for idx in series[below_min].index:
                    value = series.loc[idx]
                    result.add_error(
                        f"Value {value} below minimum {field_def.min_value} in '{col}'",
                        row_idx=idx,
                    )

        if field_def.max_value is not None:
            above_max = numeric_series > field_def.max_value
            above_max_count = above_max.sum()
            if above_max_count > 0:
                result.add_error(
                    f"Field '{col}' has {above_max_count} values above maximum {field_def.max_value}"
                )
                for idx in series[above_max].index:
                    value = series.loc[idx]
                    result.add_error(
                        f"Value {value} above maximum {field_def.max_value} in '{col}'",
                        row_idx=idx,
                    )

    except Exception as e:
        result.add_error(f"Error validating numeric field '{col}': {e}")


def _validate_string_field(
    df: pd.DataFrame, col: str, field_def: Any, valid_mask: pd.Series, result: ValidationResult
):
    """Validate string field values."""
    series = df.loc[valid_mask, col].astype(str)

    # Check min/max length
    if field_def.min_length is not None:
        too_short = series.str.len() < field_def.min_length
        too_short_count = too_short.sum()
        if too_short_count > 0:
            result.add_error(
                f"Field '{col}' has {too_short_count} values shorter than {field_def.min_length} characters"
            )
            for idx in series[too_short].index:
                value = series.loc[idx]
                result.add_error(
                    f"Value '{value}' too short (min {field_def.min_length} chars) in '{col}'",
                    row_idx=idx,
                )

    if field_def.max_length is not None:
        too_long = series.str.len() > field_def.max_length
        too_long_count = too_long.sum()
        if too_long_count > 0:
            result.add_error(
                f"Field '{col}' has {too_long_count} values longer than {field_def.max_length} characters"
            )
            for idx in series[too_long].index:
                value = series.loc[idx]
                result.add_error(
                    f"Value '{value}' too long (max {field_def.max_length} chars) in '{col}'",
                    row_idx=idx,
                )

    # Check pattern
    if field_def.pattern is not None:
        pattern = re.compile(field_def.pattern)
        invalid = ~series.str.match(pattern)
        invalid_count = invalid.sum()
        if invalid_count > 0:
            result.add_error(
                f"Field '{col}' has {invalid_count} values not matching pattern {field_def.pattern}"
            )
            for idx in series[invalid].index:
                value = series.loc[idx]
                result.add_error(
                    f"Value '{value}' doesn't match pattern {field_def.pattern} in '{col}'",
                    row_idx=idx,
                )

    # Check allowed values
    if field_def.allowed_values is not None:
        not_allowed = ~series.isin(field_def.allowed_values)
        not_allowed_count = not_allowed.sum()
        if not_allowed_count > 0:
            result.add_warning(
                f"Field '{col}' has {not_allowed_count} values not in recognized list"
            )
            for idx in series[not_allowed].index:
                value = series.loc[idx]
                result.add_warning(
                    f"Value '{value}' not in recognized list for '{col}'", row_idx=idx
                )


def _validate_date_field(
    df: pd.DataFrame, col: str, field_def: Any, valid_mask: pd.Series, result: ValidationResult
):
    """Validate date field values."""
    series = df.loc[valid_mask, col]

    # Try to parse dates
    try:
        date_series = pd.to_datetime(series, errors="coerce")
        invalid_dates = date_series.isnull() & valid_mask
        invalid_count = invalid_dates.sum()

        if invalid_count > 0:
            result.add_error(f"Field '{col}' has {invalid_count} invalid date values")
            for idx in df[invalid_dates].index:
                value = df.loc[idx, col]
                result.add_error(f"Invalid date '{value}' in field '{col}'", row_idx=idx)

        # Warn about future dates for issue_date
        if col == "issue_date":
            future_dates = date_series > pd.Timestamp.now()
            future_count = future_dates.sum()
            if future_count > 0:
                result.add_warning(f"Field '{col}' has {future_count} future dates")
                for idx in date_series[future_dates].index:
                    value = date_series.loc[idx]
                    result.add_warning(f"Future date {value} in '{col}'", row_idx=idx)

    except Exception as e:
        result.add_error(f"Error validating date field '{col}': {e}")


def _validate_date_consistency(df: pd.DataFrame, result: ValidationResult):
    """Validate that issue_date <= maturity_date."""
    if "issue_date" in df.columns and "maturity_date" in df.columns:
        try:
            issue = pd.to_datetime(df["issue_date"], errors="coerce")
            maturity = pd.to_datetime(df["maturity_date"], errors="coerce")

            both_valid = issue.notna() & maturity.notna()
            inconsistent = both_valid & (issue > maturity)
            inconsistent_count = inconsistent.sum()

            if inconsistent_count > 0:
                result.add_error(
                    f"Found {inconsistent_count} records where issue_date > maturity_date"
                )
                for idx in df[inconsistent].index:
                    issue_val = issue.loc[idx]
                    maturity_val = maturity.loc[idx]
                    result.add_error(
                        f"issue_date ({issue_val}) > maturity_date ({maturity_val})", row_idx=idx
                    )

        except Exception as e:
            result.add_warning(f"Could not validate date consistency: {e}")


def _validate_duplicate_ids(df: pd.DataFrame, result: ValidationResult):
    """Check for duplicate bond IDs."""
    if "bond_id" not in df.columns:
        return

    duplicates = df["bond_id"].duplicated(keep=False)
    duplicate_count = duplicates.sum()

    if duplicate_count > 0:
        duplicate_ids = df.loc[duplicates, "bond_id"].unique()
        result.add_error(f"Found {len(duplicate_ids)} duplicate bond IDs")

        for bond_id in duplicate_ids:
            indices = df[df["bond_id"] == bond_id].index.tolist()
            result.add_error(f"Duplicate bond_id '{bond_id}' at rows: {indices}")
            for idx in indices:
                result.add_error(f"Duplicate bond_id '{bond_id}'", row_idx=idx)
