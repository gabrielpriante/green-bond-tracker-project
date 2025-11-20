"""
Green Bond Tracker - Visualization Module

This module provides simple, educational visualization functions for green bond data.
All functions are designed to be beginner-friendly with clear explanations.

Note: This is an educational project and should not be used for investment advice.
"""

import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import Optional, Tuple


def create_project_type_bar_chart(bonds_df: pd.DataFrame, 
                                   figsize: Tuple[int, int] = (12, 6)) -> plt.Figure:
    """
    Create a bar chart showing the count of bonds by project type (use of proceeds).
    
    This visualization helps you see which types of green projects receive the most
    bond funding. For example, you might see more bonds for Renewable Energy
    compared to Sustainable Agriculture.
    
    Parameters:
    -----------
    bonds_df : pd.DataFrame
        DataFrame containing green bond data with 'use_of_proceeds' column
    figsize : tuple, optional
        Size of the figure (width, height) in inches. Default is (12, 6)
    
    Returns:
    --------
    plt.Figure
        Matplotlib figure object containing the bar chart
    
    Example:
    --------
    >>> bonds = load_green_bonds()
    >>> fig = create_project_type_bar_chart(bonds)
    >>> plt.show()
    """
    # Count how many bonds exist for each project type
    project_counts = bonds_df['use_of_proceeds'].value_counts().sort_values(ascending=True)
    
    # Create a new figure with specified size
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create horizontal bar chart (easier to read when labels are long)
    project_counts.plot(
        kind='barh',
        ax=ax,
        color='#2E7D32',  # A nice green color appropriate for "green" bonds
        edgecolor='black',
        linewidth=0.5
    )
    
    # Add labels and title
    ax.set_xlabel('Number of Bonds', fontsize=12)
    ax.set_ylabel('Project Type', fontsize=12)
    ax.set_title('Green Bond Distribution by Project Type', fontsize=14, fontweight='bold')
    
    # Add a grid to make it easier to read values
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Make the layout tight so labels don't get cut off
    plt.tight_layout()
    
    return fig


