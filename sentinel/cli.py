import click
from rich.console import Console
from sentinel.github.client import get_repo_files
from sentinel.agent.reviewer import run_review_agent
from sentinel.output.formatter import save_report, print_report
from sentinel.memory import build_system_prompt_context, run_review_session

console = Console()

MOCK_REPORT = """\
## Overall Summary

This is a mock report generated with `--mock` for testing the memory and session flow.
Three synthetic findings are included across two files.

## File: sentinel/agent/reviewer.py

### High Severity
- **Unbounded agentic loop** (line 102): The `while True` loop has no iteration cap. A tool \
that always returns `tool_use` will run forever and exhaust API credits.

### Medium Severity
- **Hardcoded model string** (line 109): `"claude-sonnet-4-20250514"` is repeated inline. \
Move it to `sentinel/config.py` so upgrades require a single change.

## File: sentinel/output/formatter.py

### Low Severity
- **Silent truncation of long repo names** (line 18): `repo_url.split("github.com/")[-1]` \
will silently produce an unexpected filename if given a non-GitHub URL.
"""


@click.group()
def cli():
    """Sentinel — Agentic code review powered by Claude."""
    pass


@cli.command()
@click.argument("repo_url")
@click.option("--ext", default=".py", help="File extension to analyze (default: .py)")
@click.option("--no-review-session", is_flag=True, default=False, help="Skip the interactive finding review.")
@click.option("--mock", is_flag=True, default=False, help="Skip the Claude API call and use a hardcoded sample report.")
def review(repo_url: str, ext: str, no_review_session: bool, mock: bool):
    """
    Review a GitHub repository.

    Example: sentinel review https://github.com/owner/repo
    """

    console.rule("[bold cyan]SENTINEL[/bold cyan]")

    if mock:
        console.print("[dim yellow]Mock mode — skipping GitHub fetch and Claude API call.[/dim yellow]\n")
        report = MOCK_REPORT
    else:
        console.print(f"[cyan]Fetching files from:[/cyan] {repo_url}")

        files = get_repo_files(repo_url, extensions=[ext])

        if not files:
            console.print("[red]No files found with that extension.[/red]")
            return

        console.print(f"[green]Found {len(files)} file(s). Starting review...[/green]\n")

        memory_context = build_system_prompt_context()
        if memory_context:
            console.print("[dim]Loaded engineer preferences from preferences.json[/dim]\n")

        console.print("[yellow]Claude is analyzing...[/yellow]")
        report = run_review_agent(files, memory_context=memory_context)

    print_report(report)
    path = save_report(repo_url, report)
    console.print(f"\n[green]Report saved to:[/green] {path}")

    if not no_review_session:
        run_review_session(report)