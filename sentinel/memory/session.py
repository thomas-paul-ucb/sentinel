import re
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from sentinel.memory import store

console = Console()

_SEVERITY_RE = re.compile(r"^###\s+(High|Medium|Low)\s+Severity", re.IGNORECASE | re.MULTILINE)
_FILE_HEADING_RE = re.compile(r"^##\s+(?:File[:\s]+)?(.+)", re.MULTILINE)
_SKIP_HEADINGS = re.compile(r"^(High|Medium|Low|Overall|Summary|Findings|Report)", re.IGNORECASE)

SEVERITY_COLORS = {"high": "red", "medium": "yellow", "low": "blue"}


def parse_findings(report: str) -> list[dict]:
    """Extract individual findings from the markdown report."""
    findings = []
    current_severity = "unknown"
    current_file = None

    for line in report.splitlines():
        line_stripped = line.strip()

        file_match = _FILE_HEADING_RE.match(line_stripped)
        if file_match:
            candidate = file_match.group(1).strip()
            if not _SKIP_HEADINGS.match(candidate):
                current_file = candidate
            continue

        sev_match = _SEVERITY_RE.match(line_stripped)
        if sev_match:
            current_severity = sev_match.group(1).lower()
            continue

        bullet_match = re.match(r"^[-*]\s+(.+)", line_stripped)
        if bullet_match:
            text = bullet_match.group(1).strip()
            # Skip very short items that are likely sub-bullets or headers, not findings
            if len(text) > 25:
                findings.append({
                    "text": text,
                    "severity": current_severity,
                    "file": current_file,
                })

    return findings


def run_review_session(report: str):
    """
    Walk the engineer through each finding after the review completes.
    Responses are persisted to preferences.json via the store module.
    """
    findings = parse_findings(report)
    if not findings:
        return

    console.print()
    console.rule("[bold yellow]ENGINEER REVIEW SESSION[/bold yellow]")
    console.print(
        "[dim]Review each finding. Options:[/dim]\n"
        "  [bold cyan]a[/bold cyan] — accept (no action)\n"
        "  [bold cyan]d[/bold cyan] — dismiss with a note (saved, suppressed in future reviews)\n"
        "  [bold cyan]p[/bold cyan] — save a style preference (applied to all future reviews)\n"
        "  [bold cyan]s[/bold cyan] — skip the rest of this session\n"
    )

    for i, finding in enumerate(findings, 1):
        color = SEVERITY_COLORS.get(finding["severity"], "white")
        file_prefix = f"[dim]{finding['file']}[/dim]\n" if finding["file"] else ""

        console.print(Panel(
            f"{file_prefix}[{color}][bold]{finding['severity'].upper()}[/bold][/{color}]\n\n{finding['text']}",
            title=f"[bold]Finding {i} of {len(findings)}[/bold]",
            border_style=color,
            padding=(0, 1),
        ))

        choice = Prompt.ask("Action", choices=["a", "d", "p", "s"], default="a")

        if choice == "s":
            console.print("[dim]Skipping remaining findings.[/dim]")
            break
        elif choice == "d":
            note = Prompt.ask("Dismiss reason [dim](optional, press Enter to skip)[/dim]", default="")
            store.add_dismissed(finding["text"], note)
            console.print("[dim green]Dismissed and saved to preferences.json[/dim green]")
        elif choice == "p":
            pref = Prompt.ask("Style preference to save for future reviews")
            if pref.strip():
                store.add_preference(pref.strip())
                console.print("[dim green]Preference saved to preferences.json[/dim green]")
        # 'a' — accept, nothing to persist

    console.print()
    console.rule("[bold yellow]SESSION COMPLETE[/bold yellow]")
