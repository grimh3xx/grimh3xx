"""Renders per-repository art: a README banner (SVG) and a social preview (SVG, 1280x640; convert to PNG to upload).

Usage: python3 scripts/repo_art.py OUT_DIR
"""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from render import GREEN, MONO, SANS, LANG_COLORS, wrap

REPOS = {
    "usbscope": ("usbscope", "Interactive USB device inspector for the Windows terminal", ["C++", "WinUSB", "Windows"]),
    "samcli-win-x64": ("samcli", "Steam Achievement Manager for the terminal, in pure C", ["C", "Windows", "Linux"]),
    "aircracking-win-x64": ("aircrackwin-x64", "TUI orchestrator for authorized Wi-Fi audits", ["Python", "aircrack-ng", "hashcat"]),
    "SecureArchSetup": ("SecureArchSetup", "Automated, hardened Arch Linux setup for pentesters", ["Python", "Arch Linux", "Hardening"]),
    "ExifTracer": ("ExifTracer", "EXIF metadata & GPS tracing with interactive maps", ["Python", "OSINT", "Forensics"]),
}


def chips(items, x, y, fs, gap):
    out = []
    for it in items:
        w = len(it) * fs * 0.62 + fs * 2.2
        dot = LANG_COLORS.get(it)
        pad = fs * 1.1
        if dot:
            out.append(f'<circle cx="{x + pad:.0f}" cy="{y + fs * 0.95:.0f}" r="{fs * 0.32:.1f}" fill="{dot}"/>')
            w += fs * 0.9
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{fs * 1.9:.0f}" rx="{fs * 0.95:.0f}" fill="none" stroke="{GREEN}" stroke-opacity="0.4"/>')
        out.append(f'<text x="{x + pad + (fs * 0.9 if dot else 0):.0f}" y="{y + fs * 1.3:.0f}" fill="#C9D1D9" font-family="{MONO}" font-size="{fs}">{escape(it)}</text>')
        x += w + gap
    return "".join(out)


def base(w, h, inner):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A0F0D"/><stop offset="1" stop-color="#05080A"/></linearGradient>
<pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="{GREEN}" stroke-opacity="0.05"/></pattern>
<radialGradient id="glow" cx="0.15" cy="0.2" r="0.7"><stop offset="0" stop-color="{GREEN}" stop-opacity="0.14"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
<filter id="neon" x="-5%" y="-30%" width="110%" height="160%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="r"><rect width="{w}" height="{h}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#r)">
<rect width="{w}" height="{h}" fill="url(#bg)"/><rect width="{w}" height="{h}" fill="url(#grid)"/><rect width="{w}" height="{h}" fill="url(#glow)"/>
{inner}
</g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{GREEN}" stroke-opacity="0.25"/>
</svg>
'''


def readme_banner(name, tagline, tags):
    w, h = 1000, 220
    inner = (
        f'<text x="48" y="64" fill="#6B7A75" font-family="{MONO}" font-size="15">grimh3xx@centraltech:~$ <tspan fill="#E6EDF3">./{escape(name)}</tspan></text>'
        f'<text x="46" y="128" fill="{GREEN}" font-family="{MONO}" font-size="50" font-weight="700" filter="url(#neon)">{escape(name)}</text>'
        f'<text x="48" y="162" fill="#9BA7B4" font-family="{SANS}" font-size="18">{escape(tagline)}</text>'
        + chips(tags, 48, 180, 12, 10)
        + f'<text x="{w - 40}" y="64" text-anchor="end" fill="#6B7A75" font-family="{MONO}" font-size="13">CentralTech · github.com/grimh3xx</text>'
    )
    return base(w, h, inner)


def social(name, tagline, tags):
    w, h = 1280, 640
    lines = wrap(tagline, 54)
    inner = (
        f'<path d="M0 64H{w}" stroke="{GREEN}" stroke-opacity="0.15"/>'
        '<circle cx="40" cy="32" r="9" fill="#FF5F57"/><circle cx="68" cy="32" r="9" fill="#FEBC2E"/><circle cx="96" cy="32" r="9" fill="#28C840"/>'
        f'<text x="{w / 2}" y="39" text-anchor="middle" fill="#6B7A75" font-family="{MONO}" font-size="20">grimh3xx@centraltech: ~</text>'
        f'<text x="88" y="190" fill="#6B7A75" font-family="{MONO}" font-size="26">$ <tspan fill="#E6EDF3">./{escape(name)}</tspan></text>'
        f'<text x="84" y="300" fill="{GREEN}" font-family="{MONO}" font-size="{min(96, int(1900 / max(len(name), 8)))}" font-weight="700" filter="url(#neon)">{escape(name)}</text>'
        + "".join(f'<text x="88" y="{372 + i * 44}" fill="#C9D1D9" font-family="{SANS}" font-size="34">{escape(l)}</text>' for i, l in enumerate(lines))
        + chips(tags, 88, 372 + len(lines) * 44 + 24, 20, 14)
        + f'<text x="{w - 64}" y="{h - 48}" text-anchor="end" fill="#6B7A75" font-family="{MONO}" font-size="22">github.com/grimh3xx · centraltechpc.com</text>'
    )
    return base(w, h, inner)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for repo, (name, tagline, tags) in REPOS.items():
        d = out / repo
        d.mkdir(parents=True, exist_ok=True)
        (d / "banner.svg").write_text(readme_banner(name, tagline, tags), encoding="utf-8")
        (d / "social-preview.svg").write_text(social(name, tagline, tags), encoding="utf-8")
