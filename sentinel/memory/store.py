import json
from datetime import datetime
from pathlib import Path

PREFERENCES_FILE = Path("preferences.json")


def load() -> dict:
    if not PREFERENCES_FILE.exists():
        return {"dismissed": [], "style_preferences": []}
    with open(PREFERENCES_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict):
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_dismissed(finding: str, note: str):
    data = load()
    data["dismissed"].append({
        "finding": finding,
        "note": note,
        "timestamp": datetime.now().isoformat(),
    })
    _save(data)


def add_preference(preference: str):
    data = load()
    data["style_preferences"].append({
        "preference": preference,
        "timestamp": datetime.now().isoformat(),
    })
    _save(data)


def build_system_prompt_context() -> str:
    data = load()
    parts = []

    if data["style_preferences"]:
        prefs = "\n".join(f"- {p['preference']}" for p in data["style_preferences"])
        parts.append(f"Engineer style preferences (follow these when writing findings):\n{prefs}")

    if data["dismissed"]:
        dismissed_lines = []
        for d in data["dismissed"]:
            line = f"- {d['finding']}"
            if d.get("note"):
                line += f" (reason: {d['note']})"
            dismissed_lines.append(line)
        parts.append(
            "The engineer has dismissed the following types of findings in past reviews. "
            "Do not raise similar issues unless the severity is significantly higher:\n"
            + "\n".join(dismissed_lines)
        )

    return "\n\n".join(parts)
