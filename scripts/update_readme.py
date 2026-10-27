"""Refresh the 'Recently updated' section of README.md from the GitHub API."""
import json
import os
import re
import urllib.request

USER = "rigoordonio"
README = "README.md"
LIMIT = 5


def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=30",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def render(repos):
    rows = []
    for r in repos:
        if r["fork"] or r["name"] == USER:
            continue
        lang = r["language"] or "—"
        desc = (r["description"] or "").replace("|", "\\|")
        rows.append(f"| [{r['name']}]({r['html_url']}) | {lang} | {desc} | {r['pushed_at'][:10]} |")
        if len(rows) == LIMIT:
            break
    header = "| Repo | Language | Description | Last push |\n|---|---|---|---|"
    return header + "\n" + "\n".join(rows)


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    new = re.sub(
        r"(<!-- RECENT:START -->).*?(<!-- RECENT:END -->)",
        lambda m: f"{m.group(1)}\n{render(fetch_repos())}\n{m.group(2)}",
        text,
        flags=re.S,
    )
    if new != text:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new)


if __name__ == "__main__":
    main()
