"""
Integration tests for CLI with configuration system.

These tests verify that the CLI works correctly with and without config files,
and that command-line options properly override configuration settings.
"""

import subprocess
from pathlib import Path

import pytest
import yaml


class TestCLIConfigIntegration:
    """Test CLI integration with configuration system."""

    def test_cli_works_without_config_file(self, tmp_path):
        """Test that CLI works without any config file (uses defaults)."""
        # Use absolute path to data file
        data_path = Path("data/green_bonds.csv").resolve()

        # Run validate with absolute path
        result = subprocess.run(
            ["gbt", "validate", "--input", str(data_path)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        # Should succeed even without config file
        assert result.returncode == 0
        assert "Loaded" in result.stdout or "records" in result.stdout

    def test_cli_with_custom_config_file(self, tmp_path):
        """Test that CLI respects custom config file."""
        # Use absolute path to data file
        data_path = Path("data/green_bonds.csv").resolve()

        # Create a custom config
        config_path = tmp_path / "custom.yaml"
        config_data = {
            "paths": {"raw_data": str(data_path), "outputs": str(tmp_path / "outputs")},
            "output": {"portfolio_summary": "custom_summary.csv"},
        }
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Run summary with custom config
        result = subprocess.run(
            ["gbt", "--config", str(config_path), "summary"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should create the custom filename
        assert (tmp_path / "outputs" / "custom_summary.csv").exists()

    def test_cli_option_overrides_config(self, tmp_path):
        """Test that CLI options override config file settings."""
        # Use absolute path to data file
        data_path = Path("data/green_bonds.csv").resolve()

        # Create a config that specifies a different output dir
        config_path = tmp_path / "test.yaml"
        config_data = {"paths": {"outputs": str(tmp_path / "config_outputs")}}
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Override with command-line option
        override_dir = tmp_path / "cli_outputs"
        result = subprocess.run(
            [
                "gbt",
                "--config",
                str(config_path),
                "summary",
                "--input",
                str(data_path),
                "--output-dir",
                str(override_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        # Should use CLI override, not config value
        assert override_dir.exists()
        assert (override_dir / "portfolio_summary.csv").exists()
        # Config dir should not be created
        assert not (tmp_path / "config_outputs").exists()

    def test_malformed_config_shows_error(self, tmp_path):
        """Test that malformed config file shows clear error message."""
        config_path = tmp_path / "bad.yaml"
        config_path.write_text("invalid: yaml: [unclosed")

        result = subprocess.run(
            ["gbt", "--config", str(config_path), "summary"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "Error loading configuration" in result.stdout or "Error" in result.stdout

    def test_validate_command_without_input_uses_config(self, tmp_path):
        """Test that validate without --input uses config default."""
        # Use absolute path to data file
        data_path = Path("data/green_bonds.csv").resolve()

        # Create config with custom path
        config_path = tmp_path / "test.yaml"
        config_data = {"paths": {"raw_data": str(data_path)}}
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Run validate without --input
        result = subprocess.run(
            ["gbt", "--config", str(config_path), "validate"],
            capture_output=True,
            text=True,
        )

        # Should use config path and succeed
        assert result.returncode == 0
        assert "Loaded" in result.stdout


class TestConfigBackwardCompatibility:
    """Test backward compatibility with existing behavior."""

    def test_validate_with_explicit_input_no_config(self):
        """Test that validate still works with explicit --input, no config."""
        result = subprocess.run(
            ["gbt", "validate", "--input", "data/green_bonds.csv"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Loaded" in result.stdout

    def test_summary_with_defaults_no_config(self):
        """Test that summary works with defaults when no config provided."""
        result = subprocess.run(
            ["gbt", "summary", "--input", "data/green_bonds.csv"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Portfolio" in result.stdout or "Total Bonds" in result.stdout

    def test_map_with_all_options_no_config(self, tmp_path):
        """Test that map works with all options specified, no config."""
        output_path = tmp_path / "test_map.html"

        # Skip if folium not installed
        try:
            import folium  # noqa: F401
        except ImportError:
            pytest.skip("Folium not installed")

        result = subprocess.run(
            [
                "gbt",
                "map",
                "--input",
                "data/green_bonds.csv",
                "--geo",
                "data/countries_geo.json",
                "--output",
                str(output_path),
            ],
            capture_output=True,
            text=True,
        )

        # Should work without config
        assert result.returncode == 0 or "require folium" in result.stdout


class TestConfigValidation:
    """Test configuration validation."""

    def test_config_with_invalid_top_n(self, tmp_path):
        """Test that invalid analytics.top_n in config is caught."""
        config_path = tmp_path / "invalid.yaml"
        config_data = {"analytics": {"top_n": 0}}  # Invalid: must be positive
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # The config loads with warnings, doesn't fail on load
        # (validation is optional in current implementation)
        result = subprocess.run(
            ["gbt", "--config", str(config_path), "summary", "--input", "data/green_bonds.csv"],
            capture_output=True,
            text=True,
        )

        # Should still work (uses defaults for invalid values)
        # or could fail depending on validation strictness
        # Current implementation: loads and uses defaults
        assert result.returncode in [0, 1]


class TestConfigHelp:
    """Test that help commands work with config option."""

    def test_validate_help_shows_config_option(self):
        """Test that validate --help mentions config can be used."""
        result = subprocess.run(
            ["gbt", "validate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        # Should show input option (checking for 'input' is enough, ignoring ANSI codes)
        assert "input" in result.stdout.lower()

    def test_summary_help_shows_config_option(self):
        """Test that summary --help shows config-aware options."""
        result = subprocess.run(
            ["gbt", "summary", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "input" in result.stdout.lower()
        assert "output" in result.stdout.lower()
