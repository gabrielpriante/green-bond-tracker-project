"""
Green Bond Tracker - Analytics Module

Portfolio-style analytics and metrics for green bond data.

Note: This is an educational project and should not be used for investment advice.
"""

from .metrics import (
    aggregation_by_category,
    aggregation_by_country,
    aggregation_by_year,
    concentration_index,
    data_coverage_report,
    issuance_overview,
    portfolio_summary_table,
    top_n_concentration,
)

__all__ = [
    "issuance_overview",
    "aggregation_by_country",
    "aggregation_by_year",
    "aggregation_by_category",
    "top_n_concentration",
    "concentration_index",
    "data_coverage_report",
    "portfolio_summary_table",
]
