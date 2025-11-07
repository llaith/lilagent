"""CLI entry point for lilagent-github (GitHub-driven mode)."""

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from .config import Config
from .workflows.github_workflow import process_github_issue, monitor_pr_for_feedback

app = typer.Typer(
    name="lilagent-github",
    help="GitHub-integrated multi-agent system for issue-driven development",
    add_completion=False,
)
console = Console()


@app.command()
def process(
    issue_number: int = typer.Argument(
        ...,
        help="GitHub issue number to process",
    ),
    branch_name: Optional[str] = typer.Option(
        None,
        "--branch",
        "-b",
        help="Custom branch name (auto-generated if not provided)",
    ),
    monitor: bool = typer.Option(
        False,
        "--monitor",
        "-m",
        help="Monitor PR for feedback after creation",
    ),
    monitor_duration: int = typer.Option(
        60,
        "--monitor-duration",
        "-d",
        help="How long to monitor PR in minutes (default: 60)",
    ),
) -> None:
    """Process a GitHub issue and create a pull request.

    This command will:
    1. Read the issue description as specification
    2. Generate code using multi-agent system
    3. Create a pull request with the implementation
    4. Monitor CI status
    5. Optionally wait for and respond to user feedback

    Example:
        lilagent-github process 123
        lilagent-github process 123 --branch my-feature --monitor
    """
    # Validate configuration
    try:
        Config.validate()
        Config.validate_github()
    except ValueError as e:
        console.print(f"\n[red]❌ Configuration Error:[/red] {str(e)}\n", style="bold")
        console.print("Please ensure your .env file is configured with:\n")
        console.print("  - OPENAI_API_KEY (or other LLM provider key)")
        console.print("  - GITHUB_TOKEN")
        console.print("  - GITHUB_REPO (format: owner/repo)\n")
        sys.exit(1)

    # Show configuration
    console.print(
        Panel.fit(
            f"[bold cyan]Repository:[/bold cyan] {Config.GITHUB_REPO}\n"
            f"[bold cyan]Issue:[/bold cyan] #{issue_number}\n"
            f"[bold cyan]Branch:[/bold cyan] {branch_name or '(auto-generated)'}\n"
            f"[bold cyan]Agent Model:[/bold cyan] {Config.AGENT_MODEL}\n"
            f"[bold cyan]Monitor PR:[/bold cyan] {monitor}\n",
            title="⚙️  GitHub Mode Configuration",
            border_style="cyan",
        )
    )

    try:
        # Process the issue
        result = process_github_issue(
            issue_number=issue_number,
            branch_name=branch_name,
        )

        if result["success"]:
            console.print(
                Panel.fit(
                    f"[bold green]✅ Pull Request Created![/bold green]\n\n"
                    f"[cyan]PR Number:[/cyan] #{result['pr_number']}\n"
                    f"[cyan]URL:[/cyan] {result['pr_url']}\n"
                    f"[cyan]Branch:[/cyan] {result['branch']}\n"
                    f"[cyan]UAT:[/cyan] {'✅ Passed' if result['uat_passed'] else '⚠️ Draft'}\n"
                    f"[cyan]CI Status:[/cyan] {result['ci_status']}\n",
                    title="🎉 Success",
                    border_style="green",
                )
            )

            # Monitor if requested
            if monitor:
                console.print(f"\n[yellow]👀 Monitoring PR for {monitor_duration} minutes...[/yellow]\n")
                monitor_pr_for_feedback(
                    pr_number=result['pr_number'],
                    timeout_minutes=monitor_duration,
                )

            sys.exit(0)
        else:
            console.print(
                Panel.fit(
                    f"[bold red]❌ Processing failed[/bold red]\n\n"
                    f"Check the issue comments for error details.\n",
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
        console.print_exception()
        sys.exit(1)


@app.command()
def monitor(
    pr_number: int = typer.Argument(
        ...,
        help="Pull request number to monitor",
    ),
    duration: int = typer.Option(
        60,
        "--duration",
        "-d",
        help="How long to monitor in minutes (default: 60)",
    ),
) -> None:
    """Monitor an existing PR for user feedback.

    Example:
        lilagent-github monitor 456 --duration 120
    """
    try:
        Config.validate()
        Config.validate_github()
    except ValueError as e:
        console.print(f"\n[red]❌ Configuration Error:[/red] {str(e)}\n", style="bold")
        sys.exit(1)

    console.print(f"\n[cyan]Monitoring PR #{pr_number} for {duration} minutes...[/cyan]\n")

    try:
        result = monitor_pr_for_feedback(pr_number, duration)
        console.print(f"\n[green]✅ Monitoring complete[/green]\n")
    except Exception as e:
        console.print(f"\n[red]❌ Error:[/red] {str(e)}\n")
        sys.exit(1)


@app.command()
def setup():
    """Show setup instructions for GitHub integration."""
    console.print("\n[bold cyan]Setting up LilAgent GitHub Integration[/bold cyan]\n")

    console.print("[bold]Step 1: Create a GitHub Personal Access Token[/bold]")
    console.print("  1. Go to: https://github.com/settings/tokens")
    console.print("  2. Click 'Generate new token' → 'Generate new token (classic)'")
    console.print("  3. Give it a name: 'LilAgent'")
    console.print("  4. Select scopes: [green]repo[/green] (full control)")
    console.print("  5. Click 'Generate token' and copy it\n")

    console.print("[bold]Step 2: Configure your .env file[/bold]")
    console.print("  Add these lines to your .env file:")
    console.print("  [yellow]GITHUB_TOKEN=your-token-here[/yellow]")
    console.print("  [yellow]GITHUB_REPO=owner/repo[/yellow]")
    console.print("  [yellow]GITHUB_DEFAULT_BRANCH=main[/yellow]\n")

    console.print("[bold]Step 3: Initialize your repository[/bold]")
    console.print("  Your repository should have:")
    console.print("  - A default branch (main/master)")
    console.print("  - Issues enabled")
    console.print("  - Optional: CI/CD workflow (GitHub Actions)\n")

    console.print("[bold]Step 4: Create an issue[/bold]")
    console.print("  Create a GitHub issue describing what you want to build\n")

    console.print("[bold]Step 5: Run lilagent-github[/bold]")
    console.print("  [green]lilagent-github process <issue-number>[/green]\n")

    console.print("[bold cyan]Example Workflow:[/bold cyan]")
    console.print("  1. Create issue: 'Build a CLI calculator'")
    console.print("  2. Run: [green]lilagent-github process 123[/green]")
    console.print("  3. Agent creates PR with implementation")
    console.print("  4. Review PR, provide feedback via comments")
    console.print("  5. Agent can respond to feedback and iterate\n")


if __name__ == "__main__":
    app()
