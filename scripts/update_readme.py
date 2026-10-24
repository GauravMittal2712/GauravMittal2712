"""Fills README.md between the PROJECTS markers with your public GitHub repos."""
import html, json, os, re, urllib.request

USER = os.environ.get("GH_USER", "GauravMittal2712")
TOKEN = os.environ.get("GITHUB_TOKEN")
MAX_REPOS = 6
START, END = "<!--PROJECTS:START-->", "<!--PROJECTS:END-->"


def fetch_repos():
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "readme-updater"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
        return json.load(r)


def pick(repos):
    ok = [r for r in repos
          if not r["fork"] and not r["archived"] and r["name"].lower() != USER.lower()]
    # repos tagged with the "featured" topic first, then stars, then most recent push
    ok.sort(key=lambda r: ("featured" in r.get("topics", []), r["stargazers_count"], r["pushed_at"]),
            reverse=True)
    return ok[:MAX_REPOS]


def card(r):
    desc = html.escape(r["description"] or "No description yet.")
    tags = []
    if r.get("language"):
        tags.append(r["language"])
    tags += [t for t in r.get("topics", []) if t != "featured"][:4]
    chips = " ".join(f"<code>{html.escape(t)}</code>" for t in tags)
    stars = f" &nbsp;⭐ {r['stargazers_count']}" if r["stargazers_count"] else ""
    return (f'<td width="50%" valign="top">\n\n'
            f'### 📦 [{r["name"]}]({r["html_url"]})\n'
            f'{desc}\n\n{chips}{stars}\n\n</td>')


def build(repos):
    if not repos:
        return "_Projects are on my GitHub profile, take a look at my repositories._"
    cells = [card(r) for r in repos]
    rows = []
    for i in range(0, len(cells), 2):
        pair = cells[i:i + 2]
        if len(pair) == 1:
            pair.append('<td width="50%"></td>')
        rows.append("<tr>\n" + "\n".join(pair) + "\n</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def main():
    with open("README.md", encoding="utf-8") as f:
        text = f.read()
    block = f"{START}\n{build(pick(fetch_repos()))}\n{END}"
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    if new != text:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new)
        print("README updated")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
