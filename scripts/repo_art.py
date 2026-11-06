"""Renders per-repository art: a README banner and a 1280x640 social preview (SVG; convert to PNG to upload).

Usage: python3 scripts/repo_art.py OUT_DIR
"""
import sys
from pathlib import Path

from brand import DARK, LANG_COLORS, MONO, SANS, escape, finish

REPOS = {
    "usbscope": ("usbscope", "Interactive USB device inspector for the Windows terminal", ["C++", "WinUSB", "Windows"]),
    "samcli-win-x64": ("samcli", "Steam Achievement Manager for the terminal, in pure C", ["C", "Windows", "Linux"]),
    "aircracking-win-x64": ("aircrackwin-x64", "TUI orchestrator for authorized Wi-Fi audits", ["Python", "aircrack-ng", "hashcat"]),
    "SecureArchSetup": ("SecureArchSetup", "Automated, hardened Arch Linux setup for pentesters", ["Python", "Arch Linux", "Hardening"]),
    "ExifTracer": ("ExifTracer", "EXIF metadata & GPS tracing with interactive maps", ["Python", "OSINT", "Forensics"]),
}
TH = DARK


def chips(items, x, y, fs):
    out = []
    for it in items:
        dot = LANG_COLORS.get(it)
        w = len(it) * fs * 0.6 + fs * 2 + (fs * 1.1 if dot else 0)
        h = fs * 2
        out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{h / 2:.0f}" fill="{TH["accent"]}" fill-opacity="0.08" stroke="{TH["border"]}"/>')
        tx = x + fs
        if dot:
            out.append(f'<circle cx="{tx + fs * 0.3:.0f}" cy="{y + h / 2:.0f}" r="{fs * 0.3:.1f}" fill="{dot}"/>')
            tx += fs * 1.1
        out.append(f'<text x="{tx:.0f}" y="{y + h / 2 + fs * 0.36:.0f}" font-family="{MONO}" font-size="{fs}" fill="{TH["text"]}">{escape(it)}</text>')
        x += w + fs * 0.7
    return "".join(out)


def base(w, h, inner):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{TH["bg"]}"/><stop offset="1" stop-color="{TH["bg2"]}"/></linearGradient>
<linearGradient id="brand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{TH["accent"]}"/><stop offset="1" stop-color="{TH["accent2"]}"/></linearGradient>
<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{TH["grid"]}" fill-opacity="0.16"/></pattern>
<radialGradient id="glow" cx="0.2" cy="0.1" r="0.8"><stop offset="0" stop-color="{TH["accent"]}" stop-opacity="0.2"/><stop offset="1" stop-color="{TH["accent"]}" stop-opacity="0"/></radialGradient>
<filter id="soft" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
<clipPath id="r"><rect width="{w}" height="{h}" rx="16"/></clipPath>
</defs>
<g clip-path="url(#r)">
<rect width="{w}" height="{h}" fill="url(#bg)"/><rect width="{w}" height="{h}" fill="url(#dots)"/><rect width="{w}" height="{h}" fill="url(#glow)"/>
{inner}
</g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="{TH["border"]}"/>
</svg>
'''


def wordmark(x, y, name, size):
    t = f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="800" letter-spacing="-1">{escape(name)}</text>'
    return f'<g fill="{TH["accent"]}" opacity="0.35" filter="url(#soft)">{t}</g><g fill="url(#brand)">{t}</g>'


def readme_banner(name, tagline, tags):
    w, h = 1000, 220
    inner = (
        f'<text x="48" y="58" font-family="{MONO}" font-size="12" letter-spacing="3" fill="{TH["muted"]}">'
        f'<tspan fill="{TH["accent2"]}">●</tspan>  CENTRALTECH  ·  GRIMH3XX</text>'
        + wordmark(46, 122, name, 54)
        + f'<text x="48" y="158" font-family="{SANS}" font-size="18" fill="{TH["text"]}">{escape(tagline)}</text>'
        + chips(tags, 48, 176, 12)
    )
    return finish(base(w, h, inner), {("JBM", 400), ("JBM", 800), ("INT", 400)})


def social(name, tagline, tags):
    w, h = 1280, 640
    size = min(110, int(2000 / max(len(name), 8)))
    inner = (
        f'<text x="96" y="150" font-family="{MONO}" font-size="20" letter-spacing="4" fill="{TH["muted"]}">'
        f'<tspan fill="{TH["accent2"]}">●</tspan>  CENTRALTECH  ·  GRIMH3XX</text>'
        + wordmark(90, 300, name, size)
        + f'<text x="96" y="376" font-family="{SANS}" font-size="36" fill="{TH["text"]}">{escape(tagline)}</text>'
        + chips(tags, 96, 420, 22)
        + f'<path d="M96 540H{w - 96}" stroke="{TH["border"]}"/>'
        + f'<text x="96" y="584" font-family="{MONO}" font-size="22" fill="{TH["muted"]}">github.com/grimh3xx</text>'
        + f'<text x="{w - 96}" y="584" text-anchor="end" font-family="{MONO}" font-size="22" fill="{TH["muted"]}">centraltechpc.com</text>'
    )
    return finish(base(w, h, inner), {("JBM", 400), ("JBM", 800), ("INT", 400)})


if __name__ == "__main__":
    out = Path(sys.argv[1])
    for repo, (name, tagline, tags) in REPOS.items():
        d = out / repo
        d.mkdir(parents=True, exist_ok=True)
        (d / "banner.svg").write_text(readme_banner(name, tagline, tags), encoding="utf-8")
        (d / "social-preview.svg").write_text(social(name, tagline, tags), encoding="utf-8")
