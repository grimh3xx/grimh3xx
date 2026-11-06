"""Renders assets/stats.svg and assets/langs.svg from the GitHub GraphQL API.

Runs in the stats workflow with the default GITHUB_TOKEN, so only public data is used.
"""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "grimh3xx")
OUT = Path(__file__).resolve().parent.parent / "assets"
GREEN = "#2BFF88"
MONO = "'JetBrains Mono','Fira Code',Consolas,Menlo,monospace"
SANS = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
SKIP_LANGS = {"Makefile", "Batchfile", "CMake", "PowerShell", "Dockerfile"}

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def streaks(weeks):
    days = [d for w in weeks for d in w["contributionDays"]]
    today = dt.date.today().isoformat()
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(days):
        if d["contributionCount"]:
            current += 1
        elif d["date"] != today:  # today without commits yet doesn't break the streak
            break
    return current, longest


def frame(w, h, title, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="#0B110E" stroke="{GREEN}" stroke-opacity="0.28"/>
<text x="24" y="38" fill="{GREEN}" font-family="{MONO}" font-size="16" font-weight="700">{escape(title)}</text>
{body}
</svg>
'''


def stats_svg(u):
    c = u["contributionsCollection"]
    cur, longest = streaks(c["contributionCalendar"]["weeks"])
    rows = [
        ("Contributions (12 mo)", c["contributionCalendar"]["totalContributions"]),
        ("Commits", c["totalCommitContributions"] + c["restrictedContributionsCount"]),
        ("Pull requests", c["totalPullRequestContributions"]),
        ("Issues", c["totalIssueContributions"]),
        ("Public repos", u["repositories"]["totalCount"]),
        ("Stars earned", sum(n["stargazerCount"] for n in u["repositories"]["nodes"])),
        ("Current streak", f"{cur} days"),
        ("Longest streak", f"{longest} days"),
    ]
    body = []
    for i, (label, value) in enumerate(rows):
        x = 24 + (i % 2) * 220
        y = 78 + (i // 2) * 34
        body.append(
            f'<text x="{x}" y="{y}" fill="#9BA7B4" font-family="{SANS}" font-size="13">{escape(label)}</text>'
            f'<text x="{x + 196}" y="{y}" text-anchor="end" fill="#E6EDF3" font-family="{MONO}" font-size="14" font-weight="700">{escape(str(value))}</text>'
        )
    return frame(460, 210, "$ github --stats", "".join(body))


def langs_svg(u):
    totals, colors = {}, {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            if name in SKIP_LANGS:
                continue
            totals[name] = totals.get(name, 0) + e["size"]
            colors[name] = e["node"]["color"] or GREEN
    top = sorted(totals.items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in top) or 1
    bar, x, legend = [], 24.0, []
    for i, (name, size) in enumerate(top):
        seg = 412 * size / total
        bar.append(f'<rect x="{x:.1f}" y="58" width="{seg:.1f}" height="10" fill="{colors[name]}"/>')
        x += seg
        lx = 24 + (i % 2) * 210
        ly = 100 + (i // 2) * 30
        legend.append(
            f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{colors[name]}"/>'
            f'<text x="{lx + 16}" y="{ly}" fill="#C9D1D9" font-family="{SANS}" font-size="13">{escape(name)}</text>'
            f'<text x="{lx + 186}" y="{ly}" text-anchor="end" fill="#9BA7B4" font-family="{MONO}" font-size="12.5">{100 * size / total:.1f}%</text>'
        )
    body = (
        '<clipPath id="bar"><rect x="24" y="58" width="412" height="10" rx="5"/></clipPath>'
        f'<g clip-path="url(#bar)">{"".join(bar)}</g>{"".join(legend)}'
    )
    return frame(460, 210, "$ github --languages", body)


if __name__ == "__main__":
    user = fetch()
    OUT.mkdir(exist_ok=True)
    (OUT / "stats.svg").write_text(stats_svg(user), encoding="utf-8")
    (OUT / "langs.svg").write_text(langs_svg(user), encoding="utf-8")
