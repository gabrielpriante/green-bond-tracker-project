"""
Tests for CLI commands - smoke tests to ensure basic functionality.

These tests verify that the CLI commands can be invoked without crashing.
"""

import re
import subprocess
import sys

import src


def strip_ansi(text):
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


class TestCLISmokeTests:
    """Smoke tests for CLI commands."""

    def test_gbt_help_command(self):
        """Test that gbt --help runs successfully."""
        result = subprocess.run(
            ["gbt", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        output = strip_ansi(result.stdout)
        assert "validate" in output
        assert "summary" in output
        assert "map" in output

    def test_gbt_version_flag(self):
        """Test that gbt --version runs successfully."""
        result = subprocess.run(
            ["gbt", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert src.__version__ in result.stdout

    def test_validate_help_command(self):
        """Test that gbt validate --help runs successfully."""
        result = subprocess.run(
            ["gbt", "validate", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        output = strip_ansi(result.stdout)
        assert "--input" in output

    def test_summary_help_command(self):
        """Test that gbt summary --help runs successfully."""
        result = subprocess.run(
            ["gbt", "summary", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        output = strip_ansi(result.stdout)
        assert "--input" in output
        assert "--output-dir" in output

    def test_map_help_command(self):
        """Test that gbt map --help runs successfully."""
        result = subprocess.run(
            ["gbt", "map", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        output = strip_ansi(result.stdout)
        assert "--input" in output
        assert "--output" in output

    def test_version_command(self):
        """Test that gbt version runs successfully."""
        result = subprocess.run(
            ["gbt", "version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert src.__version__ in result.stdout

    def test_package_imports(self):
        """Test that the package can be imported."""
        result = subprocess.run(
            [sys.executable, "-c", "import src; print(src.__version__)"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert src.__version__ in result.stdout

    def test_greenbond_alias_works(self):
        """Test that greenbond alias still works (backward compatibility)."""
        # Test with --help - should not show deprecation for just help
        result = subprocess.run(
            ["greenbond", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Test with actual command - should show deprecation
        result = subprocess.run(
            ["greenbond", "version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        output = strip_ansi(result.stdout)
        # Should show deprecation warning when running commands
        assert "deprecated" in output.lower()


class TestCLIValidateCommand:
    """Integration tests for validate command."""

    def test_validate_command_runs(self):
        """Test that gbt validate runs on sample data."""
        result = subprocess.run(
            ["gbt", "validate", "--input", "data/green_bonds.csv"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Loaded" in result.stdout or "records" in result.stdout


class TestCLISummaryCommand:
    """Integration tests for summary command."""

    def test_summary_command_runs(self):
        """Test that gbt summary runs on sample data."""
        result = subprocess.run(
            ["gbt", "summary", "--input", "data/green_bonds.csv"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Portfolio" in result.stdout or "Loaded" in result.stdout

    def test_summary_with_output_dir(self, tmp_path):
        """Test that gbt summary creates output files."""
        output_dir = tmp_path / "test_outputs"
        result = subprocess.run(
            [
                "gbt",
                "summary",
                "--input",
                "data/green_bonds.csv",
                "--output-dir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert output_dir.exists()
        assert (output_dir / "portfolio_summary.csv").exists()
