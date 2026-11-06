"""Shared palette, fonts and helpers for every generated SVG.

Fonts are subset to the glyphs each SVG actually uses and embedded as base64 WOFF2,
so the artwork renders identically regardless of what the viewer has installed.
"""
import base64
import io
import re
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape  # noqa: F401  (re-exported for the renderers)

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

MONO = "'JBM','JetBrains Mono',ui-monospace,Consolas,Menlo,monospace"
SANS = "'INT','Inter',system-ui,'Segoe UI',Arial,sans-serif"

# Palette A: CentralTech midnight blue. Green is reserved for status/success.
DARK = {
    "name": "dark", "suffix": "",
    "bg": "#0B0F17", "bg2": "#0E1420", "panel": "#111826",
    "border": "#1E2A3D", "grid": "#3B82F6",
    "accent": "#3B82F6", "accent2": "#22D3EE",
    "title": "#F1F5FB", "text": "#C5CFDD", "muted": "#8B98AD", "dim": "#5B6678",
    "ok": "#34D399", "warn": "#FBBF24",
}
LIGHT = {
    "name": "light", "suffix": "-light",
    "bg": "#FFFFFF", "bg2": "#F6F8FB", "panel": "#F6F8FB",
    "border": "#D8DEE8", "grid": "#2563EB",
    "accent": "#2563EB", "accent2": "#0891B2",
    "title": "#0F172A", "text": "#334155", "muted": "#5B6678", "dim": "#94A3B8",
    "ok": "#059669", "warn": "#B45309",
}
THEMES = [DARK, LIGHT]

LANG_COLORS = {"C": "#A8B9CC", "C++": "#F34B7D", "Python": "#3572A5", "TypeScript": "#3178C6",
               "Rust": "#DEA584", "Shell": "#89E051", "JavaScript": "#F1E05A"}

_FACES = {  # css family -> {weight: file}
    "JBM": {400: "JetBrainsMono-Regular.ttf", 700: "JetBrainsMono-Bold.ttf", 800: "JetBrainsMono-ExtraBold.ttf"},
    "INT": {400: "Inter-Regular.ttf", 600: "Inter-SemiBold.ttf"},
}


@lru_cache(maxsize=None)
def _subset(file, chars):
    from fontTools import subset
    from fontTools.ttLib import TTFont

    font = TTFont(FONTS / file)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt"]
    opts.name_IDs = []
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(text=chars)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def _texts(svg):
    """Visible text of the SVG (entities decoded) — what the fonts must cover."""
    body = re.sub(r"<style>.*?</style>", "", svg, flags=re.S)
    text = "".join(re.findall(r">([^<]+)<", body))
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'")):
        text = text.replace(a, b)
    return text


def font_css(svg, faces=None):
    """@font-face rules for the faces/weights the SVG references, subset to its text."""
    chars = "".join(sorted(set(_texts(svg)) | set(" 0123456789")))
    css = []
    for fam, weights in _FACES.items():
        if f"'{fam}'" not in svg:
            continue
        for wt, file in weights.items():
            if faces and (fam, wt) not in faces:
                continue
            css.append(f"@font-face{{font-family:'{fam}';font-weight:{wt};"
                       f"src:url(data:font/woff2;base64,{_subset(file, chars)}) format('woff2')}}")
    return "".join(css)


def finish(svg, faces=None):
    """Inject embedded fonts into the first <style> (or a new one) of the SVG."""
    css = font_css(svg, faces)
    if "<style>" in svg:
        return svg.replace("<style>", "<style>" + css, 1)
    return re.sub(r"(<svg[^>]*>)", r"\1<style>" + css.replace("\\", r"\\") + "</style>", svg, count=1)
