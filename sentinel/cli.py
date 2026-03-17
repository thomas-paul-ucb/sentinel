import click
from rich.console import Console
from sentinel.github.client import get_repo_files
from sentinel.agent.reviewer import run_review_agent
from sentinel.output.formatter import save_report, print_report

console = Console()


@click.group()
def cli():
    """Sentinel — Agentic code review powered by Claude."""
    pass


@cli.command()
@click.argument("repo_url")
@click.option("--ext", default=".py", help="File extension to analyze (default: .py)")
def review(repo_url: str, ext: str):
    """
    Review a GitHub repository.

    Example: sentinel review https://github.com/owner/repo
    """

    console.rule("[bold cyan]SENTINEL[/bold cyan]")
    console.print(f"[cyan]Fetching files from:[/cyan] {repo_url}")

    # Step 1 — fetch files from GitHub
    files = get_repo_files(repo_url, extensions=[ext])

    if not files:
        console.print("[red]No files found with that extension.[/red]")
        return

    console.print(f"[green]Found {len(files)} file(s). Starting review...[/green]\n")

    # Step 2 — run the Claude agent
    console.print("[yellow]Claude is analyzing...[/yellow]")
    report = run_review_agent(files)

    # Step 3 — print and save the report
    print_report(report)
    path = save_report(repo_url, report)
    console.print(f"\n[green]Report saved to:[/green] {path}")