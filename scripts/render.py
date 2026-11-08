"""Renders the static profile artwork into assets/: banner, project cards, certification,
skills grid and avatar. Cards come in dark and light (`*-light.svg`) variants.
"""
import json
from pathlib import Path

from brand import DARK, LANG_COLORS, MONO, SANS, THEMES, escape, finish

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
ICONS = json.loads((Path(__file__).parent / "icons.json").read_text())


def write(name, svg, faces):
    (OUT / name).write_text(finish(svg, faces), encoding="utf-8")


def wrap(text, n):
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > n and cur:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


def appear(svg, at):
    return f'<g opacity="0"><set attributeName="opacity" to="1" begin="{at:.2f}s" fill="freeze"/>{svg}</g>'


def shared_defs(th, w, h):
    return (
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{th["bg"]}"/><stop offset="1" stop-color="{th["bg2"]}"/></linearGradient>'
        f'<linearGradient id="brand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{th["accent"]}"/><stop offset="1" stop-color="{th["accent2"]}"/></linearGradient>'
        f'<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{th["grid"]}" fill-opacity="0.16"/></pattern>'
        f'<radialGradient id="fade" cx="0.5" cy="0.3" r="0.75"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
        f'<mask id="dotmask"><rect width="{w}" height="{h}" fill="url(#fade)"/></mask>'
        f'<radialGradient id="glow" cx="0.5" cy="0.0" r="0.65"><stop offset="0" stop-color="{th["accent"]}" stop-opacity="0.22"/><stop offset="1" stop-color="{th["accent"]}" stop-opacity="0"/></radialGradient>'
    )


