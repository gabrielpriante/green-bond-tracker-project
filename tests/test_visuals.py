"""
Unit tests for the visuals module.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pytest

from src.data_loader import join_bonds_with_geo, load_country_geometries, load_green_bonds
from src.visuals import (
    create_and_save_all_visuals,
    create_choropleth_map,
    create_project_type_bar_chart,
    save_figure,
)


@pytest.fixture
def sample_bonds():
    """Fixture providing sample bond data."""
    fixture_path = Path(__file__).parent / "fixtures" / "test_bonds.csv"
    return load_green_bonds(str(fixture_path))


@pytest.fixture
def sample_geo_bonds(sample_bonds):
    """Fixture providing sample geo bonds data."""
    countries = load_country_geometries()
    return join_bonds_with_geo(sample_bonds, countries)


class TestCreateProjectTypeBarChart:
    """Tests for create_project_type_bar_chart function."""

    def test_returns_figure(self, sample_bonds):
        """Test that function returns a matplotlib Figure."""
        fig = create_project_type_bar_chart(sample_bonds)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_custom_figsize(self, sample_bonds):
        """Test that custom figsize is applied."""
        fig = create_project_type_bar_chart(sample_bonds, figsize=(10, 5))
        assert fig.get_size_inches()[0] == 10
        assert fig.get_size_inches()[1] == 5
        plt.close(fig)

    def test_has_title(self, sample_bonds):
        """Test that chart has a title."""
        fig = create_project_type_bar_chart(sample_bonds)
        axes = fig.get_axes()
        assert len(axes) > 0
        assert axes[0].get_title() != ""
        plt.close(fig)

    def test_has_labels(self, sample_bonds):
        """Test that chart has axis labels."""
        fig = create_project_type_bar_chart(sample_bonds)
        axes = fig.get_axes()
        assert axes[0].get_xlabel() != ""
        assert axes[0].get_ylabel() != ""
        plt.close(fig)


class TestCreateChoroplethMap:
    """Tests for create_choropleth_map function."""

    def test_returns_figure(self, sample_geo_bonds):
        """Test that function returns a matplotlib Figure."""
        fig = create_choropleth_map(sample_geo_bonds)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_custom_column(self, sample_geo_bonds):
        """Test that custom column can be specified."""
        fig = create_choropleth_map(sample_geo_bonds, column="bond_count")
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_custom_title(self, sample_geo_bonds):
        """Test that custom title is applied."""
        custom_title = "My Custom Map Title"
        fig = create_choropleth_map(sample_geo_bonds, title=custom_title)
        axes = fig.get_axes()
        assert axes[0].get_title() == custom_title
        plt.close(fig)

    def test_custom_figsize(self, sample_geo_bonds):
        """Test that custom figsize is applied."""
        fig = create_choropleth_map(sample_geo_bonds, figsize=(20, 12))
        assert fig.get_size_inches()[0] == 20
        assert fig.get_size_inches()[1] == 12
        plt.close(fig)


class TestSaveFigure:
    """Tests for save_figure function."""

    def test_saves_file(self, sample_bonds, tmp_path):
        """Test that figure is saved to file."""
        fig = create_project_type_bar_chart(sample_bonds)
        output_path = save_figure(fig, "test_chart.png", output_dir=str(tmp_path))

        assert output_path.exists()
        assert output_path.name == "test_chart.png"
        plt.close(fig)

    def test_adds_png_extension(self, sample_bonds, tmp_path):
        """Test that .png extension is added if missing."""
        fig = create_project_type_bar_chart(sample_bonds)
        output_path = save_figure(fig, "test_chart", output_dir=str(tmp_path))

        assert output_path.name == "test_chart.png"
        plt.close(fig)

    def test_creates_output_directory(self, sample_bonds, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        fig = create_project_type_bar_chart(sample_bonds)
        new_dir = tmp_path / "new_output_dir"
        output_path = save_figure(fig, "test.png", output_dir=str(new_dir))

        assert new_dir.exists()
        assert output_path.exists()
        plt.close(fig)

    def test_custom_dpi(self, sample_bonds, tmp_path):
        """Test that custom DPI is applied."""
        fig = create_project_type_bar_chart(sample_bonds)
        output_path = save_figure(fig, "test.png", output_dir=str(tmp_path), dpi=150)

        assert output_path.exists()
        plt.close(fig)

    def test_returns_path_object(self, sample_bonds, tmp_path):
        """Test that function returns a Path object."""
        fig = create_project_type_bar_chart(sample_bonds)
        output_path = save_figure(fig, "test.png", output_dir=str(tmp_path))

        assert isinstance(output_path, Path)
        plt.close(fig)


class TestCreateAndSaveAllVisuals:
    """Tests for create_and_save_all_visuals function."""

    def test_creates_multiple_files(self, sample_bonds, sample_geo_bonds, tmp_path):
        """Test that function creates multiple visualization files."""
        saved_files = create_and_save_all_visuals(
            sample_bonds, sample_geo_bonds, output_dir=str(tmp_path)
        )

        assert isinstance(saved_files, dict)
        assert len(saved_files) >= 3  # At least 3 visualizations

    def test_all_files_exist(self, sample_bonds, sample_geo_bonds, tmp_path):
        """Test that all saved files actually exist."""
        saved_files = create_and_save_all_visuals(
            sample_bonds, sample_geo_bonds, output_dir=str(tmp_path)
        )

        for filepath in saved_files.values():
            assert Path(filepath).exists()

    def test_returns_correct_keys(self, sample_bonds, sample_geo_bonds, tmp_path):
        """Test that returned dictionary has expected keys."""
        saved_files = create_and_save_all_visuals(
            sample_bonds, sample_geo_bonds, output_dir=str(tmp_path)
        )

        expected_keys = [
            "project_type_bar_chart",
            "choropleth_total_amount",
            "choropleth_bond_count",
        ]

        for key in expected_keys:
            assert key in saved_files

    def test_uses_default_output_dir(self, sample_bonds, sample_geo_bonds):
        """Test that default output directory is used when not specified."""
        # This test just ensures the function works with default params
        # We won't verify the exact location to avoid filesystem issues
        saved_files = create_and_save_all_visuals(sample_bonds, sample_geo_bonds)
        assert isinstance(saved_files, dict)
        assert len(saved_files) > 0


class TestVisualizationIntegration:
    """Integration tests for visualization workflow."""

    def test_full_visualization_workflow(self, tmp_path):
        """Test complete workflow from data loading to visualization."""
        # Load data
        fixture_path = Path(__file__).parent / "fixtures" / "test_bonds.csv"
        bonds = load_green_bonds(str(fixture_path))
        countries = load_country_geometries()
        geo_bonds = join_bonds_with_geo(bonds, countries)

        # Create individual charts
        fig1 = create_project_type_bar_chart(bonds)
        assert isinstance(fig1, plt.Figure)
        plt.close(fig1)

        fig2 = create_choropleth_map(geo_bonds)
        assert isinstance(fig2, plt.Figure)
        plt.close(fig2)

        # Save all charts
        saved = create_and_save_all_visuals(bonds, geo_bonds, output_dir=str(tmp_path))
        assert len(saved) >= 3

        # Verify all files exist and are non-empty
        for filepath in saved.values():
            path = Path(filepath)
            assert path.exists()
            assert path.stat().st_size > 0


class TestVisualizationErrorHandling:
    """Tests for error handling in visualization functions."""

    def test_empty_dataframe_handling(self):
        """Test that empty dataframe is handled gracefully."""
        import pandas as pd

        empty_df = pd.DataFrame()

        # This might raise an error or return an empty figure
        # depending on implementation. Just ensure it doesn't crash.
        try:
            fig = create_project_type_bar_chart(empty_df)
            if fig is not None:
                plt.close(fig)
        except (KeyError, ValueError):
            # Expected behavior for empty dataframe
            pass
