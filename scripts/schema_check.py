"""Re-verify Product schema detection.

The first-pass crawler matched `"@type":"Product"` anywhere in the response body,
which also matches the Next.js RSC payload — component props, not emitted markup.
This script only reads real <script type="application/ld+json"> blocks, and
separately checks the rendered DOM in case the block is injected client-side.
"""
import json
import re
import sys
import time
import urllib.request

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from cdp import Browser  # noqa: E402

LD = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I
)


def types_from_html(html):
    """@type values that appear inside genuine ld+json blocks only."""
    found = []
    for block in LD.findall(html):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                t = node.get("@type")
                if isinstance(t, str):
                    found.append(t)
                elif isinstance(t, list):
                    found.extend(x for x in t if isinstance(x, str))
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
    return sorted(set(found))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "da-DK"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


PAGES = [
    ("trip", "/portugal/nytaarsrejse-til-lissabon"),
    ("trip", "/italien/madlavningskursus-paa-amalfikysten"),
    ("editorial-city", "/portugal/porto"),
    ("editorial-city", "/italien/milano"),
    ("editorial-city", "/portugal/madeira"),
    ("editorial-city", "/europa/kulturrejser"),
    ("editorial-thin", "/england/haverejser-england"),
    ("editorial-thin", "/jul-og-nytaar/julerejser"),
    ("editorial-thin", "/schweiz/schweiz-togrejser"),
]

b = Browser()
try:
    print(f"{'kind':<15} {'path':<48} {'raw ld+json':<26} {'rendered ld+json'}")
    print("-" * 118)
    for kind, path in PAGES:
        url = "https://smilrejser.dk" + path
        raw = types_from_html(fetch(url))
        b.goto(url)
        time.sleep(2.5)
        dom = b.eval("document.documentElement.outerHTML")
        rendered = types_from_html(dom)
        mark = lambda ts: ("Product" if "Product" in ts else "-")  # noqa: E731
        print(f"{kind:<15} {path:<48} {mark(raw):<26} {mark(rendered)}")
        print(f"{'':<15} {'':<48} {','.join(raw)[:24]:<26} {','.join(rendered)[:60]}")
finally:
    b.close()
