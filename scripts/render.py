"""Renders the static profile assets (banner + project cards) into assets/."""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
GREEN = "#2BFF88"
MONO = "'JetBrains Mono','Fira Code',Consolas,Menlo,monospace"
SANS = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"


def banner():
    w, h, fs = 1000, 300, 19
    cw = fs * 0.6
    x0, y0, lh = 40, 86, 32
    # (prompt command, output, output colour)
    lines = [
        ("whoami", "grimh3xx — Offensive Security & AI", "#E6EDF3"),
        ("cat focus.txt", "pentesting · automation · low-level tooling in C/C++, Python & Bash", "#9BA7B4"),
        ("./build --project centraltech", "[+] building CentralTech ▸ centraltechpc.com", GREEN),
    ]
    prompt = "grimh3xx@centraltech:~$ "
    parts, defs, t, y = [], [], 0.6, y0
    for i, (cmd, out, col) in enumerate(lines):
        px = x0 + len(prompt) * cw
        dur = max(0.5, len(cmd) * 0.07)
        defs.append(
            f'<clipPath id="c{i}"><rect x="{px}" y="{y - fs}" height="{fs + 8}" width="0">'
            f'<animate attributeName="width" from="0" to="{len(cmd) * cw + 2}" begin="{t}s" dur="{dur}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(
            f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t - 0.3}s" fill="freeze"/>'
            f'<text x="{x0}" y="{y}" fill="{GREEN}" textLength="{len(prompt) * cw}" lengthAdjust="spacingAndGlyphs">{escape(prompt)}</text></g>'
            f'<text x="{px}" y="{y}" fill="#E6EDF3" clip-path="url(#c{i})" textLength="{len(cmd) * cw}" lengthAdjust="spacingAndGlyphs">{escape(cmd)}</text>'
        )
        t += dur + 0.35
        y += lh
        parts.append(
            f'<text x="{x0}" y="{y}" fill="{col}" opacity="0">{escape(out)}'
            f'<set attributeName="opacity" to="1" begin="{t}s" fill="freeze"/></text>'
        )
        t += 0.6
        y += lh + 4
    parts.append(
        f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t}s" fill="freeze"/>'
        f'<text x="{x0}" y="{y - 4}" fill="{GREEN}" textLength="{len(prompt) * cw}" lengthAdjust="spacingAndGlyphs">{escape(prompt)}</text>'
        f'<rect x="{x0 + len(prompt) * cw + 2}" y="{y - 4 - fs + 3}" width="{cw}" height="{fs}" fill="{GREEN}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/></rect></g>'
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="grimh3xx — Offensive Security &amp; AI">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A0F0D"/><stop offset="1" stop-color="#05080A"/></linearGradient>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{GREEN}" stroke-opacity="0.05"/></pattern>
<radialGradient id="glow" cx="0.85" cy="0.1" r="0.6"><stop offset="0" stop-color="{GREEN}" stop-opacity="0.12"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
{"".join(defs)}
</defs>
<rect width="{w}" height="{h}" rx="14" fill="url(#bg)"/>
<rect width="{w}" height="{h}" rx="14" fill="url(#grid)"/>
<rect width="{w}" height="{h}" rx="14" fill="url(#glow)"/>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{GREEN}" stroke-opacity="0.25"/>
<path d="M0 46H{w}" stroke="{GREEN}" stroke-opacity="0.15"/>
<circle cx="28" cy="23" r="6" fill="#FF5F57"/><circle cx="48" cy="23" r="6" fill="#FEBC2E"/><circle cx="68" cy="23" r="6" fill="#28C840"/>
<text x="{w / 2}" y="28" text-anchor="middle" fill="#6B7A75" font-family="{MONO}" font-size="13">grimh3xx@centraltech: ~</text>
<g font-family="{MONO}" font-size="{fs}">
{"".join(parts)}
</g>
</svg>
'''
    (OUT / "banner.svg").write_text(svg, encoding="utf-8")


def wrap(text, n):
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > n and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


LANG_COLORS = {"C": "#A8B9CC", "C++": "#F34B7D", "Python": "#3572A5", "TypeScript": "#3178C6", "Rust": "#DEA584"}


def card(slug, title, desc, langs, tag):
    w, h = 420, 150
    body = "".join(
        f'<text x="22" y="{74 + i * 20}" fill="#9BA7B4" font-family="{SANS}" font-size="13.5">{escape(l)}</text>'
        for i, l in enumerate(wrap(desc, 54)[:3])
    )
    x, chips = 22, []
    for lang in langs:
        chips.append(
            f'<circle cx="{x + 5}" cy="{h - 22}" r="5" fill="{LANG_COLORS.get(lang, GREEN)}"/>'
            f'<text x="{x + 15}" y="{h - 18}" fill="#C9D1D9" font-family="{SANS}" font-size="12.5">{escape(lang)}</text>'
        )
        x += 30 + len(lang) * 7.5
    tag_w = len(tag) * 7.2 + 18
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="#0B110E" stroke="{GREEN}" stroke-opacity="0.28"/>
<rect x="0.5" y="0.5" width="3" height="{h - 1}" rx="1.5" fill="{GREEN}"/>
<text x="22" y="40" fill="{GREEN}" font-family="{MONO}" font-size="18" font-weight="700">{escape(title)}</text>
<rect x="{w - tag_w - 16}" y="22" width="{tag_w}" height="24" rx="12" fill="none" stroke="{GREEN}" stroke-opacity="0.45"/>
<text x="{w - tag_w / 2 - 16}" y="38.5" text-anchor="middle" fill="{GREEN}" font-family="{MONO}" font-size="11">{escape(tag)}</text>
{body}
{"".join(chips)}
</svg>
'''
    (OUT / f"card-{slug}.svg").write_text(svg, encoding="utf-8")


PROJECTS = [
    ("usbscope", "usbscope", "Interactive USB inspector for the Windows terminal. Reads descriptors straight from the hub driver and flags suspicious device combos.", ["C++"], "PUBLIC"),
    ("samcli", "samcli", "Terminal Steam Achievement Manager written in pure C. One small binary for Windows and Linux.", ["C"], "PUBLIC"),
    ("aircrack", "aircrackwin-x64", "TUI orchestrator for authorized Wi-Fi audits: WPA/WPA2 handshake capture and offline cracking via aircrack-ng & hashcat.", ["Python"], "PUBLIC"),
    ("securearch", "SecureArchSetup", "Automates a hardened Arch Linux setup: pentest tooling, hardened Docker, kernel hardening and SUID auditing.", ["Python"], "PUBLIC"),
    ("exiftracer", "ExifTracer", "Extracts EXIF metadata from images, resolves GPS coordinates to addresses and plots them on interactive maps.", ["Python"], "PUBLIC"),
    ("netsentry", "NetSentry", "Modular reconnaissance and security testing suite with a native desktop UI.", ["Rust", "TypeScript"], "IN DEVELOPMENT"),
    ("aegis", "Aegis", "AI security copilot for Windows and Linux: endpoint agent plus analysis backend.", ["Python"], "IN DEVELOPMENT"),
    ("winforge", "WinForge", "Windows optimization and hardening toolkit built for low-level control.", ["C++"], "IN DEVELOPMENT"),
    ("cts", "CTS Optimizer", "CentralTech's flagship desktop optimizer, with its website and backend.", ["TypeScript"], "IN DEVELOPMENT"),
]

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    banner()
    for p in PROJECTS:
        card(*p)
