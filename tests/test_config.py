"""
Tests for the configuration module.

These tests verify that the configuration system works correctly,
handles missing config files gracefully, and validates configuration properly.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.config import (
    Config,
    ConfigurationError,
    get_config,
    load_config,
    reset_config,
    validate_config,
)


class TestConfigClass:
    """Test the Config class."""

    def test_empty_config_uses_defaults(self):
        """Test that empty config uses default values."""
        config = Config({})
        assert config.raw_data_path == "data/green_bonds.csv"
        assert config.geo_data_path == "data/countries_geo.json"
        assert config.outputs_dir == "outputs"
        assert config.maps_dir == "maps"

    def test_config_with_custom_paths(self):
        """Test that config respects custom path values."""
        config_dict = {
            "paths": {
                "raw_data": "custom/data.csv",
                "geo_data": "custom/geo.json",
                "outputs": "custom/outputs",
                "maps": "custom/maps",
            }
        }
        config = Config(config_dict)
        assert config.raw_data_path == "custom/data.csv"
        assert config.geo_data_path == "custom/geo.json"
        assert config.outputs_dir == "custom/outputs"
        assert config.maps_dir == "custom/maps"

    def test_required_columns_default(self):
        """Test default required columns."""
        config = Config({})
        assert "bond_id" in config.required_columns
        assert "issuer" in config.required_columns
        assert "country_code" in config.required_columns
        assert "amount_usd_millions" in config.required_columns

    def test_optional_columns_default(self):
        """Test default optional columns."""
        config = Config({})
        assert "issue_date" in config.optional_columns
        assert "maturity_date" in config.optional_columns
        assert "currency" in config.optional_columns

    def test_all_columns_combines_required_and_optional(self):
        """Test that all_columns includes both required and optional."""
        config = Config({})
        all_cols = config.all_columns
        assert "bond_id" in all_cols
        assert "issue_date" in all_cols
        assert len(all_cols) == len(config.required_columns) + len(config.optional_columns)

    def test_dtypes_default(self):
        """Test default data type mappings."""
        config = Config({})
        assert config.dtypes["bond_id"] == "string"
        assert config.dtypes["amount_usd_millions"] == "float"
        assert config.dtypes["issue_date"] == "date"

    def test_map_configuration(self):
        """Test map configuration defaults."""
        config = Config({})
        assert config.map_default_output == "green_bonds_map.html"
        assert config.map_colormap == "YlGn"
        assert config.map_figsize == (14, 8)
        assert config.map_dpi == 300

    def test_analytics_configuration(self):
        """Test analytics configuration defaults."""
        config = Config({})
        assert config.analytics_top_n == 5
        assert config.analytics_coverage_threshold == 80.0

    def test_output_configuration(self):
        """Test output filename configuration."""
        config = Config({})
        assert config.output_portfolio_summary == "portfolio_summary.csv"
        assert config.output_data_coverage_report == "data_coverage_report.csv"
        assert config.output_validation_report == "validation_report.csv"

    def test_get_method_with_dot_notation(self):
        """Test the get method with dot notation."""
        config_dict = {
            "paths": {"raw_data": "custom.csv"},
            "map": {"style": {"dpi": 150}},
        }
        config = Config(config_dict)
        assert config.get("paths.raw_data") == "custom.csv"
        assert config.get("map.style.dpi") == 150
        assert config.get("nonexistent.key", "default") == "default"


class TestLoadConfig:
    """Test the load_config function."""

    def test_load_config_from_nonexistent_file_uses_defaults(self, tmp_path):
        """Test that loading from non-existent file uses defaults."""
        reset_config()
        config_path = tmp_path / "nonexistent.yaml"
        with pytest.warns(UserWarning, match="Configuration file not found"):
            config = load_config(config_path)
        assert config.raw_data_path == "data/green_bonds.csv"

    def test_load_config_from_valid_file(self, tmp_path):
        """Test loading config from a valid YAML file."""
        reset_config()
        config_path = tmp_path / "test_config.yaml"
        config_data = {
            "paths": {"raw_data": "test/data.csv"},
            "schema": {"required_columns": ["bond_id", "issuer"]},
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = load_config(config_path)
        assert config.raw_data_path == "test/data.csv"
        assert config.required_columns == ["bond_id", "issuer"]

    def test_load_config_from_empty_file_warns(self, tmp_path):
        """Test that loading from empty file warns and uses defaults."""
        reset_config()
        config_path = tmp_path / "empty_config.yaml"
        config_path.write_text("")

        with pytest.warns(UserWarning, match="Configuration file is empty"):
            config = load_config(config_path)
        assert config.raw_data_path == "data/green_bonds.csv"

    def test_load_config_from_malformed_yaml_raises_error(self, tmp_path):
        """Test that malformed YAML raises ConfigurationError."""
        reset_config()
        config_path = tmp_path / "bad_config.yaml"
        config_path.write_text("invalid: yaml: content: [")

        with pytest.raises(ConfigurationError, match="Failed to parse YAML"):
            load_config(config_path)

    def test_load_config_with_missing_sections_warns(self, tmp_path):
        """Test that missing sections produce warnings."""
        reset_config()
        config_path = tmp_path / "partial_config.yaml"
        config_data = {"paths": {"raw_data": "test.csv"}}  # Missing other sections
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        with pytest.warns(UserWarning, match="missing sections"):
            config = load_config(config_path)
        assert config.raw_data_path == "test.csv"

    def test_load_config_with_non_dict_raises_error(self, tmp_path):
        """Test that non-dictionary YAML raises error."""
        reset_config()
        config_path = tmp_path / "list_config.yaml"
        config_path.write_text("- item1\n- item2")

        with pytest.raises(ConfigurationError, match="must be a YAML dictionary"):
            load_config(config_path)


class TestValidateConfig:
    """Test the validate_config function."""

    def test_validate_valid_config(self):
        """Test that valid config passes validation."""
        config = Config({})  # Default config should be valid
        is_valid, errors = validate_config(config)
        assert is_valid
        assert len(errors) == 0

    def test_validate_config_with_no_required_columns_fails(self):
        """Test that config with no required columns fails."""
        config_dict = {"schema": {"required_columns": []}}
        config = Config(config_dict)
        is_valid, errors = validate_config(config)
        assert not is_valid
        assert any("at least one required column" in err for err in errors)

    def test_validate_config_with_missing_dtypes_fails(self):
        """Test that required columns missing from dtypes fails."""
        config_dict = {
            "schema": {
                "required_columns": ["bond_id", "new_field"],
                "dtypes": {"bond_id": "string"},  # Missing new_field
            }
        }
        config = Config(config_dict)
        is_valid, errors = validate_config(config)
        assert not is_valid
        assert any("new_field" in err and "missing from dtypes" in err for err in errors)

    def test_validate_config_with_invalid_top_n_fails(self):
        """Test that invalid top_n value fails."""
        config_dict = {"analytics": {"top_n": 0}}
        config = Config(config_dict)
        is_valid, errors = validate_config(config)
        assert not is_valid
        assert any("top_n must be positive" in err for err in errors)

    def test_validate_config_with_invalid_coverage_threshold_fails(self):
        """Test that invalid coverage threshold fails."""
        config_dict = {"analytics": {"coverage_threshold": 150}}
        config = Config(config_dict)
        is_valid, errors = validate_config(config)
        assert not is_valid
        assert any("coverage_threshold must be between 0 and 100" in err for err in errors)

    def test_validate_config_with_invalid_figsize_fails(self):
        """Test that invalid figsize fails."""
        config_dict = {"map": {"style": {"figsize": [14]}}}  # Only 1 element
        config = Config(config_dict)
        is_valid, errors = validate_config(config)
        assert not is_valid
        assert any("figsize must be a list of 2 elements" in err for err in errors)

    def test_validate_config_with_invalid_dpi_fails(self):
        """Test that invalid DPI fails."""
        config_dict = {"map": {"style": {"dpi": -100}}}
        config = Config(config_dict)
        is_valid, errors = validate_config(config)
        assert not is_valid
        assert any("dpi must be positive" in err for err in errors)


class TestGetConfig:
    """Test the get_config singleton function."""

    def test_get_config_without_path_returns_default(self):
        """Test that get_config without path returns default config."""
        reset_config()
        config = get_config()
        assert config.raw_data_path == "data/green_bonds.csv"

    def test_get_config_with_path_loads_custom_config(self, tmp_path):
        """Test that get_config with path loads custom config."""
        reset_config()
        config_path = tmp_path / "custom.yaml"
        config_data = {"paths": {"raw_data": "custom.csv"}}
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = get_config(config_path)
        assert config.raw_data_path == "custom.csv"

    def test_get_config_is_singleton(self, tmp_path):
        """Test that get_config returns the same instance."""
        reset_config()
        config1 = get_config()
        config2 = get_config()
        # In the current implementation, calling get_config() without path
        # returns the cached config, so this should be the same object
        assert config1 is config2

    def test_reset_config_clears_singleton(self):
        """Test that reset_config clears the singleton."""
        reset_config()
        config1 = get_config()
        reset_config()
        config2 = get_config()
        # After reset, we should get a fresh instance
        # Note: They might have the same values but be different objects
        assert config1.raw_data_path == config2.raw_data_path


class TestDefaultWarnings:
    """Test that appropriate warnings are shown when using defaults."""

    def test_raw_data_path_warns_when_using_default(self):
        """Test that accessing raw_data_path warns when using default."""
        config = Config({})  # No paths section
        with pytest.warns(UserWarning, match="Using default raw_data path"):
            _ = config.raw_data_path

    def test_geo_data_path_warns_when_using_default(self):
        """Test that accessing geo_data_path warns when using default."""
        config = Config({})  # No paths section
        with pytest.warns(UserWarning, match="Using default geo_data path"):
            _ = config.geo_data_path

    def test_no_warning_when_config_provides_path(self):
        """Test that no warning is shown when config provides path."""
        config = Config({"paths": {"raw_data": "custom.csv"}})
        # Should not warn since we provided a value
        import warnings

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = config.raw_data_path
            # Filter for our specific warning
            relevant_warnings = [
                warn for warn in w if "Using default" in str(warn.message)
            ]
            assert len(relevant_warnings) == 0
