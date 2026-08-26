"""Schema census over every trip-shaped URL, using ld+json blocks only.

Replaces the first-pass crawler's `has_product_schema`, which regex-matched
`"@type":"Product"` anywhere in the response and therefore also matched the
Next.js RSC payload. Only genuine <script type="application/ld+json"> blocks
count here, and nesting is walked so list items are seen.
"""
import csv
import json
import re
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

LD = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I
)
INTEREST = ["Product", "Offer", "AggregateOffer", "FAQPage", "BreadcrumbList",
            "ItemList", "TouristDestination", "Collection", "Article"]


def walk_types(node, out):
    if isinstance(node, dict):
        t = node.get("@type")
        if isinstance(t, str):
            out.add(t)
        elif isinstance(t, list):
            out.update(x for x in t if isinstance(x, str))
        for v in node.values():
            walk_types(v, out)
    elif isinstance(node, list):
        for v in node:
            walk_types(v, out)


def top_level_types(node, out):
    """@type of entities that are the subject of the page, not list members."""
    for n in (node if isinstance(node, list) else [node]):
        if isinstance(n, dict):
            t = n.get("@type")
            if isinstance(t, str):
                out.add(t)
            elif isinstance(t, list):
                out.update(x for x in t if isinstance(x, str))


def fetch(row):
    path = row["path"]
    req = urllib.request.Request(
        "https://smilrejser.dk" + path,
        headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "da-DK"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception as e:
        return {"path": path, "kind": row["kind"], "error": str(e)}

    nested, top = set(), set()
    blocks = 0
    for block in LD.findall(html):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        blocks += 1
        walk_types(data, nested)
        top_level_types(data, top)

    return {
        "path": path,
        "kind": row["kind"],
        "ldjson_blocks": blocks,
        "top_level": "|".join(sorted(top)),
        "nested": "|".join(sorted(nested)),
        "error": "",
    }


rows = list(csv.DictReader(open("evidence/page_taxonomy.csv")))
print(f"fetching {len(rows)} trip-shaped URLs\n")
with ThreadPoolExecutor(max_workers=6) as ex:
    results = list(ex.map(fetch, rows))

fields = ["path", "kind", "ldjson_blocks", "top_level", "nested", "error"]
with open("evidence/schema_census.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in results:
        w.writerow({k: r.get(k, "") for k in fields})

errs = [r for r in results if r.get("error")]
ok = [r for r in results if not r.get("error")]
print(f"ok {len(ok)}, errors {len(errs)}\n")

for kind in ("trip", "editorial-city", "editorial-thin"):
    grp = [r for r in ok if r["kind"] == kind]
    if not grp:
        continue
    print(f"{kind}  ({len(grp)} pages)")
    print("   as a top-level entity (the page's own subject):")
    c = Counter()
    for r in grp:
        c.update(r["top_level"].split("|") if r["top_level"] else ["(none)"])
    for t in INTEREST:
        if c.get(t):
            print(f"     {t:<20} {c[t]:>4} / {len(grp)}")
    print("   anywhere, including nested list items:")
    c2 = Counter()
    for r in grp:
        c2.update(r["nested"].split("|") if r["nested"] else ["(none)"])
    for t in INTEREST:
        if c2.get(t):
            print(f"     {t:<20} {c2[t]:>4} / {len(grp)}")
    print()

print("wrote evidence/schema_census.csv")
