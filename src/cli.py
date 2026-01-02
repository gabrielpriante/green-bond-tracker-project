"""
Green Bond Tracker - Command Line Interface

This module provides a CLI for validating, analyzing, and visualizing green bond data.

Note: This is an educational project and should not be used for investment advice.
"""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import get_config, reset_config

app = typer.Typer(
    name="gbt",
    help="Green Bond Tracker - Educational toolkit for green bond analysis",
    add_completion=False,
)
console = Console()

# Global state for config path (set in main callback)
_config_path: Path | None = None


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        from . import __version__

        console.print(f"Green Bond Tracker v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration YAML file (default: config.yaml in repo root)",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """Green Bond Tracker - Educational toolkit for green bond analysis."""
    # Store config path globally for subcommands
    global _config_path
    _config_path = config

    # Load config if provided
    if config:
        try:
            get_config(config)
        except Exception as e:
            console.print(f"[bold red]Error loading configuration:[/bold red] {e}")
            raise typer.Exit(code=1)

    # Show deprecation warning if invoked via greenbond
    if len(sys.argv) > 0 and "greenbond" in sys.argv[0]:
        console.print(
            "[yellow]Note:[/yellow] 'greenbond' is deprecated; please use 'gbt' instead.\n"
        )


@app.command()
def validate(
    input_path: Path | None = typer.Option(
        None,
        "--input",
        "-i",
        help="Path to the green bonds CSV file (overrides config)",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    output: Path | None = typer.Option(
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

    # Get config and determine input path
    config = get_config(_config_path)
    if input_path is None:
        input_path = Path(config.raw_data_path)

    console.print(f"\n[bold cyan]Validating:[/bold cyan] {input_path}")

    try:
        # Load data
        df = load_green_bonds(str(input_path))
        console.print(f"[green]✓[/green] Loaded {len(df)} records")

        # Validate
        result = validate_bond_data_enhanced(df)

        # Print results
        if result.is_valid:
            console.print("\n[bold green]✓ Validation PASSED[/bold green]")
        else:
            console.print("\n[bold red]✗ Validation FAILED[/bold red]")

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
    input_path: Path | None = typer.Option(
        None,
        "--input",
        "-i",
        help="Path to the green bonds CSV file (overrides config)",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory to save summary CSVs (overrides config)",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output summary as JSON",
    ),
):
    """
    Generate portfolio analytics and summary statistics for green bond data.

    Displays:
    - Portfolio overview (total bonds, issuance, issuers, countries, data quality)
    - Concentration metrics (top 5 countries share, HHI)
    - Top categories (top country, year, project type)

    Outputs:
    - Console: Human-readable summary table
    - CSV: outputs/portfolio_summary.csv
    - CSV: outputs/data_coverage_report.csv
    """
    from .analytics.metrics import data_coverage_report, portfolio_summary_table
    from .data_loader import load_green_bonds

    # Get config and determine paths
    config = get_config(_config_path)
    if input_path is None:
        input_path = Path(config.raw_data_path)
    if output_dir is None:
        output_dir = Path(config.outputs_dir)

    console.print(f"\n[bold cyan]Portfolio Analytics:[/bold cyan] {input_path}")

    try:
        # Load data
        df = load_green_bonds(str(input_path))
        console.print(f"[green]✓[/green] Loaded {len(df)} records")

        # Generate portfolio summary table
        summary_table = portfolio_summary_table(df)

        # Generate data coverage report
        coverage_report = data_coverage_report(df)

        if json_output:
            import json

            output = {
                "portfolio_summary": summary_table.to_dict(orient="records"),
                "data_coverage": coverage_report.to_dict(orient="records"),
            }
            console.print(json.dumps(output, indent=2))
        else:
            # Display portfolio summary
            console.print("\n[bold cyan]Portfolio Summary:[/bold cyan]")
            table = Table(show_header=True)
            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Value", style="green")

            for _, row in summary_table.iterrows():
                table.add_row(row["metric"], row["value"])

            console.print(table)

            # Display data coverage highlights
            console.print("\n[bold cyan]Data Coverage Highlights:[/bold cyan]")
            low_coverage = coverage_report[coverage_report["pct_non_null"] < 80]
            if len(low_coverage) > 0:
                console.print("[yellow]⚠ Fields with low coverage (<80%):[/yellow]")
                for _, row in low_coverage.iterrows():
                    console.print(f"  • {row['column_name']}: {row['pct_non_null']:.1f}%")
            else:
                console.print("[green]✓ All fields have good coverage (>=80%)[/green]")

        # Save to CSV files
        output_dir.mkdir(parents=True, exist_ok=True)

        summary_path = output_dir / config.output_portfolio_summary
        summary_table.to_csv(summary_path, index=False)
        console.print(f"\n[green]✓[/green] Portfolio summary saved to: {summary_path}")

        coverage_path = output_dir / config.output_data_coverage_report
        coverage_report.to_csv(coverage_path, index=False)
        console.print(f"[green]✓[/green] Data coverage report saved to: {coverage_path}")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback

        console.print(traceback.format_exc())
        raise typer.Exit(code=1)


@app.command()
def map(
    input_path: Path | None = typer.Option(
        None,
        "--input",
        "-i",
        help="Path to the green bonds CSV file (overrides config)",
        exists=True,
        dir_okay=False,
        readable=True,
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output path for the interactive HTML map (overrides config)",
    ),
    geo_path: Path | None = typer.Option(
        None,
        "--geo",
        "-g",
        help="Path to the countries GeoJSON file (overrides config)",
    ),
):
    """
    Generate an interactive choropleth map for green bond data.

    Creates an interactive HTML map showing green bond distribution by country.
    Requires folium to be installed (pip install green-bond-tracker[interactive]).
    """
    from .data_loader import join_bonds_with_geo, load_country_geometries, load_green_bonds

    # Get config and determine paths
    config = get_config(_config_path)
    if input_path is None:
        input_path = Path(config.raw_data_path)
    if geo_path is None:
        geo_path = Path(config.geo_data_path)
    if output is None:
        output = Path(config.outputs_dir) / config.map_default_output

    console.print("\n[bold cyan]Creating interactive map[/bold cyan]")
    console.print(f"  Input: {input_path}")
    console.print(f"  Output: {output}")

    try:
        # Check if folium is available
        try:
            from .interactive import create_interactive_choropleth_map
        except ImportError:
            console.print("\n[bold red]Error:[/bold red] Interactive maps require folium.")
            console.print(
                "Install with: [cyan]pip install 'green-bond-tracker[interactive]'[/cyan]"
            )
            raise typer.Exit(code=2)

        # Load data
        console.print("\n[cyan]Loading data...[/cyan]")
        bonds = load_green_bonds(str(input_path))
        countries = load_country_geometries(str(geo_path))
        geo_bonds = join_bonds_with_geo(bonds, countries)

        console.print(f"[green]✓[/green] Loaded {len(bonds)} bonds and {len(countries)} countries")

        # Create output directory if needed
        output.parent.mkdir(parents=True, exist_ok=True)

        # Generate interactive map
        console.print("\n[cyan]Generating interactive map...[/cyan]")
        create_interactive_choropleth_map(
            geo_bonds,
            output_path=str(output),
        )
        console.print(f"\n[bold green]✓ Interactive map saved to:[/bold green] {output}")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback

        console.print(traceback.format_exc())
        raise typer.Exit(code=1)


@app.command()
def viz(
    input_path: Path | None = typer.Option(
        None,
        "--input",
        "-i",
        help="Path to the green bonds CSV file (overrides config)",
    ),
    geo_path: Path | None = typer.Option(
        None,
        "--geo",
        "-g",
        help="Path to the countries GeoJSON file (overrides config)",
    ),
    output_dir: Path | None = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Directory to save visualizations (overrides config)",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
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

    # Get config and determine paths
    config = get_config(_config_path)
    if input_path is None:
        input_path = Path(config.raw_data_path)
    if geo_path is None:
        geo_path = Path(config.geo_data_path)
    if output_dir is None:
        output_dir = Path(config.outputs_dir)

    console.print("\n[bold cyan]Creating visualizations[/bold cyan]")
    console.print(f"  Data: {input_path}")
    console.print(f"  Geo: {geo_path}")
    console.print(f"  Output: {output_dir}")

    try:
        # Load data
        console.print("\n[cyan]Loading data...[/cyan]")
        bonds = load_green_bonds(str(input_path))
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
                interactive_path = output_dir / config.map_default_output
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
