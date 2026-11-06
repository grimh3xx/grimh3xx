"""Renders the static profile assets (banner, project cards, certification card) into assets/.

Cards come in a dark and a light variant (`*-light.svg`) so the README can switch with the viewer's theme.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
GREEN = "#2BFF88"
MONO = "'JetBrains Mono','Fira Code',Consolas,Menlo,monospace"
SANS = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"

THEMES = {
    "dark": {"bg": "#0B110E", "border": GREEN, "border_op": 0.28, "accent": GREEN, "title": GREEN,
             "text": "#9BA7B4", "strong": "#E6EDF3", "chip": "#C9D1D9", "suffix": ""},
    "light": {"bg": "#FFFFFF", "border": "#1F883D", "border_op": 0.35, "accent": "#1F883D", "title": "#116329",
              "text": "#57606A", "strong": "#1F2328", "chip": "#24292F", "suffix": "-light"},
}

# 5x7 pixel font for the banner logo
GLYPHS = {
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
}


def pixel_text(text, x0, y0, px):
    rects = []
    for i, ch in enumerate(text):
        for r, row in enumerate(GLYPHS[ch]):
            for c, on in enumerate(row):
                if on == "#":
                    rects.append(f'<rect x="{x0 + (i * 6 + c) * px}" y="{y0 + r * px}" width="{px - 1}" height="{px - 1}"/>')
    return "".join(rects)


def typed(x, y, text, begin, cw, fill, cid, defs, speed=0.065):
    """Text revealed left-to-right like typing; returns (svg, end_time)."""
    dur = max(0.3, len(text) * speed)
    defs.append(
        f'<clipPath id="{cid}"><rect x="{x}" y="{y - 20}" height="28" width="0">'
        f'<animate attributeName="width" from="0" to="{len(text) * cw + 2:.1f}" begin="{begin:.2f}s" dur="{dur:.2f}s" '
        f'calcMode="discrete" values="{";".join(f"{k * cw:.1f}" for k in range(len(text) + 1))}" fill="freeze"/></rect></clipPath>'
    )
    svg = (f'<text x="{x}" y="{y}" fill="{fill}" clip-path="url(#{cid})" textLength="{len(text) * cw:.1f}" '
           f'lengthAdjust="spacingAndGlyphs">{escape(text)}</text>')
    return svg, begin + dur


def appear(svg, at):
    return f'<g opacity="0"><set attributeName="opacity" to="1" begin="{at:.2f}s" fill="freeze"/>{svg}</g>'


def banner():
    w, h, fs = 1000, 400, 16
    cw = fs * 0.6
    defs, parts = [], []

    # logo: GRIMH3XX in a pixel font with an RGB-split glitch
    px = 11
    logo_w = (8 * 6 - 1) * px
    lx, ly = (w - logo_w) / 2, 78
    logo = pixel_text("GRIMH3XX", lx, ly, px)
    defs.append(
        f'<clipPath id="reveal"><rect x="{lx - 10}" y="{ly - 10}" height="{7 * px + 20}" width="0">'
        f'<animate attributeName="width" from="0" to="{logo_w + 20}" begin="0.2s" dur="0.9s" fill="freeze"/></rect></clipPath>'
    )
    parts.append(
        f'<g clip-path="url(#reveal)">'
        f'<g class="gl-a" fill="#FF2BD6" opacity="0">{logo}</g>'
        f'<g class="gl-b" fill="#2BE8FF" opacity="0">{logo}</g>'
        f'<g class="gl-main" fill="{GREEN}" filter="url(#neon)">{logo}</g></g>'
    )
    tag = "OFFENSIVE SECURITY  ·  AI  ·  LOW-LEVEL TOOLING"
    parts.append(appear(
        f'<text x="{w / 2}" y="{ly + 7 * px + 34}" text-anchor="middle" fill="#9BA7B4" font-size="13" letter-spacing="4">{tag}</text>', 1.1))
    sep_y = ly + 7 * px + 54
    parts.append(appear(f'<path d="M40 {sep_y}H{w - 40}" stroke="{GREEN}" stroke-opacity="0.18" stroke-dasharray="2 4"/>', 1.2))

    # boot log
    mods = ["recon & osint", "exploit development", "hardware hacking", "ai security"]
    t, by = 1.4, sep_y + 34
    for i, m in enumerate(mods):
        x = 40 + (i % 2) * 470
        y = by + (i // 2) * 26
        line = (f'<text x="{x}" y="{y}" fill="#6B7A75" xml:space="preserve">[<tspan fill="{GREEN}">  OK  </tspan>]</text>'
                f'<text x="{x + 9 * cw}" y="{y}" fill="#C9D1D9">loaded module <tspan fill="#E6EDF3" font-weight="700">{escape(m)}</tspan></text>')
        parts.append(appear(line, t))
        t += 0.28

    # prompt + whoami
    prompt = "grimh3xx@centraltech:~$ "
    py = by + 2 * 26 + 30
    pw = len(prompt) * cw
    t += 0.4
    parts.append(appear(f'<text x="40" y="{py}" fill="{GREEN}" textLength="{pw:.1f}" lengthAdjust="spacingAndGlyphs">{prompt}</text>', t))
    cmd, t = typed(40 + pw, py, "whoami", t + 0.3, cw, "#E6EDF3", "c0", defs, speed=0.11)
    parts.append(cmd)
    t += 0.35
    parts.append(appear(
        f'<text x="40" y="{py + 26}" fill="#E6EDF3">grimh3xx <tspan fill="#6B7A75">·</tspan> offensive security engineer '
        f'<tspan fill="#6B7A75">·</tspan> founder of <tspan fill="{GREEN}">CentralTech</tspan></text>', t))
    t += 0.5
    parts.append(appear(
        f'<text x="40" y="{py + 52}" fill="{GREEN}" textLength="{pw:.1f}" lengthAdjust="spacingAndGlyphs">{prompt}</text>'
        f'<rect class="cursor" x="{40 + pw + 2:.1f}" y="{py + 52 - fs + 2}" width="{cw:.1f}" height="{fs + 1}" fill="{GREEN}"/>', t))

    css = (
        ".gl-a{animation:ga 7s infinite steps(1,end) 2s}.gl-b{animation:gb 7s infinite steps(1,end) 2s}"
        ".gl-main{animation:gm 7s infinite steps(1,end) 2s}"
        "@keyframes ga{0%,90%,100%{opacity:0;transform:none}91%{opacity:.85;transform:translate(-5px,1px)}"
        "92%{opacity:.85;transform:translate(4px,-2px)}93%{opacity:0}96%{opacity:.7;transform:translate(-3px,0)}97%{opacity:0}}"
        "@keyframes gb{0%,90%,100%{opacity:0;transform:none}91%{opacity:.85;transform:translate(5px,-1px)}"
        "92%{opacity:.85;transform:translate(-4px,2px)}93%{opacity:0}96%{opacity:.7;transform:translate(3px,0)}97%{opacity:0}}"
        "@keyframes gm{0%,90%,100%{transform:none}91%{transform:translate(2px,0) skewX(-6deg)}92%{transform:translate(-2px,0)}"
        "93%{transform:none}96%{transform:translate(1px,0) skewX(4deg)}97%{transform:none}}"
        ".cursor{animation:blink 1s steps(1,end) infinite}@keyframes blink{50%{opacity:0}}"
        ".scan{animation:scan 6s linear infinite}@keyframes scan{0%{transform:translateY(-80px)}100%{transform:translateY(" + str(h + 80) + "px)}}"
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="grimh3xx — Offensive Security &amp; AI">
<style>{css}</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A0F0D"/><stop offset="1" stop-color="#05080A"/></linearGradient>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{GREEN}" stroke-opacity="0.045"/></pattern>
<pattern id="lines" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" fill-opacity="0.22"/></pattern>
<radialGradient id="glow" cx="0.5" cy="0.25" r="0.55"><stop offset="0" stop-color="{GREEN}" stop-opacity="0.13"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset="0.5" stop-color="{GREEN}" stop-opacity="0.07"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>
<filter id="neon" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="win"><rect width="{w}" height="{h}" rx="14"/></clipPath>
{"".join(defs)}
</defs>
<g clip-path="url(#win)">
<rect width="{w}" height="{h}" fill="url(#bg)"/>
<rect width="{w}" height="{h}" fill="url(#grid)"/>
<rect width="{w}" height="{h}" fill="url(#glow)"/>
<path d="M0 46H{w}" stroke="{GREEN}" stroke-opacity="0.15"/>
<circle cx="28" cy="23" r="6" fill="#FF5F57"/><circle cx="48" cy="23" r="6" fill="#FEBC2E"/><circle cx="68" cy="23" r="6" fill="#28C840"/>
<text x="{w / 2}" y="28" text-anchor="middle" fill="#6B7A75" font-family="{MONO}" font-size="13">grimh3xx@centraltech: ~</text>
<g font-family="{MONO}" font-size="{fs}">
{"".join(parts)}
</g>
<rect class="scan" y="0" width="{w}" height="80" fill="url(#beam)"/>
<rect width="{w}" height="{h}" fill="url(#lines)"/>
</g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{GREEN}" stroke-opacity="0.25"/>
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


def frame(w, h, th, body, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="10" fill="{th["bg"]}" stroke="{th["border"]}" stroke-opacity="{th["border_op"]}"/>
<rect x="0.5" y="0.5" width="3" height="{h - 1}" rx="1.5" fill="{th["accent"]}"/>
{body}
</svg>
'''


def tag_pill(w, text, th):
    tw = len(text) * 7.2 + 18
    return (f'<rect x="{w - tw - 16}" y="22" width="{tw}" height="24" rx="12" fill="none" stroke="{th["accent"]}" stroke-opacity="0.5"/>'
            f'<text x="{w - tw / 2 - 16}" y="38.5" text-anchor="middle" fill="{th["title"]}" font-family="{MONO}" font-size="11">{escape(text)}</text>')


def card(slug, title, desc, langs, tag, th):
    w, h = 420, 150
    body = [f'<text x="22" y="40" fill="{th["title"]}" font-family="{MONO}" font-size="18" font-weight="700">{escape(title)}</text>',
            tag_pill(w, tag, th)]
    body += [f'<text x="22" y="{74 + i * 20}" fill="{th["text"]}" font-family="{SANS}" font-size="13.5">{escape(l)}</text>'
             for i, l in enumerate(wrap(desc, 54)[:3])]
    x = 22
    for lang in langs:
        body.append(f'<circle cx="{x + 5}" cy="{h - 22}" r="5" fill="{LANG_COLORS.get(lang, GREEN)}"/>'
                    f'<text x="{x + 15}" y="{h - 18}" fill="{th["chip"]}" font-family="{SANS}" font-size="12.5">{escape(lang)}</text>')
        x += 30 + len(lang) * 7.5
    (OUT / f"card-{slug}{th['suffix']}.svg").write_text(frame(w, h, th, "".join(body), title), encoding="utf-8")


CERT = {
    "title": "Certificate IV in Cyber Security",
    "code": "22603VIC",
    "issuer": "Australian Pacific College  ·  Nationally Recognised Training (AQF)  ·  2026",
    "units": [
        "Expose website security vulnerabilities",
        "Evaluate & test incident response plans",
        "Implement network security infrastructure",
        "Investigate Windows security features",
        "Configure & secure networked endpoints",
        "Perform cyber security data analysis",
    ],
}


def cert_card(th):
    w, h = 860, 200
    body = [
        f'<text x="24" y="40" fill="{th["title"]}" font-family="{MONO}" font-size="19" font-weight="700">{escape(CERT["title"])}</text>',
        tag_pill(w, CERT["code"], th),
        f'<text x="24" y="66" fill="{th["text"]}" font-family="{SANS}" font-size="13.5">{escape(CERT["issuer"])}</text>',
        f'<path d="M24 84H{w - 24}" stroke="{th["accent"]}" stroke-opacity="0.18"/>',
    ]
    for i, u in enumerate(CERT["units"]):
        x = 24 + (i % 2) * 410
        y = 114 + (i // 2) * 28
        body.append(f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="14"><tspan fill="{th["accent"]}" font-weight="700">✓</tspan>'
                    f'<tspan fill="{th["strong"]}" dx="8">{escape(u)}</tspan></text>')
    (OUT / f"cert{th['suffix']}.svg").write_text(frame(w, h, th, "".join(body), CERT["title"]), encoding="utf-8")


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
    for th in THEMES.values():
        for p in PROJECTS:
            card(*p, th)
        cert_card(th)
