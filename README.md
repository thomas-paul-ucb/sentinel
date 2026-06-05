# Sentinel

> Agentic code review powered by Claude

Sentinel reviews GitHub repositories autonomously. Point it at any public repo and it fetches the source, runs static analysis, and sends everything through a Claude agentic loop that produces a severity-ranked markdown report. After each review, an interactive session lets you accept, dismiss, or annotate findings — and those decisions persist so the review style adapts over time.

## How it works

```
GitHub repo
    │
    ▼
 Fetch files (PyGithub)
    │
    ▼
 Claude agentic loop
    ├── tool call: run_pylint   → unused vars, bad naming, complexity
    ├── tool call: parse_structure → oversized functions, class layout
    └── (repeats until Claude has enough signal)
    │
    ▼
 Markdown report (severity-ranked: high / medium / low)
    │
    ▼
 Engineer review session
    ├── accept finding
    ├── dismiss with note  ──► saved to preferences.json
    └── save style preference ──► saved to preferences.json
    │
    ▼
 Next run: memory injected into Claude system prompt
```

### Agentic loop

`sentinel/agent/reviewer.py` drives a tool-use loop against the Claude API. Claude decides which files to inspect and which tools to call. Each tool result is fed back into the conversation until Claude signals `end_turn` with a finished report. The loop has no fixed iteration count — Claude stops when it has enough information.

If `preferences.json` exists, the stored engineer preferences are injected as a `system` prompt before the loop starts, shaping what Claude flags and how it phrases findings.

### Memory system

`sentinel/memory/` persists two kinds of engineer feedback:

| Type | What it stores | Effect on next run |
|---|---|---|
| **Dismissed finding** | The finding text + optional reason | Claude is told not to raise similar issues; finding is hidden from the session |
| **Style preference** | Free-text rule (e.g. "suggest f-strings over .format()") | Injected verbatim into Claude's system prompt |

Both are stored in `preferences.json` in the project root. The file is created on first use.

```json
{
  "dismissed": [
    {
      "finding": "Missing type hints on public functions",
      "note": "We use docstrings instead",
      "timestamp": "2026-06-05T14:32:00"
    }
  ],
  "style_preferences": [
    {
      "preference": "Always suggest f-strings instead of .format()",
      "timestamp": "2026-06-05T14:33:00"
    }
  ]
}
```

### Interactive review session

After the report is printed, Sentinel walks you through each finding one at a time:

```
╭─ Finding 1 of 3 ──────────────────────────────────────────╮
│ sentinel/agent/reviewer.py                                 │
│ HIGH                                                       │
│                                                            │
│ **Unbounded agentic loop** (line 102): The `while True`    │
│ loop has no iteration cap.                                 │
╰────────────────────────────────────────────────────────────╯
Action (a, d, p, s) [a]:
```

Options:
- `a` — accept, move to next finding
- `d` — dismiss; optionally add a note explaining why; suppressed in future reviews
- `p` — save a style preference that will be applied to all future reviews
- `s` — skip the rest of the session

Previously dismissed findings are automatically filtered out before the session starts.

## Setup

```bash
git clone https://github.com/thomas-paul-ucb/sentinel.git
cd sentinel
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
cp .env.example .env
# fill in your API keys
```

**Environment variables** (`.env`):
```
ANTHROPIC_API_KEY=your_claude_api_key
GITHUB_TOKEN=your_github_token
```

## Usage

**Review a repository:**
```bash
python -m sentinel review https://github.com/owner/repo
```

**Review only TypeScript files:**
```bash
python -m sentinel review https://github.com/owner/repo --ext .ts
```

**Run with a hardcoded sample report — no API calls, no GitHub fetch:**
```bash
python -m sentinel review https://github.com/owner/repo --mock
```
Useful for testing the memory system and interactive session without spending API credits.

**Skip the interactive session (e.g. in CI):**
```bash
python -m sentinel review https://github.com/owner/repo --no-review-session
```

Reports are saved to `reports/<owner>_<repo>_<timestamp>.md`.

## Project structure

```
sentinel/
├── agent/
│   └── reviewer.py        # Claude agentic loop, tool dispatch
├── github/
│   └── client.py          # Fetch files from a GitHub repo
├── memory/
│   ├── store.py           # Read/write preferences.json
│   └── session.py         # Parse findings, run interactive review
├── output/
│   └── formatter.py       # Rich terminal output, save markdown report
├── cli.py                 # Click CLI entry point
├── config.py              # Load API keys from .env
└── __main__.py            # python -m sentinel entry point
```

## Future improvements

- **Multi-engineer support:** replace the flat JSON store with a database backend and per-engineer session tokens so preferences are scoped per user rather than globally.

## Tech stack

- [Claude API](https://docs.anthropic.com/) — agentic loop with tool use
- [PyGithub](https://pygithub.readthedocs.io/) — repository file fetching
- [pylint](https://pylint.org/) + `ast` — static analysis tools
- [Rich](https://rich.readthedocs.io/) — terminal rendering
- [Click](https://click.palletsprojects.com/) — CLI
