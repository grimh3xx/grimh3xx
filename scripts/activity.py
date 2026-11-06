"""Rewrites the activity block in README.md with the latest public GitHub events."""
import datetime as dt
import json
import os
import re
import urllib.request
from pathlib import Path

USER = os.environ.get("GH_USER", "grimh3xx")
README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!--ACTIVITY:START-->", "<!--ACTIVITY:END-->"
LIMIT = 6


def fetch():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/events/public?per_page=100",
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def ago(ts):
    delta = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    days = delta.days
    if days >= 60:
        return f"{days // 30} months ago"
    if days >= 1:
        return f"{days} day{'s' * (days > 1)} ago"
    hours = delta.seconds // 3600
    return f"{hours} hour{'s' * (hours != 1)} ago" if hours else "just now"


def describe(e):
    repo = e["repo"]["name"]
    if repo.lower() == f"{USER}/{USER}".lower():
        return None
    link = f"[**{repo.split('/')[1]}**](https://github.com/{repo})"
    p = e.get("payload", {})
    kind = e["type"]
    if kind == "PushEvent":
        return f"🔨 Pushed to {link}"
    if kind == "ReleaseEvent" and p.get("action") == "published":
        rel = p.get("release", {})
        return f"🚀 Released [{rel.get('tag_name', '')}]({rel.get('html_url', '')}) of {link}"
    if kind == "CreateEvent" and p.get("ref_type") == "repository":
        return f"✨ Created {link}"
    if kind == "PublicEvent":
        return f"🔓 Open-sourced {link}"
    if kind == "PullRequestEvent" and p.get("action") in ("opened", "closed"):
        pr = p.get("pull_request", {})
        verb = "Merged" if pr.get("merged") else ("Opened" if p["action"] == "opened" else None)
        return verb and f"🔀 {verb} PR [#{pr.get('number')}]({pr.get('html_url')}) in {link}"
    if kind == "WatchEvent":
        return f"⭐ Starred {link}"
    return None


def main():
    lines, seen = [], set()
    for e in sorted(fetch(), key=lambda e: e["created_at"], reverse=True):
        text = describe(e)
        if not text or text in seen:  # collapse repeated pushes to the same repo
            continue
        seen.add(text)
        lines.append(f"- {text} <sub>· {ago(e['created_at'])}</sub>")
        if len(lines) == LIMIT:
            break
    block = "\n".join(lines) if lines else "_No public activity in the last 90 days._"
    readme = README.read_text(encoding="utf-8")
    new = re.sub(f"{START}.*?{END}", f"{START}\n{block}\n{END}", readme, flags=re.S)
    README.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    main()
