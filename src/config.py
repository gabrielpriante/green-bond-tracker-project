"""
Green Bond Tracker - Configuration Module

This module provides centralized configuration management for the Green Bond Tracker.
It loads and validates YAML configuration files, providing type-safe access to settings.

Note: This is an educational project and should not be used for investment advice.
"""

import warnings
from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(Exception):
    """Raised when configuration is invalid or cannot be loaded."""

    pass


class Config:
    """
    Configuration object for Green Bond Tracker.

    Loads configuration from YAML file and provides validated access to settings.
    Falls back to sensible defaults when configuration is missing.
    """

    def __init__(self, config_dict: dict[str, Any] | None = None):
        """
        Initialize configuration from dictionary.

        Parameters:
        -----------
        config_dict : dict, optional
            Configuration dictionary. If None, uses empty dict (all defaults).
        """
        self._config = config_dict or {}

    # =========================================================================
    # PATH CONFIGURATION
    # =========================================================================

    @property
    def raw_data_path(self) -> str:
        """Get path to raw bond data CSV file."""
        default = "data/green_bonds.csv"
        path = self._config.get("paths", {}).get("raw_data", default)
        if path == default and "paths" not in self._config:
            warnings.warn(
                f"Using default raw_data path: {default}. "
                "Consider setting 'paths.raw_data' in config.yaml",
                stacklevel=2,
            )
        return path

    @property
    def geo_data_path(self) -> str:
        """Get path to geographic data GeoJSON file."""
        default = "data/countries_geo.json"
        path = self._config.get("paths", {}).get("geo_data", default)
        if path == default and "paths" not in self._config:
            warnings.warn(
                f"Using default geo_data path: {default}. "
                "Consider setting 'paths.geo_data' in config.yaml",
                stacklevel=2,
            )
        return path

    @property
    def outputs_dir(self) -> str:
        """Get path to outputs directory."""
        default = "outputs"
        path = self._config.get("paths", {}).get("outputs", default)
        return path

    @property
    def maps_dir(self) -> str:
        """Get path to maps directory."""
        default = "maps"
        path = self._config.get("paths", {}).get("maps", default)
        return path

    # =========================================================================
    # SCHEMA CONFIGURATION
    # =========================================================================

    @property
    def required_columns(self) -> list[str]:
        """Get list of required column names."""
        default = ["bond_id", "issuer", "country_code", "amount_usd_millions"]
        return self._config.get("schema", {}).get("required_columns", default)

    @property
    def optional_columns(self) -> list[str]:
        """Get list of optional column names."""
        default = [
            "issue_date",
            "maturity_date",
            "currency",
            "coupon_rate",
            "use_of_proceeds",
            "certification",
        ]
        return self._config.get("schema", {}).get("optional_columns", default)

    @property
    def all_columns(self) -> list[str]:
        """Get list of all column names (required + optional)."""
        return self.required_columns + self.optional_columns

    @property
    def dtypes(self) -> dict[str, str]:
        """Get data type mappings for columns."""
        default = {
            "bond_id": "string",
            "issuer": "string",
            "country_code": "string",
            "amount_usd_millions": "float",
            "issue_date": "date",
            "maturity_date": "date",
            "currency": "string",
            "coupon_rate": "float",
            "use_of_proceeds": "string",
            "certification": "string",
        }
        return self._config.get("schema", {}).get("dtypes", default)

    @property
    def validation_rules(self) -> dict[str, dict]:
        """Get validation rules for columns."""
        return self._config.get("schema", {}).get("validation", {})

    # =========================================================================
    # NORMALIZATION CONFIGURATION
    # =========================================================================

    @property
    def currency_fields(self) -> list[str]:
        """Get list of currency field names."""
        default = ["amount_usd_millions"]
        return self._config.get("normalization", {}).get("currency_fields", default)

    @property
    def date_fields(self) -> list[str]:
        """Get list of date field names."""
        default = ["issue_date", "maturity_date"]
        return self._config.get("normalization", {}).get("date_fields", default)

    @property
    def numeric_fields(self) -> list[str]:
        """Get list of numeric field names."""
        default = ["amount_usd_millions", "coupon_rate"]
        return self._config.get("normalization", {}).get("numeric_fields", default)

    @property
    def string_fields(self) -> list[str]:
        """Get list of string field names."""
        default = [
            "bond_id",
            "issuer",
            "country_code",
            "currency",
            "use_of_proceeds",
            "certification",
        ]
        return self._config.get("normalization", {}).get("string_fields", default)

    # =========================================================================
    # MAP CONFIGURATION
    # =========================================================================

    @property
    def map_default_output(self) -> str:
        """Get default output filename for maps."""
        default = "green_bonds_map.html"
        return self._config.get("map", {}).get("default_output", default)

    @property
    def map_tooltip_fields(self) -> list[str]:
        """Get list of fields to include in map tooltips."""
        default = ["name", "total_amount_usd_millions", "bond_count", "avg_amount_usd_millions"]
        return self._config.get("map", {}).get("tooltip_fields", default)

    @property
    def map_colormap(self) -> str:
        """Get default colormap for choropleth maps."""
        default = "YlGn"
        return self._config.get("map", {}).get("style", {}).get("colormap", default)

    @property
    def map_figsize(self) -> tuple[int, int]:
        """Get default figure size for maps."""
        default = [14, 8]
        figsize = self._config.get("map", {}).get("style", {}).get("figsize", default)
        return tuple(figsize)

    @property
    def map_dpi(self) -> int:
        """Get default DPI for static maps."""
        default = 300
        return self._config.get("map", {}).get("style", {}).get("dpi", default)

    # =========================================================================
    # ANALYTICS CONFIGURATION
    # =========================================================================

    @property
    def analytics_top_n(self) -> int:
        """Get top N value for concentration analysis."""
        default = 5
        return self._config.get("analytics", {}).get("top_n", default)

    @property
    def analytics_coverage_threshold(self) -> float:
        """Get minimum coverage threshold for quality warnings."""
        default = 80.0
        return self._config.get("analytics", {}).get("coverage_threshold", default)

    @property
    def analytics_aggregation_dimensions(self) -> list[str]:
        """Get default aggregation dimensions."""
        default = ["country_code", "use_of_proceeds", "certification"]
        return self._config.get("analytics", {}).get("aggregation_dimensions", default)

    # =========================================================================
    # OUTPUT CONFIGURATION
    # =========================================================================

    @property
    def output_portfolio_summary(self) -> str:
        """Get filename for portfolio summary output."""
        default = "portfolio_summary.csv"
        return self._config.get("output", {}).get("portfolio_summary", default)

    @property
    def output_data_coverage_report(self) -> str:
        """Get filename for data coverage report output."""
        default = "data_coverage_report.csv"
        return self._config.get("output", {}).get("data_coverage_report", default)

    @property
    def output_validation_report(self) -> str:
        """Get filename for validation report output."""
        default = "validation_report.csv"
        return self._config.get("output", {}).get("validation_report", default)

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key path.

        Supports dot notation for nested keys (e.g., 'paths.raw_data').

        Parameters:
        -----------
        key : str
            Configuration key (supports dot notation)
        default : Any
            Default value if key not found

        Returns:
        --------
        Any
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default


