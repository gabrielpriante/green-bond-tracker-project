"""
Green Bond Tracker - Command Line Interface

This module provides a CLI for validating, analyzing, and visualizing green bond data.

Note: This is an educational project and should not be used for investment advice.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="greenbond",
    help="Green Bond Tracker - Educational toolkit for green bond analysis",
    add_completion=False,
)
console = Console()


@app.command()
def validate(
    csv_path: Path = typer.Argument(
        ...,
        help="Path to the green bonds CSV file",
        exists=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to save validation report CSV with row flags",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed validation results",
    ),
):
    """
    Validate green bond CSV data against the schema.

    Checks for:
    - Missing required fields
    - Null values in required columns
    - Invalid data types
    - Out-of-range values
    - Invalid ISO codes
    - Date inconsistencies
    - Duplicate bond IDs
    """
    from .data_loader import load_green_bonds
    from .validation import validate_bond_data_enhanced

    console.print(f"\n[bold cyan]Validating:[/bold cyan] {csv_path}")

    try:
        # Load data
        df = load_green_bonds(str(csv_path))
        console.print(f"[green]✓[/green] Loaded {len(df)} records")

        # Validate
        result = validate_bond_data_enhanced(df)

        # Print results
        if result.is_valid:
            console.print(f"\n[bold green]✓ Validation PASSED[/bold green]")
        else:
            console.print(f"\n[bold red]✗ Validation FAILED[/bold red]")

        console.print(f"  Errors: [red]{len(result.errors)}[/red]")
        console.print(f"  Warnings: [yellow]{len(result.warnings)}[/yellow]")

        if verbose or not result.is_valid:
            if result.errors:
                console.print("\n[bold red]Errors:[/bold red]")
                for error in result.errors[:20]:  # Limit to first 20
                    console.print(f"  [red]•[/red] {error}")
                if len(result.errors) > 20:
                    console.print(f"  ... and {len(result.errors) - 20} more errors")

            if result.warnings and verbose:
                console.print("\n[bold yellow]Warnings:[/bold yellow]")
                for warning in result.warnings[:20]:  # Limit to first 20
                    console.print(f"  [yellow]•[/yellow] {warning}")
                if len(result.warnings) > 20:
                    console.print(f"  ... and {len(result.warnings) - 20} more warnings")

        # Save flagged output if requested
        if output:
            flags_list = []
            for idx in df.index:
                if idx in result.row_flags:
                    flags_list.append(" | ".join(result.row_flags[idx]))
                else:
                    flags_list.append("OK")

            output_df = df.copy()
            output_df["validation_flags"] = flags_list

            output.parent.mkdir(parents=True, exist_ok=True)
            output_df.to_csv(output, index=False)
            console.print(f"\n[green]✓[/green] Validation report saved to: {output}")

        # Exit with error code if validation failed
        if not result.is_valid:
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def summary(
    csv_path: Path = typer.Argument(
        Path("data/green_bonds.csv"),
        help="Path to the green bonds CSV file",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output summary as JSON",
    ),
):
    """
    Print summary statistics for green bond data.

    Shows:
    - Total number of bonds
    - Total and average amounts
    - Number of unique issuers and countries
    - Date range
    - Top countries by amount
    """
    from .data_loader import get_summary_statistics, load_green_bonds

    console.print(f"\n[bold cyan]Analyzing:[/bold cyan] {csv_path}")

    try:
        # Load data
        df = load_green_bonds(str(csv_path))

        # Get statistics
        stats = get_summary_statistics(df)

        if json_output:
            import json

            # Convert datetime objects to strings for JSON serialization
            stats_json = stats.copy()
            if "earliest_issue" in stats_json:
                stats_json["earliest_issue"] = str(stats_json["earliest_issue"])
            if "latest_issue" in stats_json:
                stats_json["latest_issue"] = str(stats_json["latest_issue"])

            console.print(json.dumps(stats_json, indent=2))
        else:
            # Create a nice table
            table = Table(title="Green Bond Summary Statistics", show_header=True)
            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Value", style="green")

            table.add_row("Total Bonds", str(stats["total_bonds"]))
            table.add_row(
                "Total Amount (USD Millions)",
                f"${stats['total_amount_usd_millions']:,.2f}",
            )
            table.add_row(
                "Average Bond Size (USD Millions)",
                f"${stats['average_bond_size_usd_millions']:,.2f}",
            )
            table.add_row(
                "Median Bond Size (USD Millions)",
                f"${stats['median_bond_size_usd_millions']:,.2f}",
            )
            table.add_row("Unique Issuers", str(stats["unique_issuers"]))
            table.add_row("Unique Countries", str(stats["unique_countries"]))

            if "earliest_issue" in stats:
                table.add_row("Earliest Issue", str(stats["earliest_issue"].date()))
                table.add_row("Latest Issue", str(stats["latest_issue"].date()))

            console.print(table)

            # Top countries
            if "top_5_countries" in stats and stats["top_5_countries"]:
                console.print("\n[bold cyan]Top 5 Countries by Amount:[/bold cyan]")
                for country, amount in stats["top_5_countries"].items():
                    console.print(f"  {country}: ${amount:,.2f}M")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def viz(
    csv_path: Path = typer.Argument(
        Path("data/green_bonds.csv"),
        help="Path to the green bonds CSV file",
    ),
    geo_path: Path = typer.Option(
        Path("data/countries_geo.json"),
        "--geo",
        "-g",
        help="Path to the countries GeoJSON file",
    ),
    output_dir: Path = typer.Option(
        Path("outputs"),
        "--output-dir",
        "-o",
        help="Directory to save visualizations",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Generate interactive map (requires folium)",
    ),
):
    """
    Generate visualizations for green bond data.

    Creates:
    - Project type bar chart
    - Choropleth map (total amount)
    - Choropleth map (bond count)
    - Optional: Interactive map (if --interactive flag is used)

    All outputs are saved to the specified output directory.
    """
    from .data_loader import join_bonds_with_geo, load_country_geometries, load_green_bonds
    from .visuals import create_and_save_all_visuals

    console.print(f"\n[bold cyan]Creating visualizations[/bold cyan]")
    console.print(f"  Data: {csv_path}")
    console.print(f"  Geo: {geo_path}")
    console.print(f"  Output: {output_dir}")

    try:
        # Load data
        console.print("\n[cyan]Loading data...[/cyan]")
        bonds = load_green_bonds(str(csv_path))
        countries = load_country_geometries(str(geo_path))
        geo_bonds = join_bonds_with_geo(bonds, countries)

        console.print(f"[green]✓[/green] Loaded {len(bonds)} bonds and {len(countries)} countries")

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate static visualizations
        console.print("\n[cyan]Generating static visualizations...[/cyan]")
        saved_files = create_and_save_all_visuals(bonds, geo_bonds, str(output_dir))

        console.print("\n[bold green]✓ Static visualizations created:[/bold green]")
        for name, path in saved_files.items():
            console.print(f"  [green]•[/green] {name}: {path}")

        # Generate interactive map if requested
        if interactive:
            try:
                from .interactive import create_interactive_choropleth_map

                console.print("\n[cyan]Generating interactive map...[/cyan]")
                interactive_path = (
                    output_dir / "green_bonds_interactive_map.html"
                )
                create_interactive_choropleth_map(
                    geo_bonds,
                    output_path=str(interactive_path),
                )
                console.print(f"[green]✓[/green] Interactive map: {interactive_path}")
            except ImportError:
                console.print(
                    "\n[yellow]⚠[/yellow] Interactive maps require folium. "
                    "Install with: pip install 'green-bond-tracker[interactive]'"
                )

        console.print(f"\n[bold green]✓ All visualizations saved to:[/bold green] {output_dir}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback

        console.print(traceback.format_exc())
        raise typer.Exit(code=1)


@app.command()
def version():
    """Show version information."""
    from . import __version__

    console.print(f"Green Bond Tracker v{__version__}")
    console.print("Educational toolkit for green bond analysis with GIS visualization")
    console.print("\n[yellow]⚠ DISCLAIMER:[/yellow] For educational purposes only.")
    console.print("Not intended for investment advice or financial decision-making.")


if __name__ == "__main__":
    app()
