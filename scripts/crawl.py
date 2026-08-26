#!/usr/bin/env python3
"""
CRO crawler for smilrejser.dk.

Reads raw/sitemap.xml, fetches every URL and writes evidence/crawl.csv.

The site is Next.js App Router, so every page inlines a large RSC payload inside
<script> tags. That payload repeats page copy, CTA labels and prices, so all text
analysis happens AFTER scripts and styles are stripped. Counting on the raw HTML
inflates every figure by roughly 3x.
"""

import csv
import gzip
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = os.path.join(ROOT, "raw", "sitemap.xml")
OUT = os.path.join(ROOT, "evidence", "crawl.csv")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0 Safari/537.36")

WORKERS = 4
CTX = ssl.create_default_context()

# Top-level path segments that are destinations rather than site furniture.
NON_DESTINATION = {
    "blog", "om-os", "rejsetyper", "rejsemal", "rejsekalender", "rejseforsikring",
    "rejsebetingelser", "rejseforedrag", "privatlivspolitik", "cookie-politik",
    "nyhedsbrev", "katalog", "gavekort", "faq", "inspiration", "tryghed",
    "transformation", "samvirke", "saeson", "flyrejser", "laeserrejser",
}
TRAVEL_TYPES = {
    "naturrejser", "musik-og-underholdning", "vinrejser", "madrejser", "vinterrejser",
    "vandreferier", "togrejser", "storbyferier", "sommerrejser", "seniorrejser",
    "safarirejser", "rundrejser", "paaskerejser", "langtidsferier", "kulturrejser",
    "historiske-rejser", "foraarsrejser", "flere-generationer", "efteraarsrejser",
    "jul-og-nytaar", "flodkrydstogter",
}


def fetch(url):
    """Return (status, ttfb_ms, body_bytes, html_text)."""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Encoding": "gzip",
        "Accept-Language": "da-DK,da;q=0.9",
    })
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
            status = r.status
            raw = r.read()
            ttfb = int((time.time() - start) * 1000)
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return status, ttfb, len(raw), raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, int((time.time() - start) * 1000), 0, ""
    except Exception as e:
        sys.stderr.write("ERR %s %s\n" % (url, e))
        return 0, int((time.time() - start) * 1000), 0, ""


SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.S | re.I)
STYLE_RE = re.compile(r"<style\b[^>]*>.*?</style>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def visible_text(html):
    """Page copy a human can read: scripts and styles removed, tags stripped."""
    h = SCRIPT_RE.sub(" ", html)
    h = STYLE_RE.sub(" ", h)
    h = TAG_RE.sub(" ", h)
    h = (h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#x27;", "'")
          .replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">"))
    return WS_RE.sub(" ", h).strip()


def first(pattern, html, group=1, flags=re.S | re.I):
    m = re.search(pattern, html, flags)
    return (m.group(group) or "").strip() if m else ""


def classify(path):
    segs = [s for s in path.split("/") if s]
    if not segs:
        return "homepage"
    top = segs[0]
    if top == "blog":
        return "blog-index" if len(segs) == 1 else "blog-post"
    if top in TRAVEL_TYPES:
        return "travel-type" if len(segs) == 1 else "trip"
    if top in NON_DESTINATION:
        return "info"
    if len(segs) == 1:
        return "destination-hub"
    return "trip"


