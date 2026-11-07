"""Renders assets/releases.svg (+ -light): the most recent releases across the public repos,
so the profile shows which projects are actively shipped.
"""
import datetime as dt
import json
import os
import re
import urllib.request
from pathlib import Path

from brand import MONO, SANS, THEMES, escape, finish

USER = os.environ.get("GH_USER", "grimh3xx")
OUT = Path(__file__).resolve().parent.parent / "assets"
LIMIT = 5

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      nodes {
        name
        description
        releases(first: 5, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes { tagName publishedAt isDraft isPrerelease }
        }
      }
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
    out = []
    for repo in data["data"]["user"]["repositories"]["nodes"]:
        for rel in repo["releases"]["nodes"]:
            if rel["isDraft"] or not rel["publishedAt"]:
                continue
            out.append({"repo": repo["name"], "desc": repo["description"] or "", "tag": rel["tagName"],
                        "pre": rel["isPrerelease"], "at": dt.datetime.fromisoformat(rel["publishedAt"].replace("Z", "+00:00"))})
    out.sort(key=lambda r: r["at"], reverse=True)
    # one row per repo: its newest release
    seen, rows = set(), []
    for r in out:
        if r["repo"] not in seen:
            seen.add(r["repo"])
            rows.append(r)
    return rows[:LIMIT]


def ago(t):
    days = (dt.datetime.now(dt.timezone.utc) - t).days
    if days < 1:
        return "today"
    if days < 30:
        return f"{days} day{'s' if days > 1 else ''} ago"
    months = days // 30
    return f"{months} month{'s' if months > 1 else ''} ago"


def short(text, n):
    """First clause of the description, cut to n characters."""
    text = re.split(r"[:.(]\s|\s\(", text.strip(), maxsplit=1)[0].strip()
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def card(rows, th):
    w, row_h, top = 900, 46, 74
    h = top + row_h * len(rows) + 14
    p = [
        f'<text x="26" y="40" font-family="{MONO}" font-size="15" font-weight="700" fill="{th["title"]}">'
        f'<tspan fill="{th["accent2"]}">$</tspan> git tag --sort=-creatordate</text>',
        f'<text x="{w - 26}" y="40" text-anchor="end" font-family="{SANS}" font-size="12" fill="{th["muted"]}">latest releases</text>',
        f'<path d="M26 56H{w - 26}" stroke="{th["border"]}"/>',
    ]
    for i, r in enumerate(rows):
        y = top + i * row_h + 18
        tag = r["tag"]
        tw = len(tag) * 7.2 + 18
        name_w = len(r["repo"]) * 8.7
        p.append(
            f'<circle cx="32" cy="{y - 5}" r="4" fill="{th["accent2"] if i == 0 else th["accent"]}"/>'
            f'<text x="46" y="{y}" font-family="{MONO}" font-size="14.5" font-weight="700" fill="{th["title"]}">{escape(r["repo"])}</text>'
            f'<rect x="{56 + name_w:.0f}" y="{y - 15}" width="{tw:.0f}" height="21" rx="10.5" fill="{th["accent"]}" fill-opacity="0.12" stroke="{th["accent"]}" stroke-opacity="0.4"/>'
            f'<text x="{56 + name_w + tw / 2:.0f}" y="{y - 1}" text-anchor="middle" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{th["accent2"]}">{escape(tag)}</text>'
            f'<text x="{70 + name_w + tw:.0f}" y="{y}" font-family="{SANS}" font-size="13" fill="{th["muted"]}">{escape(short(r["desc"], 64))}</text>'
            f'<text x="{w - 26}" y="{y}" text-anchor="end" font-family="{SANS}" font-size="12" fill="{th["dim"]}">{ago(r["at"])}</text>'
        )
        if i < len(rows) - 1:
            p.append(f'<path d="M46 {y + 16}H{w - 26}" stroke="{th["border"]}" stroke-dasharray="2 4"/>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Latest releases">
<defs><linearGradient id="top" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{th["accent"]}"/><stop offset="1" stop-color="{th["accent2"]}"/></linearGradient>
<clipPath id="c"><rect width="{w}" height="{h}" rx="12"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{th["panel"]}"/><rect width="{w}" height="2" fill="url(#top)"/></g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{th["border"]}"/>
{"".join(p)}
</svg>
'''
    return finish(svg, {("JBM", 700), ("INT", 400)})


if __name__ == "__main__":
    rows = fetch()
    if rows:
        OUT.mkdir(exist_ok=True)
        for th in THEMES:
            (OUT / f"releases{th['suffix']}.svg").write_text(card(rows, th), encoding="utf-8")
