from github import Github
from sentinel.config import GITHUB_TOKEN

def parse_repo_url(url: str) -> str:
    """
    Converts a full GitHub URL to owner/repo format.
    e.g. https://github.com/torvalds/linux -> torvalds/linux
    """
    url = url.rstrip("/")
    parts = url.split("github.com/")
    if len(parts) != 2:
        raise ValueError(f"Invalid GitHub URL: {url}")
    return parts[1]


def get_repo_files(repo_url: str, extensions: list[str] = [".py"]) -> list[dict]:
    """
    Fetches all files from a GitHub repo matching the given extensions.
    Returns a list of dicts with filename and content.
    """
    g = Github(GITHUB_TOKEN)
    repo_name = parse_repo_url(repo_url)
    repo = g.get_repo(repo_name)

    files = []
    contents = repo.get_contents("")

    while contents:
        file = contents.pop(0)
        if file.type == "dir":
            contents.extend(repo.get_contents(file.path))
        elif any(file.path.endswith(ext) for ext in extensions):
            files.append({
                "path": file.path,
                "content": file.decoded_content.decode("utf-8")
            })

    return files