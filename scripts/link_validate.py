"""Validate how internal links must be extracted on this site.

Corrections 1 and 2 both came from matching raw HTML on a Next.js App Router
site, where the response body also carries the RSC payload. Before crawling 421
pages for a link graph, confirm which extraction method agrees with the rendered
DOM: naive `href=` anywhere, `<a href>` after stripping scripts, or real Chrome.
"""
import re
import sys
import time
import urllib.request

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from cdp import Browser  # noqa: E402

SCRIPT_STYLE = re.compile(r"<(script|style|noscript)\b[^>]*>.*?</\1>", re.S | re.I)
ANCHOR = re.compile(r"<a\b[^>]*?\bhref=[\"']([^\"']+)", re.I)
ANY_HREF = re.compile(r"href=[\"']([^\"']+)", re.I)

SAMPLE = [
    ("homepage", "/"),
    ("bookable trip", "/portugal/nytaarsrejse-til-lissabon"),
    ("empty trip", "/italien/madlavningskursus-paa-amalfikysten"),
    ("destination guide", "/portugal/porto"),
]


def internal(hrefs):
    """Site-internal document paths only, normalised, no assets or params."""
    out = set()
    for h in hrefs:
        h = h.strip()
        if h.startswith("https://smilrejser.dk"):
            h = h[len("https://smilrejser.dk"):]
        if not h.startswith("/") or h.startswith("//"):
            continue
        # Fragments and query strings must be stripped on both sides of the
        # comparison, or /a and /a#SECTION count as two different pages.
        h = h.split("#")[0].split("?")[0].rstrip("/") or "/"
        if not h.startswith("/"):
            continue
        if re.search(r"\.(png|jpe?g|svg|webp|ico|css|js|xml|pdf|txt|avif|woff2?)$", h, re.I):
            continue
        out.add(h)
    return out


def fetch(path):
    req = urllib.request.Request(
        "https://smilrejser.dk" + path,
        headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "da-DK"},
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


b = Browser()
try:
    print(f"{'page':<20} {'naive href=':>12} {'<a> no-script':>14} {'rendered DOM':>13}   verdict")
    print("-" * 92)
    for label, path in SAMPLE:
        html = fetch(path)
        naive = internal(ANY_HREF.findall(html))
        careful = internal(ANCHOR.findall(SCRIPT_STYLE.sub(" ", html)))

        b.goto("https://smilrejser.dk" + path)
        time.sleep(2.5)
        dom_hrefs = b.eval(
            "Array.from(document.querySelectorAll('a[href]'))"
            ".map(a=>a.getAttribute('href'))"
        ) or []
        rendered = internal(dom_hrefs)

        missing = rendered - careful
        extra = careful - rendered
        verdict = "static matches rendered"
        if missing or extra:
            verdict = f"-{len(missing)} missed, +{len(extra)} phantom"
        print(f"{label:<20} {len(naive):>12} {len(careful):>14} {len(rendered):>13}   {verdict}")
        if missing:
            print(f"{'':<20} missed by static : {sorted(missing)[:4]}")
        if extra:
            print(f"{'':<20} static-only      : {sorted(extra)[:4]}")
        inflation = len(naive) - len(rendered)
        print(f"{'':<20} naive over-counts rendered by {inflation} paths "
              f"({'RSC payload leaking' if inflation > 5 else 'acceptable'})")
finally:
    b.close()
