"""
Tests for CLI commands - smoke tests to ensure basic functionality.

These tests verify that the CLI commands can be invoked without crashing.
"""

import re
import subprocess
import sys


def strip_ansi(text):
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


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
        assert "--outdir" in output

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
        assert "--out" in output

    def test_version_command(self):
        """Test that gbt version runs successfully."""
        result = subprocess.run(
            ["gbt", "version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "0.2.0" in result.stdout

    def test_package_imports(self):
        """Test that the package can be imported."""
        result = subprocess.run(
            [sys.executable, "-c", "import src; print(src.__version__)"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "0.2.0" in result.stdout
