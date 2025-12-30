"""
Green Bond Tracker - Interactive Visualization Module

This module provides interactive map visualizations using Folium.
It is an optional feature that requires the 'interactive' extra to be installed.

Note: This is an educational project and should not be used for investment advice.
"""

from pathlib import Path
from typing import Optional

import geopandas as gpd

try:
    import folium
    from folium import plugins

    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False


def create_interactive_choropleth_map(
    geo_bonds_df: gpd.GeoDataFrame,
    column: str = "total_amount_usd_millions",
    output_path: Optional[str] = None,
    title: Optional[str] = None,
) -> "folium.Map":
    """
    Create an interactive choropleth map showing green bond data by country.

    This function creates a Folium-based interactive map that users can pan,
    zoom, and hover over to see detailed information about green bonds in
    each country.

    Parameters
    ----------
    geo_bonds_df : gpd.GeoDataFrame
        GeoDataFrame with bond data joined to country geometries
    column : str, optional
        Column name to visualize. Default is 'total_amount_usd_millions'
    output_path : str, optional
        Path to save the HTML map file. If None, map is not saved to disk
    title : str, optional
        Custom title for the map. If None, a default title is generated

    Returns
    -------
    folium.Map
        Folium map object that can be displayed in Jupyter or saved to HTML

    Raises
    ------
    ImportError
        If folium is not installed

    Examples
    --------
    >>> from src.data_loader import load_green_bonds, load_country_geometries, join_bonds_with_geo
    >>> from src.interactive import create_interactive_choropleth_map
    >>> bonds = load_green_bonds()
    >>> countries = load_country_geometries()
    >>> geo_bonds = join_bonds_with_geo(bonds, countries)
    >>> map_obj = create_interactive_choropleth_map(geo_bonds, output_path='map.html')
    >>> # In Jupyter: display(map_obj)
    >>> # Or open map.html in a web browser

    Notes
    -----
    - Requires the 'interactive' extra: pip install 'green-bond-tracker[interactive]'
    - The map includes a legend, tooltips, and zoom controls
    - Countries with no bond data are shown in grey
    """
    if not FOLIUM_AVAILABLE:
        raise ImportError(
            "Folium is required for interactive maps. "
            "Install it with: pip install 'green-bond-tracker[interactive]'"
        )

    # Convert to GeoJSON format (required for folium)
    # Use EPSG:4326 (WGS84) which is required by Folium
    geo_bonds_wgs84 = geo_bonds_df.to_crs(epsg=4326)

    # Create base map centered on world
    m = folium.Map(
        location=[20, 0],  # Center of the world
        zoom_start=2,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # Set title
    if title is None:
        title = f"Green Bonds by Country: {column.replace('_', ' ').title()}"

    # Add title to map
    title_html = f"""
    <div style="position: fixed;
                top: 10px;
                left: 50px;
                width: 500px;
                height: 60px;
                z-index: 9999;
                font-size: 16px;
                font-weight: bold;
                background-color: white;
                border: 2px solid grey;
                border-radius: 5px;
                padding: 10px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
        <p style="margin: 0; padding: 0;">{title}</p>
        <p style="margin: 0; padding: 0; font-size: 11px; font-weight: normal; color: red;">
            ⚠ Educational data only - Not for investment advice
        </p>
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # Get min and max values for color scale
    min_val = geo_bonds_wgs84[column].min()
    max_val = geo_bonds_wgs84[column].max()

    # Create choropleth layer
    folium.Choropleth(
        geo_data=geo_bonds_wgs84,
        name="choropleth",
        data=geo_bonds_wgs84,
        columns=["iso_a3", column],
        key_on="feature.properties.iso_a3",
        fill_color="YlGn",  # Yellow-Green color scheme
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name=column.replace("_", " ").title(),
        nan_fill_color="lightgrey",
        nan_fill_opacity=0.4,
    ).add_to(m)

    # Add tooltips with detailed information
    style_function = lambda x: {
        "fillColor": "#ffffff",
        "color": "#000000",
        "fillOpacity": 0.1,
        "weight": 0.1,
    }

    highlight_function = lambda x: {
        "fillColor": "#000000",
        "color": "#000000",
        "fillOpacity": 0.3,
        "weight": 0.5,
    }

    # Create GeoJson overlay with tooltips
    tooltip = folium.GeoJsonTooltip(
        fields=["name", "iso_a3", "total_amount_usd_millions", "bond_count"],
        aliases=[
            "Country:",
            "ISO Code:",
            "Total Amount (USD M):",
            "Number of Bonds:",
        ],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: white;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
    )

    folium.GeoJson(
        geo_bonds_wgs84,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=tooltip,
    ).add_to(m)

    # Add fullscreen button
    plugins.Fullscreen(
        position="topright",
        title="Expand map",
        title_cancel="Exit fullscreen",
        force_separate_button=True,
    ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save to file if path provided
    if output_path:
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        m.save(str(output_path_obj))

    return m


def create_interactive_bubble_map(
    bonds_df,
    geo_df: gpd.GeoDataFrame,
    output_path: Optional[str] = None,
) -> "folium.Map":
    """
    Create an interactive bubble map with circles proportional to bond amounts.

    This is an alternative visualization that shows individual bonds or
    aggregated data as circles on a map, where the circle size represents
    the bond amount.

    Parameters
    ----------
    bonds_df : pd.DataFrame
        DataFrame containing green bond data
    geo_df : gpd.GeoDataFrame
        GeoDataFrame containing country geometries
    output_path : str, optional
        Path to save the HTML map file

    Returns
    -------
    folium.Map
        Folium map object

    Raises
    ------
    ImportError
        If folium is not installed
    """
    if not FOLIUM_AVAILABLE:
        raise ImportError(
            "Folium is required for interactive maps. "
            "Install it with: pip install 'green-bond-tracker[interactive]'"
        )

    # Create base map
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

    # Aggregate bonds by country
    country_totals = (
        bonds_df.groupby("country_code")
        .agg({"amount_usd_millions": ["sum", "count"], "issuer": "nunique"})
        .reset_index()
    )
    country_totals.columns = [
        "country_code",
        "total_amount",
        "bond_count",
        "unique_issuers",
    ]

    # Get centroids for each country
    geo_df_wgs84 = geo_df.to_crs(epsg=4326)
    centroids = geo_df_wgs84.copy()
    centroids["centroid"] = centroids.geometry.centroid

    # Merge with bond data
    merged = centroids.merge(country_totals, left_on="iso_a3", right_on="country_code", how="inner")

    # Add circles for each country
    max_amount = merged["total_amount"].max()

    for _, row in merged.iterrows():
        # Scale radius based on amount (logarithmic scale for better visualization)
        import math

        radius = 5 + (math.log(row["total_amount"] + 1) / math.log(max_amount + 1)) * 45

        folium.CircleMarker(
            location=[row["centroid"].y, row["centroid"].x],
            radius=radius,
            popup=folium.Popup(
                f"""
                <b>{row['name']}</b><br>
                Total Amount: ${row['total_amount']:.2f}M<br>
                Number of Bonds: {row['bond_count']}<br>
                Unique Issuers: {row['unique_issuers']}
                """,
                max_width=200,
            ),
            color="darkgreen",
            fill=True,
            fillColor="green",
            fillOpacity=0.6,
            weight=2,
        ).add_to(m)

    # Add title
    title_html = """
    <div style="position: fixed;
                top: 10px;
                left: 50px;
                width: 400px;
                z-index: 9999;
                font-size: 14px;
                font-weight: bold;
                background-color: white;
                border: 2px solid grey;
                border-radius: 5px;
                padding: 10px;">
        Green Bonds by Country (Bubble Size = Total Amount)
    </div>
    """
    m.get_root().html.add_child(folium.Element(title_html))

    # Save if path provided
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        m.save(output_path)

    return m
