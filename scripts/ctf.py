"""Renders the Hack The Box and TryHackMe rank cards (assets/htb*.svg, assets/thm*.svg)
and the README block between the CTF markers.

Each platform is fetched live when possible and cached in data/<platform>.json, so a
failed or blocked request keeps the last known numbers instead of breaking the card.

  HTB_TOKEN  Hack The Box App Token (repo secret). Without it the cache is used.
  THM_USER   TryHackMe username. Without it the TryHackMe card is skipped.
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

from brand import MONO, SANS, THEMES, escape, finish

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
DATA = ROOT / "data"
README = ROOT / "README.md"
ICONS = json.loads((Path(__file__).parent / "icons.json").read_text())
UA = "Mozilla/5.0 (X11; Linux x86_64) grimh3xx-profile-card"
HTB_API = ("https://labs.hackthebox.com/api/v4", "https://www.hackthebox.com/api/v4")


def log(msg):
    print(f"[ctf] {msg}", file=sys.stderr)


def get_json(url, token=None):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as r:
        return json.load(r)


def cached(name, fetch):
    path = DATA / f"{name}.json"
    try:
        data = fetch()
    except Exception as e:  # network, auth, bot checkpoints: fall back to the cache
        log(f"{name}: live fetch failed ({type(e).__name__}: {e})")
        data = None
    if data:
        DATA.mkdir(exist_ok=True)
        data["fetched"] = dt.date.today().isoformat()
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        log(f"{name}: updated")
        return data
    if path.exists():
        log(f"{name}: using cache")
        return json.loads(path.read_text(encoding="utf-8"))
    return None


# ------------------------------------------------------------------ fetchers
def fetch_htb():
    token = os.environ.get("HTB_TOKEN", "").strip()
    if not token:
        log("htb: HTB_TOKEN not set")
        return None
    last = None
    for base in HTB_API:
        try:
            uid = get_json(f"{base}/user/info", token)["info"]["id"]
            p = get_json(f"{base}/user/profile/basic/{uid}", token)["profile"]
            break
        except Exception as e:
            last = e
    else:
        raise last
    challenges = None
    try:
        c = get_json(f"{base}/user/profile/progress/challenges/{uid}", token)["profile"]["challenge_owns"]
        challenges = c.get("solved")
    except Exception as e:
        log(f"htb: challenge progress unavailable ({type(e).__name__})")
    log(f"htb: profile fields: {', '.join(sorted(p))}")
    return {
        "id": uid, "name": p.get("name"), "rank": p.get("rank"), "next_rank": p.get("next_rank"),
        "progress": p.get("current_rank_progress") or 0, "ranking": p.get("ranking"),
        "points": p.get("points"), "system_owns": p.get("system_owns"), "user_owns": p.get("user_owns"),
        "bloods": (p.get("user_bloods") or 0) + (p.get("system_bloods") or 0),
        "respects": p.get("respects"), "challenges": challenges,
    }


def fetch_thm(user):
    d = get_json(f"https://tryhackme.com/api/v2/public-profile?username={user}")["data"]
    return {
        "name": d.get("username", user), "rank": d.get("rank"), "level": d.get("level"),
        "top": d.get("topPercentage"), "rooms": d.get("completedRoomsNumber"),
        "badges": d.get("badgesNumber"), "streak": d.get("streak"),
    }


# ------------------------------------------------------------------ rendering
def fmt(v, prefix=""):
    if v in (None, "", 0, "0") and prefix == "#":
        return "—"
    if v is None or v == "":
        return "—"
    if isinstance(v, (int, float)):
        return f"{prefix}{v:,.0f}"
    return f"{prefix}{v}"


def pill(x_right, y, text, color):
    tw = len(text) * 6.6 + 26
    x = x_right - tw
    return (f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="22" rx="11" fill="{color}" fill-opacity="0.1" stroke="{color}" stroke-opacity="0.35"/>'
            f'<circle cx="{x + 11:.1f}" cy="{y + 11}" r="3" fill="{color}"/>'
            f'<text x="{x + 19:.1f}" y="{y + 15}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="{color}">{escape(text)}</text>')


def card(th, *, icon, title, handle, badge, metrics, bar, updated):
    w, h = 440, 212
    s = 26 / 24
    body = [
        f'<rect x="22" y="22" width="44" height="44" rx="10" fill="{th["accent"]}" fill-opacity="0.12" stroke="{th["accent"]}" stroke-opacity="0.35"/>'
        f'<path transform="translate(31 31) scale({s:.3f})" d="{ICONS[icon]["path"]}" fill="url(#brand)"/>',
        f'<text x="80" y="41" font-family="{MONO}" font-size="17" font-weight="700" fill="{th["title"]}">{escape(title)}</text>',
        f'<text x="80" y="60" font-family="{SANS}" font-size="12.5" fill="{th["muted"]}">{escape(handle)}</text>',
        pill(w - 20, 24, badge.upper(), th["accent2"]),
        f'<path d="M22 84H{w - 22}" stroke="{th["border"]}"/>',
    ]
    # columns sized to their content, leftover space shared evenly between them
    need = [max(len(v) * 12.7, len(l) * 6.4) for v, l in metrics]
    gap = (w - 44 - sum(need)) / (len(metrics) - 1)
    x = 22
    for (val, label), n in zip(metrics, need):
        body.append(f'<text x="{x:.0f}" y="122" font-family="{MONO}" font-size="21" font-weight="700" fill="{th["title"]}">{escape(val)}</text>'
                    f'<text x="{x:.0f}" y="141" font-family="{SANS}" font-size="11.5" fill="{th["muted"]}">{escape(label)}</text>')
        x += n + gap
    label, pct = bar
    pct = max(0.0, min(100.0, float(pct or 0)))
    bw = w - 44
    body.append(
        f'<text x="22" y="174" font-family="{SANS}" font-size="11.5" fill="{th["muted"]}">{escape(label)}</text>'
        f'<text x="{w - 22}" y="174" text-anchor="end" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{th["text"]}">{pct:.0f}%</text>'
        f'<rect x="22" y="183" width="{bw}" height="6" rx="3" fill="{th["border"]}"/>'
        f'<rect x="22" y="183" width="{max(6, bw * pct / 100):.1f}" height="6" rx="3" fill="url(#brand)"/>'
        f'<text x="{w - 22}" y="60" text-anchor="end" font-family="{SANS}" font-size="10.5" fill="{th["dim"]}">updated {escape(updated)}</text>'
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)} profile">
<defs><linearGradient id="brand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{th["accent"]}"/><stop offset="1" stop-color="{th["accent2"]}"/></linearGradient>
<clipPath id="c"><rect width="{w}" height="{h}" rx="12"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{th["panel"]}"/><rect width="{w}" height="2" fill="url(#brand)"/></g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{th["border"]}"/>
{"".join(body)}
</svg>
'''
    return finish(svg, {("JBM", 700), ("INT", 400)})


def updated(d):
    return f"{dt.date.fromisoformat(d['fetched']):%d %b %Y}"


def htb_card(d, th):
    third = ("challenges", fmt(d.get("challenges"))) if d.get("challenges") is not None else ("user owns", fmt(d.get("user_owns")))
    nxt = d.get("next_rank")
    return card(
        th, icon="hackthebox", title="Hack The Box", handle=f"@{d['name']}", badge=d.get("rank") or "unranked",
        metrics=[(fmt(d.get("ranking"), "#"), "global rank"), (fmt(d.get("points")), "points"),
                 (fmt(d.get("system_owns")), "machines owned"), (third[1], third[0])],
        bar=(f"progress to {nxt}" if nxt else "rank progress", d.get("progress")), updated=updated(d),
    )


def thm_card(d, th):
    top = d.get("top")
    return card(
        th, icon="tryhackme", title="TryHackMe", handle=f"@{d['name']}",
        badge=f"level {d.get('level', '?')}",
        metrics=[(fmt(d.get("rank"), "#"), "global rank"), (fmt(d.get("rooms")), "rooms completed"),
                 (fmt(d.get("badges")), "badges"), (f"{fmt(d.get('streak'))}d", "streak")],
        bar=(f"top {top}% of all users" if top is not None else "global percentile", 100 - float(top) if top is not None else 0),
        updated=updated(d),
    )


def picture(name, alt, href):
    img = (f'<picture><source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg"/>'
           f'<img src="assets/{name}.svg" width="49%" alt="{alt}"/></picture>')
    return f'  <a href="{href}">{img}</a>'


def main():
    OUT.mkdir(exist_ok=True)
    cells = []
    htb = cached("htb", fetch_htb)
    # a fresh account (0 points, no owns) is held back until there is progress to show
    if htb and (htb.get("points") or htb.get("system_owns") or htb.get("user_owns") or htb.get("challenges")):
        for th in THEMES:
            (OUT / f"htb{th['suffix']}.svg").write_text(htb_card(htb, th), encoding="utf-8")
        cells.append(picture("htb", f"Hack The Box: {htb.get('rank')}", f"https://app.hackthebox.com/profile/{htb['id']}"))
    user = os.environ.get("THM_USER", "").strip()
    thm = cached("thm", lambda: fetch_thm(user)) if user else None
    if thm and (thm.get("rooms") or thm.get("badges")):
        for th in THEMES:
            (OUT / f"thm{th['suffix']}.svg").write_text(thm_card(thm, th), encoding="utf-8")
        cells.append(picture("thm", "TryHackMe profile", f"https://tryhackme.com/p/{thm['name']}"))

    block = '\n## Hacking platforms\n\n<p align="center">\n' + "\n".join(cells) + "\n</p>\n\n" if cells else "\n"
    text = README.read_text(encoding="utf-8")
    new = re.sub(r"(<!--CTF:START-->).*?(<!--CTF:END-->)", lambda m: m.group(1) + block + m.group(2), text, flags=re.S)
    if new != text:
        README.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    main()
