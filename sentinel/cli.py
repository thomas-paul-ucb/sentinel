import click
from rich.console import Console
from sentinel.github.client import get_repo_files
from sentinel.agent.reviewer import run_review_agent
from sentinel.output.formatter import save_report, print_report
from sentinel.memory import build_system_prompt_context, run_review_session

console = Console()


@click.group()
def cli():
    """Sentinel — Agentic code review powered by Claude."""
    pass


@cli.command()
@click.argument("repo_url")
@click.option("--ext", default=".py", help="File extension to analyze (default: .py)")
@click.option("--no-review-session", is_flag=True, default=False, help="Skip the interactive finding review.")
def review(repo_url: str, ext: str, no_review_session: bool):
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

    # Step 2 — load engineer memory and run the Claude agent
    memory_context = build_system_prompt_context()
    if memory_context:
        console.print("[dim]Loaded engineer preferences from preferences.json[/dim]\n")

    console.print("[yellow]Claude is analyzing...[/yellow]")
    report = run_review_agent(files, memory_context=memory_context)

    # Step 3 — print and save the report
    print_report(report)
    path = save_report(repo_url, report)
    console.print(f"\n[green]Report saved to:[/green] {path}")

    # Step 4 — interactive engineer review session
    if not no_review_session:
        run_review_session(report)