# ------------------------------------------------------------------ banner
def banner():
    th = DARK
    w, h = 1000, 400
    parts, defs = [], [shared_defs(th, w, h)]
    cx = w / 2

    parts.append(appear(
        f'<text x="{cx}" y="96" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="3.5" fill="{th["muted"]}">'
        f'<tspan fill="{th["accent2"]}">●</tspan>  CENTRALTECH  ·  OFFENSIVE SECURITY</text>', 0.1))

    word = "grimh3xx"
    fs = 92
    mark = f'<text x="{cx}" y="190" text-anchor="middle" font-family="{MONO}" font-size="{fs}" font-weight="800" letter-spacing="-2">{word}</text>'
    defs.append(
        f'<clipPath id="reveal"><rect x="0" y="100" height="110" width="0">'
        f'<animate attributeName="width" from="0" to="{w}" begin="0.25s" dur="0.9s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></rect></clipPath>'
        f'<filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="14"/></filter>'
    )
    parts.append(
        f'<g clip-path="url(#reveal)">'
        f'<g fill="{th["accent"]}" opacity="0.35" filter="url(#soft)">{mark}</g>'
        f'<g class="ga" fill="{th["accent2"]}" opacity="0">{mark}</g>'
        f'<g class="gb" fill="#F472B6" opacity="0">{mark}</g>'
        f'<g class="gm" fill="url(#brand)">{mark}</g></g>'
    )
    parts.append(appear(
        f'<text x="{cx}" y="232" text-anchor="middle" font-family="{SANS}" font-size="17" fill="{th["text"]}">'
        f'Pentesting <tspan fill="{th["dim"]}">·</tspan> Automation <tspan fill="{th["dim"]}">·</tspan> '
        f'Low-level tooling <tspan fill="{th["dim"]}">·</tspan> AI security</text>', 1.0))

    # boot log + prompt in a terminal strip
    y0 = 270
    parts.append(appear(f'<rect x="60" y="{y0}" width="{w - 120}" height="102" rx="10" fill="{th["panel"]}" fill-opacity="0.75" stroke="{th["border"]}"/>', 1.15))
    mods = ["recon & osint", "exploit development", "hardware hacking", "ai security"]
    t = 1.35
    widths = [(len(m) + 7) * 13 * 0.6 for m in mods]
    gap = (w - 168 - sum(widths)) / (len(mods) - 1)
    x = 84
    for i, m in enumerate(mods):
        parts.append(appear(
            f'<text x="{x}" y="{y0 + 32}" font-family="{MONO}" font-size="13" fill="{th["dim"]}" xml:space="preserve">'
            f'[<tspan fill="{th["ok"]}" font-weight="700"> OK </tspan>] <tspan fill="{th["text"]}">{escape(m)}</tspan></text>', t))
        x += widths[i] + gap
        t += 0.22
    prompt_x, py = 84, y0 + 72
    prompt = "grimh3xx@centraltech:~$"
    cw = 15 * 0.6
    t += 0.3
    parts.append(appear(
        f'<text x="{prompt_x}" y="{py}" font-family="{MONO}" font-size="15" fill="{th["accent2"]}">{prompt}</text>', t))
    cmd = "whoami"
    cmd_x = prompt_x + (len(prompt) + 1) * cw
    vals = ";".join(f"{k * cw:.1f}" for k in range(len(cmd) + 1))
    defs.append(f'<clipPath id="type"><rect x="{cmd_x}" y="{py - 16}" height="22" width="0">'
                f'<animate attributeName="width" values="{vals}" calcMode="discrete" begin="{t + 0.3:.2f}s" dur="0.7s" fill="freeze"/></rect></clipPath>')
    parts.append(f'<text x="{cmd_x}" y="{py}" font-family="{MONO}" font-size="15" fill="{th["title"]}" clip-path="url(#type)">{cmd}</text>')
    t += 1.2
    out_x = cmd_x + (len(cmd) + 2) * cw
    parts.append(appear(
        f'<text x="{out_x}" y="{py}" font-family="{MONO}" font-size="15" fill="{th["muted"]}" xml:space="preserve">→ '
        f'<tspan fill="{th["text"]}">offensive security engineer, founder of </tspan><tspan fill="{th["accent2"]}" font-weight="700">CentralTech</tspan></text>'
        f'<rect class="cur" x="{out_x + (len("→ offensive security engineer, founder of CentralTech") + 1) * cw:.1f}" y="{py - 13}" width="{cw:.1f}" height="17" fill="{th["accent2"]}"/>', t))

    css = (
        ".ga{animation:ga 11s steps(1,end) infinite 3s}.gb{animation:gb 11s steps(1,end) infinite 3s}.gm{animation:gm 11s steps(1,end) infinite 3s}"
        "@keyframes ga{0%,95%,100%{opacity:0;transform:none}95.4%{opacity:.55;transform:translate(-3px,0)}96.2%{opacity:0}}"
        "@keyframes gb{0%,95%,100%{opacity:0;transform:none}95.4%{opacity:.45;transform:translate(3px,0)}96.2%{opacity:0}}"
        "@keyframes gm{0%,95%,100%{transform:none}95.4%{transform:translate(1px,0)}96.2%{transform:none}}"
        ".cur{animation:blink 1.1s steps(1,end) infinite}@keyframes blink{50%{opacity:0}}"
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="grimh3xx: offensive security engineer, founder of CentralTech">
<style>{css}</style>
<defs>{"".join(defs)}<clipPath id="win"><rect width="{w}" height="{h}" rx="16"/></clipPath></defs>
<g clip-path="url(#win)">
<rect width="{w}" height="{h}" fill="url(#bg)"/>
<rect width="{w}" height="{h}" fill="url(#dots)" mask="url(#dotmask)"/>
<rect width="{w}" height="{h}" fill="url(#glow)"/>
<circle cx="28" cy="26" r="5.5" fill="#FF5F57" fill-opacity="0.85"/><circle cx="46" cy="26" r="5.5" fill="#FEBC2E" fill-opacity="0.85"/><circle cx="64" cy="26" r="5.5" fill="#28C840" fill-opacity="0.85"/>
{"".join(parts)}
</g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="{th["border"]}"/>
</svg>
'''
    write("banner.svg", svg, {("JBM", 400), ("JBM", 700), ("JBM", 800), ("INT", 400)})


# ------------------------------------------------------------------ cards
def card_frame(w, h, th, body, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">
<defs><linearGradient id="brand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{th["accent"]}"/><stop offset="1" stop-color="{th["accent2"]}"/></linearGradient>
<clipPath id="c"><rect width="{w}" height="{h}" rx="12"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{th["panel"]}"/><rect width="{w}" height="2" fill="url(#brand)"/></g>
<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{th["border"]}"/>
{body}
</svg>
'''


def pill(x_right, y, text, th, color):
    tw = len(text) * 6.6 + 26
    x = x_right - tw
    return (f'<rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="22" rx="11" fill="{color}" fill-opacity="0.1" stroke="{color}" stroke-opacity="0.35"/>'
            f'<circle cx="{x + 11:.1f}" cy="{y + 11}" r="3" fill="{color}"/>'
            f'<text x="{x + 19:.1f}" y="{y + 15}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="{color}">{escape(text)}</text>')


def card(slug, title, desc, langs, status, th):
    w, h = 420, 144
    color = th["ok"] if status == "PUBLIC" else th["warn"]
    body = [f'<text x="22" y="40" font-family="{MONO}" font-size="17" font-weight="700" fill="{th["title"]}">{escape(title)}</text>',
            pill(w - 18, 23, status, th, color)]
    body += [f'<text x="22" y="{70 + i * 20}" font-family="{SANS}" font-size="13.5" fill="{th["text"]}">{escape(l)}</text>'
             for i, l in enumerate(wrap(desc, 56)[:2])]
    x = 22
    for lang in langs:
        body.append(f'<circle cx="{x + 5}" cy="{h - 24}" r="4.5" fill="{LANG_COLORS.get(lang, th["accent"])}"/>'
                    f'<text x="{x + 15}" y="{h - 20}" font-family="{SANS}" font-size="12.5" fill="{th["muted"]}">{escape(lang)}</text>')
        x += 32 + len(lang) * 7.2
    write(f"card-{slug}{th['suffix']}.svg", card_frame(w, h, th, "".join(body), title), {("JBM", 700), ("INT", 400)})


CERT = {
    "title": "Certificate IV in Cyber Security",
    "code": "22603VIC",
    "issuer": "Australian Pacific College  ·  Nationally Recognised Training (AQF)  ·  2026",
    "units": [
        "Expose website security vulnerabilities", "Evaluate & test incident response plans",
        "Implement network security infrastructure", "Investigate Windows security features",
        "Configure & secure networked endpoints", "Perform cyber security data analysis",
    ],
}
SHIELD = "M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5l-8-3z"


def cert_card(th):
    w, h = 900, 196
    body = [
        f'<rect x="22" y="22" width="44" height="44" rx="10" fill="{th["accent"]}" fill-opacity="0.12" stroke="{th["accent"]}" stroke-opacity="0.35"/>'
        f'<g transform="translate(32 32) scale(1)"><path d="{SHIELD}" fill="none" stroke="url(#brand)" stroke-width="1.8" stroke-linejoin="round"/>'
        f'<path d="m8.5 12 2.4 2.4 4.6-4.8" fill="none" stroke="{th["accent2"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></g>',
        f'<text x="82" y="42" font-family="{MONO}" font-size="18" font-weight="700" fill="{th["title"]}">{escape(CERT["title"])}</text>',
        f'<text x="82" y="62" font-family="{SANS}" font-size="13" fill="{th["muted"]}">{escape(CERT["issuer"])}</text>',
        pill(w - 20, 24, CERT["code"], th, th["accent2"]),
        f'<path d="M22 84H{w - 22}" stroke="{th["border"]}"/>',
    ]
    for i, u in enumerate(CERT["units"]):
        x = 26 + (i % 2) * 440
        y = 114 + (i // 2) * 26
        body.append(f'<path d="m{x} {y - 5} 3.2 3.2 6-6.4" fill="none" stroke="{th["ok"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
                    f'<text x="{x + 20}" y="{y}" font-family="{SANS}" font-size="13.5" fill="{th["text"]}">{escape(u)}</text>')
    write(f"cert{th['suffix']}.svg", card_frame(w, h, th, "".join(body), CERT["title"]), {("JBM", 700), ("INT", 400)})


# ------------------------------------------------------------------ skills
GLYPHS = {  # generic stroke icons (24x24) for things without a brand mark
    "nmap": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4.5"/><path d="M12 12 18.5 5.5"/>',
    "shodan": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3.2 3.6 3.2 14.4 0 18M12 3c-3.2 3.6-3.2 14.4 0 18"/>',
    "osint": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.4 15.4 5.1 5.1"/>',
    "asm": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9.5 2.5v3.5M14.5 2.5v3.5M9.5 18v3.5M14.5 18v3.5M2.5 9.5H6M2.5 14.5H6M18 9.5h3.5M18 14.5h3.5"/>',
    "windows": '<path d="M3.5 5.6 10.5 4.6v6.9h-7zM12 4.4l8.5-1.2v8.3H12zM3.5 13h7v6.9l-7-1zM12 13h8.5v8.3L12 20.1z"/>',
    "hwhack": '<rect x="4" y="4" width="16" height="16" rx="3"/><path d="m12.8 7.5-3 5h4.4l-3 4"/>',
}
SKILLS = [
    ("Offensive", [("Burp Suite", "burpsuite"), ("Metasploit", "metasploit"), ("Wireshark", "wireshark"), ("Nmap", "nmap"),
                   ("Shodan", "shodan"), ("OSINT", "osint"), ("Kali", "kalilinux"), ("Parrot OS", "parrotsecurity")]),
    ("Languages", [("C", "c"), ("C++", "cplusplus"), ("Rust", "rust"), ("Python", "python"), ("Bash", "gnubash"),
                   ("x86-64 ASM", "asm"), ("TypeScript", "typescript"), ("JavaScript", "javascript")]),
    ("Systems", [("Linux", "linux"), ("Arch Linux", "archlinux"), ("Debian", "debian"), ("Ubuntu", "ubuntu"),
                 ("Windows", "windows"), ("Arduino UNO", "arduino")]),
    ("Tooling", [("Git", "git"), ("Docker", "docker"), ("Tauri", "tauri"), ("React", "react"), ("Node.js", "nodedotjs"), ("VSCodium", "vscodium")]),
    ("Learning", [("HW Hacking", "hwhack")]),
]


def icon(key, x, y, size, color):
    s = size / 24
    if key in GLYPHS:
        return (f'<g transform="translate({x} {y}) scale({s:.3f})" fill="none" stroke="{color}" stroke-width="1.7" '
                f'stroke-linecap="round" stroke-linejoin="round">{GLYPHS[key]}</g>')
    return f'<path transform="translate({x} {y}) scale({s:.3f})" d="{ICONS[key]["path"]}" fill="{color}"/>'


def skills(th):
    tile, gap, label_w = 88, 8, 112
    rows = len(SKILLS)
    w = label_w + 8 * tile + 7 * gap + 40
    h = 24 + rows * (tile - 8) + (rows - 1) * 12 + 24
    body, y = [], 24
    for cat, items in SKILLS:
        body.append(f'<text x="22" y="{y + 44}" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1.5" fill="{th["muted"]}">{cat.upper()}</text>')
        for i, (name, key) in enumerate(items):
            x = label_w + i * (tile + gap)
            hl = key in ("hwhack",)
            body.append(f'<rect x="{x}" y="{y}" width="{tile}" height="{tile - 8}" rx="10" fill="{th["bg2"] if th is not DARK else th["bg"]}" '
                        f'stroke="{th["accent"] if hl else th["border"]}" stroke-opacity="{0.6 if hl else 1}"/>')
            body.append(icon(key, x + tile / 2 - 12, y + 14, 24, th["title"]))
            body.append(f'<text x="{x + tile / 2}" y="{y + 61}" text-anchor="middle" font-family="{SANS}" font-size="11.5" fill="{th["text"]}">{escape(name)}</text>')
        y += tile - 8 + 12
    write(f"skills{th['suffix']}.svg", card_frame(w, h, th, "".join(body), "Skills"), {("JBM", 700), ("INT", 400)})


# ------------------------------------------------------------------ avatar
def avatar():
    th = DARK
    s = 512
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}">
<defs>{shared_defs(th, s, s)}</defs>
<rect width="{s}" height="{s}" fill="url(#bg)"/>
<rect width="{s}" height="{s}" fill="url(#dots)" mask="url(#dotmask)"/>
<rect width="{s}" height="{s}" fill="url(#glow)"/>
<circle cx="256" cy="256" r="196" fill="none" stroke="url(#brand)" stroke-width="3" stroke-opacity="0.55"/>
<circle cx="256" cy="256" r="214" fill="none" stroke="{th["border"]}" stroke-width="1.5" stroke-dasharray="3 9"/>
<text x="256" y="300" text-anchor="middle" font-family="{MONO}" font-size="150" font-weight="800" letter-spacing="-8" fill="url(#brand)">g3<tspan fill="{th["accent2"]}">_</tspan></text>
</svg>
'''
    write("avatar.svg", svg, {("JBM", 800)})


PROJECTS = [
    ("dllh3x", "DLLH3x", "Read-only DLL hijacking auditor for Windows PE, finding deep transitive chains with ATT&CK mapping.", ["Rust"], "PUBLIC"),
    ("credreap", "credreap", "Lockout-aware credential spraying & hashcat orchestration for authorized engagements.", ["Rust"], "PUBLIC"),
    ("faultline", "faultline", "Exploit-dev toolkit: ROP gadgets, cyclic patterns, checksec and a crash fuzzer.", ["Rust"], "PUBLIC"),
    ("daclseek", "daclseek", "Read-only Windows privesc enumerator: real AccessCheck over DACLs, services, tokens, autoruns and credential surfaces.", ["Rust"], "PUBLIC"),
    ("arpspoofer", "arp-spoofer", "LAN MITM toolkit for authorised assessments: ARP spoof, host discovery, MAC spoof, LLMNR/NBT-NS/mDNS poisoning.", ["Rust"], "PUBLIC"),
    ("samcli", "samcli", "Terminal Steam Achievement Manager written in pure C. One small binary for Windows and Linux.", ["C"], "PUBLIC"),
    ("aircrack", "aircrackwin-x64", "TUI orchestrator for authorized Wi-Fi audits: handshake capture and offline cracking via aircrack-ng & hashcat.", ["Python"], "PUBLIC"),
    ("securearch", "SecureArchSetup", "Arch Linux hardening & pentest setup in Bash: dry run, backups with restore, nftables, audit score.", ["Shell"], "PUBLIC"),
    ("exiftracer", "ExifTracer", "Finds what images give away (GPS, device serials, owner, time), maps it and strips it.", ["Python"], "PUBLIC"),
    ("nyxnet", "NyxNet", "Tor identity rotator with a live circuit dashboard. Verified exits, full circuit view. Linux and Windows.", ["Python"], "PUBLIC"),
    ("pebinaries", "pe-binaries", "EDR-evasion detector for PE files: imphash & IOCs, import/API analysis, RWX checks, risk score.", ["C++"], "PUBLIC"),
    ("netreap", "netreap", "Lean SMB+LDAP enum & post-ex in Python/Impacket: lockout-aware spraying, PtH, secretsdump, kerberoast.", ["Python"], "PUBLIC"),
    ("bypass403", "403-bypass", "403/401 bypass toolkit in C: verb tampering, IP headers, path mutations, batch mode, JSON/CSV output.", ["C"], "PUBLIC"),
]

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    banner()
    avatar()
    for th in THEMES:
        for p in PROJECTS:
            card(*p, th)
        cert_card(th)
        skills(th)