def load_config(config_path: str | Path | None = None) -> Config:
    """
    Load configuration from YAML file.

    Parameters:
    -----------
    config_path : str or Path, optional
        Path to configuration YAML file.
        If None, looks for 'config.yaml' in repository root.
        If file doesn't exist, returns Config with all defaults.

    Returns:
    --------
    Config
        Configuration object with validated settings

    Raises:
    -------
    ConfigurationError
        If configuration file is malformed or invalid
    """
    # Determine config file path
    if config_path is None:
        # Look for config.yaml in repository root (relative to this file)
        repo_root = Path(__file__).parent.parent
        config_path = repo_root / "config.yaml"
    else:
        config_path = Path(config_path)

    # If config file doesn't exist, use defaults
    if not config_path.exists():
        warnings.warn(
            f"Configuration file not found: {config_path}. Using defaults.",
            stacklevel=2,
        )
        return Config()

    # Load YAML file
    try:
        with open(config_path, encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Failed to parse YAML configuration: {e}") from e
    except Exception as e:
        raise ConfigurationError(f"Failed to read configuration file: {e}") from e

    # Validate that we got a dictionary
    if config_dict is None:
        warnings.warn(
            f"Configuration file is empty: {config_path}. Using defaults.",
            stacklevel=2,
        )
        return Config()

    if not isinstance(config_dict, dict):
        raise ConfigurationError(
            f"Configuration must be a YAML dictionary, got {type(config_dict)}"
        )

    # Validate required top-level sections (optional, just for helpful errors)
    expected_sections = ["paths", "schema", "normalization", "map", "analytics", "output"]
    missing_sections = [s for s in expected_sections if s not in config_dict]
    if missing_sections:
        warnings.warn(
            f"Configuration is missing sections: {missing_sections}. "
            "Using defaults for missing sections.",
            stacklevel=2,
        )

    return Config(config_dict)


def validate_config(config: Config) -> tuple[bool, list[str]]:
    """
    Validate configuration for completeness and correctness.

    Parameters:
    -----------
    config : Config
        Configuration object to validate

    Returns:
    --------
    tuple[bool, list[str]]
        (is_valid, list_of_errors)
        is_valid: True if configuration is valid
        list_of_errors: List of validation errors (empty if valid)
    """
    errors = []

    # Validate required columns are not empty
    if not config.required_columns:
        errors.append("Configuration must specify at least one required column")

    # Validate that required columns are also in dtypes
    for col in config.required_columns:
        if col not in config.dtypes:
            errors.append(f"Required column '{col}' is missing from dtypes configuration")

    # Validate analytics top_n is positive
    if config.analytics_top_n <= 0:
        errors.append(f"analytics.top_n must be positive, got {config.analytics_top_n}")

    # Validate coverage threshold is between 0 and 100
    threshold = config.analytics_coverage_threshold
    if threshold < 0 or threshold > 100:
        errors.append(f"analytics.coverage_threshold must be between 0 and 100, got {threshold}")

    # Validate map figsize has 2 elements
    figsize = config.map_figsize
    if not isinstance(figsize, tuple) or len(figsize) != 2:
        errors.append(f"map.style.figsize must be a list of 2 elements, got {figsize}")

    # Validate map DPI is positive
    if config.map_dpi <= 0:
        errors.append(f"map.style.dpi must be positive, got {config.map_dpi}")

    is_valid = len(errors) == 0
    return is_valid, errors


# Global config instance (lazy loaded)
_global_config: Config | None = None


def get_config(config_path: str | Path | None = None) -> Config:
    """
    Get the global configuration instance.

    This function provides a singleton configuration object that can be
    shared across the application. If a config_path is provided, it will
    reload the configuration from that path.

    Parameters:
    -----------
    config_path : str or Path, optional
        Path to configuration YAML file. If None and config not yet loaded,
        uses default path.

    Returns:
    --------
    Config
        Global configuration object
    """
    global _global_config

    # If config_path is provided, always reload
    if config_path is not None:
        _global_config = load_config(config_path)
        return _global_config

    # If no config loaded yet, load from default path
    if _global_config is None:
        _global_config = load_config()

    return _global_config


def reset_config():
    """Reset the global configuration instance (useful for testing)."""
    global _global_config
    _global_config = None