def analyse(url, status, ttfb, nbytes, html):
    path = re.sub(r"^https?://[^/]+", "", url) or "/"
    row = {
        "url": url,
        "path": path,
        "top_segment": (path.strip("/").split("/") or [""])[0],
        "template": classify(path),
        "status": status,
        "ttfb_ms": ttfb,
        "html_bytes": nbytes,
    }
    if not html:
        return row

    body = SCRIPT_RE.sub(" ", STYLE_RE.sub(" ", html))
    text = visible_text(html)

    title = first(r"<title[^>]*>(.*?)</title>", html)
    desc = first(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    h1 = first(r"<h1[^>]*>(.*?)</h1>", html)
    h1 = TAG_RE.sub("", h1).strip()

    row["title"] = title
    row["title_len"] = len(title)
    row["meta_desc"] = desc
    row["meta_desc_len"] = len(desc)
    row["h1"] = h1
    row["h1_count"] = len(re.findall(r"<h1\b", body, re.I))
    row["h2_count"] = len(re.findall(r"<h2\b", body, re.I))
    row["h3_count"] = len(re.findall(r"<h3\b", body, re.I))
    row["word_count"] = len(text.split())

    # Images and loading priority.
    imgs = re.findall(r"<img\b[^>]*>", body, re.I)
    row["img_count"] = len(imgs)
    row["img_lazy"] = sum(1 for t in imgs if 'loading="lazy"' in t.lower())
    row["img_eager"] = sum(1 for t in imgs if 'loading="eager"' in t.lower())
    row["fetchpriority_high"] = len(re.findall(r'fetchpriority\s*=\s*"high"', html, re.I))
    row["img_missing_alt"] = sum(
        1 for t in imgs if not re.search(r'\balt\s*=\s*"[^"]+"', t, re.I))

    # Structured data.
    types = sorted(set(re.findall(r'"@type"\s*:\s*"([^"]+)"', html)))
    row["schema_types"] = "|".join(types)
    row["has_product_schema"] = int("Product" in types)
    row["ldjson_blocks"] = len(re.findall(r'application/ld\+json', html, re.I))

    # Conversion elements. Booking links are the only true purchase path, and each
    # bookable departure renders its own /booking/travel/{id}/{dep}/... href, so the
    # count of unique hrefs is the count of departures a visitor can actually buy.
    booking_hrefs = set(re.findall(r'href="(/booking/[^"]+)"', body))
    row["booking_links"] = len(booking_hrefs)
    row["cta_bestil"] = len(re.findall(r">\s*Bestil\s*<", body, re.I))
    row["cta_se_rejsen"] = len(re.findall(r">\s*Se rejsen\s*<", body, re.I))
    row["cta_laes_mere"] = len(re.findall(r">\s*L(?:æ|ae)s mere\s*<", body, re.I))
    row["tel_links"] = len(re.findall(r'href="tel:', body, re.I))
    row["mailto_links"] = len(re.findall(r'href="mailto:', body, re.I))
    row["form_count"] = len(re.findall(r"<form\b", body, re.I))

    # Price. Danish thousands separator is a dot: "Fra 11.495 DKK".
    prices = [int(p.replace(".", "")) for p in
              re.findall(r"([\d]{1,3}(?:\.[\d]{3})+)\s*DKK", text)]
    row["has_price"] = int(bool(prices))
    row["price_min"] = min(prices) if prices else ""
    row["price_count"] = len(prices)
    row["has_fra_price"] = int(bool(re.search(r"Fra\s+[\d.]+\s*DKK", text)))

    # Trust and social proof.
    row["trustpilot"] = int("trustpilot" in html.lower())
    row["rejsegarantifonden"] = int("rejsegarantifond" in html.lower())
    row["travelife"] = int("travelife" in html.lower())
    row["has_faq_schema"] = int("FAQPage" in types)
    row["duration_days"] = first(r"(\d+)\s*dage", text)

    # Directives.
    row["canonical"] = first(r'<link\s+rel="canonical"\s+href="([^"]*)"', html)
    row["robots_meta"] = first(r'<meta\s+name="robots"\s+content="([^"]*)"', html)
    row["og_image"] = int(bool(re.search(r'property="og:image"', html, re.I)))
    row["h1_matches_title"] = int(bool(h1) and h1.lower() in title.lower())
    return row


FIELDS = [
    "url", "path", "top_segment", "template", "status", "ttfb_ms", "html_bytes",
    "title", "title_len", "meta_desc", "meta_desc_len", "h1", "h1_count",
    "h2_count", "h3_count", "word_count", "img_count", "img_lazy", "img_eager",
    "fetchpriority_high", "img_missing_alt", "schema_types", "has_product_schema",
    "ldjson_blocks", "booking_links", "cta_bestil", "cta_se_rejsen",
    "cta_laes_mere", "tel_links", "mailto_links", "form_count", "has_price",
    "price_min", "price_count", "has_fra_price", "trustpilot",
    "rejsegarantifonden", "travelife", "has_faq_schema", "duration_days",
    "canonical", "robots_meta", "og_image", "h1_matches_title",
]


def main():
    with open(SITEMAP, encoding="utf-8") as f:
        urls = re.findall(r"<loc>([^<]+)</loc>", f.read())
    # Homepage is not in the sitemap but is the most important page on the site.
    urls = ["https://smilrejser.dk/"] + [u for u in urls if u.rstrip("/") !=
                                         "https://smilrejser.dk"]
    print("crawling %d urls with %d workers" % (len(urls), WORKERS))

    done = [0]

    def work(u):
        status, ttfb, nbytes, html = fetch(u)
        time.sleep(0.35)  # keep well under ~2 req/s per worker
        done[0] += 1
        if done[0] % 25 == 0:
            print("  %d/%d" % (done[0], len(urls)), flush=True)
        return analyse(u, status, ttfb, nbytes, html)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        rows = list(ex.map(work, urls))

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)

    ok = sum(1 for r in rows if r.get("status") == 200)
    print("wrote %s — %d rows, %d x 200, %d non-200"
          % (OUT, len(rows), ok, len(rows) - ok))


if __name__ == "__main__":
    main()