def create_choropleth_map(geo_bonds_df: gpd.GeoDataFrame,
                         column: str = 'total_amount_usd_millions',
                         figsize: Tuple[int, int] = (16, 10),
                         title: Optional[str] = None) -> plt.Figure:
    """
    Create a choropleth map showing green bond data by country.
    
    A choropleth map uses different colors to show values across geographic regions.
    Darker colors typically indicate higher values. This makes it easy to see which
    countries have more green bond activity at a glance.
    
    Parameters:
    -----------
    geo_bonds_df : gpd.GeoDataFrame
        GeoDataFrame with bond data joined to country geometries
    column : str, optional
        Column name to visualize. Default is 'total_amount_usd_millions'
    figsize : tuple, optional
        Size of the figure (width, height) in inches. Default is (16, 10)
    title : str, optional
        Custom title for the map. If None, a default title is generated
    
    Returns:
    --------
    plt.Figure
        Matplotlib figure object containing the choropleth map
    
    Example:
    --------
    >>> bonds = load_green_bonds()
    >>> countries = load_country_geometries()
    >>> geo_bonds = join_bonds_with_geo(bonds, countries)
    >>> fig = create_choropleth_map(geo_bonds)
    >>> plt.show()
    """
    # Create a new figure with specified size
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the choropleth map
    # - 'column' determines what data to show with colors
    # - 'cmap' is the color scheme (YlGn = Yellow to Green, fitting for green bonds!)
    # - 'legend' adds a color bar showing what the colors mean
    # - 'edgecolor' adds black borders around countries for clarity
    geo_bonds_df.plot(
        column=column,
        ax=ax,
        legend=True,
        cmap='YlGn',  # Yellow-Green color scheme
        edgecolor='black',
        linewidth=0.5,
        missing_kwds={'color': 'lightgrey', 'label': 'No Data'}  # Countries with no bonds
    )
    
    # Set the title
    if title is None:
        # Create a readable title from the column name
        title = f'Green Bonds by Country: {column.replace("_", " ").title()}'
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Remove axis labels (latitude/longitude aren't needed here)
    ax.set_xlabel('')
    ax.set_ylabel('')
    
    # Remove tick marks for cleaner appearance
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Make the layout tight
    plt.tight_layout()
    
    return fig


def save_figure(fig: plt.Figure, 
                filename: str,
                output_dir: Optional[str] = None,
                dpi: int = 300) -> Path:
    """
    Save a matplotlib figure to the outputs directory.
    
    This function saves your charts as PNG image files so you can use them in
    reports, presentations, or share them with others. Higher DPI (dots per inch)
    means better quality but larger file sizes.
    
    Parameters:
    -----------
    fig : plt.Figure
        Matplotlib figure object to save
    filename : str
        Name for the output file (e.g., 'project_types.png')
        The '.png' extension will be added if not present
    output_dir : str, optional
        Directory to save the file. If None, uses the default 'outputs/' folder
    dpi : int, optional
        Resolution in dots per inch. Default is 300 (high quality)
        Use 150 for web images, 300+ for print quality
    
    Returns:
    --------
    Path
        Path object pointing to the saved file
    
    Example:
    --------
    >>> fig = create_project_type_bar_chart(bonds)
    >>> filepath = save_figure(fig, 'project_types.png')
    >>> print(f"Chart saved to: {filepath}")
    """
    # Determine the output directory
    if output_dir is None:
        # Use default outputs folder in project root
        base_path = Path(__file__).parent.parent
        output_dir = base_path / "outputs"
    else:
        output_dir = Path(output_dir)
    
    # Create the directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure filename has .png extension
    if not filename.endswith('.png'):
        filename = filename + '.png'
    
    # Create full file path
    filepath = output_dir / filename
    
    # Save the figure
    # bbox_inches='tight' ensures nothing gets cut off
    fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
    
    return filepath


def create_and_save_all_visuals(bonds_df: pd.DataFrame,
                                geo_bonds_df: gpd.GeoDataFrame,
                                output_dir: Optional[str] = None) -> dict:
    """
    Create all standard visualizations and save them to the outputs directory.
    
    This is a convenience function that generates all the key charts at once.
    It's useful when you want to quickly generate a complete set of visuals
    for your analysis.
    
    Parameters:
    -----------
    bonds_df : pd.DataFrame
        DataFrame containing green bond data
    geo_bonds_df : gpd.GeoDataFrame
        GeoDataFrame with bond data joined to country geometries
    output_dir : str, optional
        Directory to save files. If None, uses the default 'outputs/' folder
    
    Returns:
    --------
    dict
        Dictionary mapping chart names to their file paths
    
    Example:
    --------
    >>> bonds = load_green_bonds()
    >>> countries = load_country_geometries()
    >>> geo_bonds = join_bonds_with_geo(bonds, countries)
    >>> saved_files = create_and_save_all_visuals(bonds, geo_bonds)
    >>> for name, path in saved_files.items():
    ...     print(f"{name}: {path}")
    """
    saved_files = {}
    
    # Create and save project type bar chart
    print("Creating project type bar chart...")
    fig1 = create_project_type_bar_chart(bonds_df)
    path1 = save_figure(fig1, 'project_type_distribution.png', output_dir)
    saved_files['project_type_bar_chart'] = path1
    plt.close(fig1)  # Close to free memory
    
    # Create and save choropleth map (total amount)
    print("Creating choropleth map (total amount)...")
    fig2 = create_choropleth_map(
        geo_bonds_df,
        column='total_amount_usd_millions',
        title='Green Bond Total Amount by Country (USD Millions)'
    )
    path2 = save_figure(fig2, 'green_bonds_choropleth_amount.png', output_dir)
    saved_files['choropleth_total_amount'] = path2
    plt.close(fig2)
    
    # Create and save choropleth map (bond count)
    print("Creating choropleth map (bond count)...")
    fig3 = create_choropleth_map(
        geo_bonds_df,
        column='bond_count',
        title='Number of Green Bonds by Country'
    )
    path3 = save_figure(fig3, 'green_bonds_choropleth_count.png', output_dir)
    saved_files['choropleth_bond_count'] = path3
    plt.close(fig3)
    
    print(f"\nAll visualizations saved to: {output_dir or 'outputs/'}")
    return saved_files
