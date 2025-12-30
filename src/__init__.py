"""
Green Bond Tracker - A lightweight educational project for tracking green bonds
with GIS visualization capabilities.

This package provides tools to load, validate, and visualize green bond data.

Note: This is an educational project and should not be used for investment advice.
"""

from .data_loader import (
    get_summary_statistics,
    join_bonds_with_geo,
    load_country_geometries,
    load_green_bonds,
    validate_bond_data,
)

__version__ = "0.2.0"

__all__ = [
    "load_green_bonds",
    "load_country_geometries",
    "validate_bond_data",
    "join_bonds_with_geo",
    "get_summary_statistics",
]
