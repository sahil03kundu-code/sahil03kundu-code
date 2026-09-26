import os
import requests

USERNAME = "sahil03kundu-code"
TOKEN = os.environ.get("GH_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

START_MARKER = "<!-- PROJECTS:START -->"
END_MARKER = "<!-- PROJECTS:END -->"


def get_repos():
    repos = []
    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            params={"sort": "updated", "per_page": 100, "page": page},
            headers=HEADERS,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


def build_table(repos):
    rows = []
    for repo in repos:
        if repo.get("fork") or repo.get("archived"):
            continue
        if repo["name"].lower() == USERNAME.lower():
            continue  # skip the special profile repo itself
        name = repo["name"]
        url = repo["html_url"]
        desc = (repo.get("description") or "No description yet").replace("|", "-")
        lang = repo.get("language") or "\u2014"
        stars = repo.get("stargazers_count", 0)
        rows.append(f"| [{name}]({url}) | {desc} | {lang} | \u2b50 {stars} |")

    if not rows:
        return "_No public repositories yet._"

    header = "| Project | Description | Language | Stars |\n|---|---|---|---|\n"
    return header + "\n".join(rows)


def update_readme(table_md):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    start = content.index(START_MARKER) + len(START_MARKER)
    end = content.index(END_MARKER)
    new_content = content[:start] + "\n\n" + table_md + "\n\n" + content[end:]

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    repos = get_repos()
    table_md = build_table(repos)
    update_readme(table_md)
    print(f"Updated README with {len(repos)} repos fetched.")
