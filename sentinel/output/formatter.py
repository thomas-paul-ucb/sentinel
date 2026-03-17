from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

console = Console()


def save_report(repo_url: str, report: str) -> str:
    """
    Saves the markdown report to a reports/ folder.
    Returns the path where it was saved.
    """
    # Create reports directory if it doesnt exist
    Path("reports").mkdir(exist_ok=True)

    # Clean repo name for filename e.g torvalds/linux -> torvalds_linux
    repo_name = repo_url.split("github.com/")[-1].replace("/", "_").strip("/")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/{repo_name}_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Sentinel Report\n")
        f.write(f"**Repo:** {repo_url}\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(report)

    return filename


def print_report(report: str):
    """
    Prints the markdown report beautifully in the terminal using Rich.
    """
    console.print("\n")
    console.rule("[bold cyan]SENTINEL REPORT[/bold cyan]")
    console.print("\n")
    console.print(Markdown(report))
    console.rule("[bold cyan]END OF REPORT[/bold cyan]")