import subprocess
import json


def run_pylint(filepath: str, content: str) -> dict:
    """
    Writes content to a temp file and runs pylint on it.
    Returns structured findings.
    """
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [
                "pylint",
                tmp_path,
                "--output-format=json",
                "--disable=C0114,C0115,C0116"  # ignore missing docstring warnings
            ],
            capture_output=True,
            text=True
        )
        findings = json.loads(result.stdout) if result.stdout.strip() else []
    except Exception as e:
        findings = [{"error": str(e)}]
    finally:
        os.unlink(tmp_path)  # delete the temp file

    return {
        "file": filepath,
        "findings": [
            {
                "line": f.get("line"),
                "message": f.get("message"),
                "symbol": f.get("symbol"),
                "type": f.get("type")
            }
            for f in findings
        ]
    }