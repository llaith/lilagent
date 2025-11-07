"""CLI entry point for lilagent."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from .config import Config
from .orchestrator import run_spec_to_code

app = typer.Typer(
    name="lilagent",
    help="LLM-powered multi-agent system that generates software packages from specifications",
    add_completion=False,
)
console = Console()


@app.command()
def run(
    spec_file: Path = typer.Argument(
        ...,
        help="Path to specification file (markdown format)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    work_dir: Path = typer.Argument(
        ...,
        help="Output directory where package will be created",
    ),
    verbose: bool = typer.Option(
        True,
        "--verbose/--quiet",
        "-v/-q",
        help="Enable verbose logging",
    ),
) -> None:
    """Generate a software package from a specification file.

    SPEC_FILE: Path to your specification markdown file

    WORK_DIR: Directory where the package will be created

    Example:
        lilagent spec.md ./output-dir/
    """
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        console.print(f"\n[red]❌ Configuration Error:[/red] {str(e)}\n", style="bold")
        console.print("Please ensure your .env file is configured with required API keys.\n")
        console.print("Copy .env.example to .env and fill in your values.\n")
        sys.exit(1)

    # Convert paths to strings
    spec_file_str = str(spec_file.absolute())
    work_dir_str = str(work_dir.absolute())

    # Show configuration panel
    console.print(
        Panel.fit(
            f"[bold cyan]Specification:[/bold cyan] {spec_file_str}\n"
            f"[bold cyan]Output Directory:[/bold cyan] {work_dir_str}\n"
            f"[bold cyan]Normalizer Model:[/bold cyan] {Config.NORMALIZER_MODEL}\n"
            f"[bold cyan]Agent Model:[/bold cyan] {Config.AGENT_MODEL}\n"
            f"[bold cyan]Webhook URL:[/bold cyan] {Config.WEBHOOK_URL or 'Not configured'}\n",
            title="⚙️  Configuration",
            border_style="cyan",
        )
    )

    try:
        # Run the spec-to-code pipeline
        result = run_spec_to_code(spec_file_str, work_dir_str)

        if result["success"]:
            console.print(
                Panel.fit(
                    f"[bold green]✅ Package successfully created![/bold green]\n\n"
                    f"[cyan]Location:[/cyan] {result['work_dir']}\n"
                    f"[cyan]Duration:[/cyan] {result['duration']}\n"
                    f"[cyan]Iterations:[/cyan] {result['implementation']['iterations']}\n",
                    title="🎉 Success",
                    border_style="green",
                )
            )
            sys.exit(0)
        else:
            console.print(
                Panel.fit(
                    f"[bold red]❌ Package creation failed[/bold red]\n\n"
                    f"UAT did not pass after {result['implementation']['iterations']} iteration(s).\n"
                    f"Check the output directory for partial results.\n",
                    title="⚠️  Failure",
                    border_style="red",
                )
            )
            sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Interrupted by user[/yellow]\n")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red] {str(e)}\n", style="bold")
        if verbose:
            console.print_exception()
        sys.exit(1)


@app.command()
def version():
    """Show version information."""
    console.print("\n[bold cyan]lilagent[/bold cyan] version [green]0.1.0[/green]\n")
    console.print("Multi-agent spec-to-code system powered by LLMs\n")


if __name__ == "__main__":
    app()
