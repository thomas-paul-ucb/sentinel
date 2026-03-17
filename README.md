# Sentinel 🔍

> Agentic code review powered by Claude

Sentinel is an AI agent that autonomously reviews GitHub repositories. Point it at any public repo and it will scan the codebase, run static analysis, and use Claude to generate a structured, severity-ranked code review report.

## How it works

1. **Fetch** — pulls file tree and source code from a GitHub repo
2. **Analyze** — runs static analysis tools (pylint, AST) on each file
3. **Reason** — Claude agent loops over findings using tool use
4. **Report** — outputs a markdown report with ranked issues and fixes

## Tech Stack

- Python
- Claude API (tool use / agentic loop)
- GitHub API (PyGithub)
- pylint + ast (static analysis)
- Rich (terminal output)
- Click (CLI)

## Usage
```bash
python -m sentinel review https://github.com/owner/repo
```

## Setup
```bash
git clone https://github.com/thomas-paul-ucb/sentinel.git
cd sentinel
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# add your API keys to .env
```

## Environment Variables
```
ANTHROPIC_API_KEY=your_claude_api_key
GITHUB_TOKEN=your_github_token
```