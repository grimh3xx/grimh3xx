"""Renders assets/activity.svg (+ -light): a single dashboard with contribution metrics,
a 12-month weekly contribution chart and top languages, from the GitHub GraphQL API.

Runs in the update workflow with the default GITHUB_TOKEN, so only public data is used
(plus private contribution counts if the user enabled them on their profile).
"""
import datetime as dt
import json
import os
import urllib.request
from pathlib import Path

from brand import LANG_COLORS, MONO, SANS, THEMES, escape, finish

USER = os.environ.get("GH_USER", "grimh3xx")
OUT = Path(__file__).resolve().parent.parent / "assets"
SKIP_LANGS = {"Makefile", "Batchfile", "CMake", "PowerShell", "Dockerfile"}

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
      }
    }
    contributionsCollection {
      totalCommitContributions
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


def streaks(days):
    today = dt.date.today().isoformat()
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(days):
        if d["contributionCount"]:
            current += 1
        elif d["date"] != today:  # no commits yet today doesn't break the streak
            break
    return current, longest


def languages(u):
    totals, colors = {}, {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            if name in SKIP_LANGS:
                continue
            totals[name] = totals.get(name, 0) + e["size"]
            colors[name] = LANG_COLORS.get(name) or e["node"]["color"] or "#888"
    top = sorted(totals.items(), key=lambda kv: -kv[1])[:5]
    top = [kv for kv in top if kv[1] >= 0.01 * sum(totals.values())]
    total = sum(v for _, v in top) or 1
    return [(n, v / total, colors[n]) for n, v in top]


def dashboard(u, th):
    w, h = 900, 300
    c = u["contributionsCollection"]
    weeks = c["contributionCalendar"]["weeks"]
    days = [d for wk in weeks for d in wk["contributionDays"]]
    cur, longest = streaks(days)
    metrics = [
        (c["contributionCalendar"]["totalContributions"], "contributions"),
        (c["totalCommitContributions"] + c["restrictedContributionsCount"], "commits"),
        (f"{cur}d", "current streak"),
        (f"{longest}d", "longest streak"),
        (u["repositories"]["totalCount"], "public repos"),
        (sum(n["stargazerCount"] for n in u["repositories"]["nodes"]), "stars earned"),
    ]
    p = [
        f'<text x="26" y="40" font-family="{MONO}" font-size="15" font-weight="700" fill="{th["title"]}">'
        f'<tspan fill="{th["accent2"]}">$</tspan> github --activity</text>',
        f'<text x="{w - 26}" y="40" text-anchor="end" font-family="{SANS}" font-size="12" fill="{th["muted"]}">last 12 months · updated {dt.date.today():%d %b %Y}</text>',
        f'<path d="M26 58H{w - 26}" stroke="{th["border"]}"/>',
    ]
    for i, (val, label) in enumerate(metrics):
        x = 26 + (i % 2) * 140
        y = 104 + (i // 2) * 62
        p.append(f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="26" font-weight="700" fill="{th["title"]}">{escape(str(val))}</text>'
                 f'<text x="{x}" y="{y + 20}" font-family="{SANS}" font-size="12" fill="{th["muted"]}">{escape(label)}</text>')
    p.append(f'<path d="M318 78V{h - 26}" stroke="{th["border"]}"/>')

    # weekly bars
    cx0, cx1, cy0, cy1 = 346, w - 26, 84, 196
    sums = [sum(d["contributionCount"] for d in wk["contributionDays"]) for wk in weeks][-52:]
    peak = max(sums) or 1
    bw = (cx1 - cx0) / len(sums)
    for k in range(4):
        gy = cy0 + (cy1 - cy0) * k / 3
        p.append(f'<path d="M{cx0} {gy:.1f}H{cx1}" stroke="{th["border"]}" stroke-dasharray="2 4"/>')
    for i, v in enumerate(sums):
        bh = max(2.0, (cy1 - cy0) * v / peak) if v else 2.0
        op = 1
        fill = "url(#brand)" if v else th["border"]
        p.append(f'<rect x="{cx0 + i * bw + 1.2:.1f}" y="{cy1 - bh:.1f}" width="{bw - 2.4:.1f}" height="{bh:.1f}" rx="1.5" fill="{fill}" opacity="{op}"/>')
    first = dt.date.fromisoformat(weeks[-len(sums)]["contributionDays"][0]["date"])
    last_month = None
    for i in range(len(sums)):
        d = first + dt.timedelta(weeks=i)
        if d.month != last_month and i < len(sums) - 2:
            if last_month is not None:
                p.append(f'<text x="{cx0 + i * bw:.1f}" y="{cy1 + 18}" font-family="{SANS}" font-size="10.5" fill="{th["dim"]}">{d:%b}</text>')
            last_month = d.month
    p.append(f'<text x="{cx1}" y="{cy0 - 8}" text-anchor="end" font-family="{SANS}" font-size="10.5" fill="{th["dim"]}">peak {peak}/week</text>')

    # languages
    ly = 246
    p.append(f'<text x="{cx0}" y="{ly}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.5" fill="{th["muted"]}">LANGUAGES</text>')
    langs = languages(u)
    x = cx0 + 96
    bar = []
    for name, share, col in langs:
        seg = (cx1 - cx0 - 96) * share
        bar.append(f'<rect x="{x:.1f}" y="{ly - 9}" width="{seg:.1f}" height="8" fill="{col}"/>')
        x += seg
    p.append(f'<clipPath id="lb"><rect x="{cx0 + 96}" y="{ly - 9}" width="{cx1 - cx0 - 96}" height="8" rx="4"/></clipPath><g clip-path="url(#lb)">{"".join(bar)}</g>')
    x = cx0
    for name, share, col in langs:
        label = f"{name} {share * 100:.0f}%"
        p.append(f'<circle cx="{x + 4}" cy="{ly + 23}" r="4" fill="{col}"/>'
                 f'<text x="{x + 13}" y="{ly + 27}" font-family="{SANS}" font-size="12" fill="{th["text"]}">{escape(name)} '
                 f'<tspan fill="{th["muted"]}">{share * 100:.0f}%</tspan></text>')
        x += 30 + len(label) * 6.8

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="GitHub activity">
<defs><linearGradient id="brand" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{th["accent"]}"/><stop offset="1" stop-color="{th["accent2"]}"/></linearGradient>
<linearGradient id="top" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{th["accent"]}"/><stop offset="1" stop-color="{th["accent2"]}"/></linearGradient>
<clipPath id="c"><rect width="{w}" height="{h}" rx="12"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{th["panel"]}"/><rect width="{w}" height="2" fill="url(#top)"/></g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{th["border"]}"/>
{"".join(p)}
</svg>
'''
    return finish(svg, {("JBM", 700), ("INT", 400)})


if __name__ == "__main__":
    user = fetch()
    OUT.mkdir(exist_ok=True)
    for th in THEMES:
        (OUT / f"activity{th['suffix']}.svg").write_text(dashboard(user, th), encoding="utf-8")
