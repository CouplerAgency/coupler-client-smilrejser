"""Check the ItemList name on every editorial page that emits one.

Found by hand on two unrelated pages (Porto in Portugal, a garden tour in England)
that both named their trip list "Rejser til Frankrig" — trips to France. This
counts how many pages carry a list name that does not match their own country.
"""
import csv
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor

LD = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I
)

# Danish country names as they appear in the URL's top segment.
COUNTRY_DA = {
    "italien": "Italien", "portugal": "Portugal", "spanien": "Spanien",
    "england": "England", "frankrig": "Frankrig", "graekenland": "Grækenland",
    "schweiz": "Schweiz", "kroatien": "Kroatien", "malta": "Malta",
    "irland": "Irland", "skotland": "Skotland", "tyskland": "Tyskland",
    "oestrig": "Østrig", "marokko": "Marokko", "cypern": "Cypern",
}


def itemlists(html):
    out = []
    for block in LD.findall(html):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        for node in (data if isinstance(data, list) else [data]):
            if isinstance(node, dict) and node.get("@type") == "ItemList":
                items = node.get("itemListElement") or []
                out.append((node.get("name"), node.get("numberOfItems"), len(items)))
    return out


def check(path):
    url = "https://smilrejser.dk" + path
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "da-DK"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception as e:
        return path, None, str(e)
    return path, itemlists(html), None


rows = list(csv.DictReader(open("evidence/page_taxonomy.csv")))
targets = [r for r in rows if r["kind"] != "trip" and r["has_product_schema"] == "1"]
print(f"checking {len(targets)} editorial pages that emit Product\n")

results = []
with ThreadPoolExecutor(max_workers=6) as ex:
    for path, lists, err in ex.map(lambda r: check(r["path"]), targets):
        results.append((path, lists, err))

names = {}
mismatched = []
for path, lists, err in results:
    if err or not lists:
        continue
    for name, declared, actual in lists:
        names[name] = names.get(name, 0) + 1
        seg = path.strip("/").split("/")[0]
        expected = COUNTRY_DA.get(seg)
        if expected and name and expected not in name:
            mismatched.append((path, name, declared, actual))

print("ItemList name -> how many pages use it")
for name, n in sorted(names.items(), key=lambda kv: -kv[1]):
    print(f"  {n:>4}  {name!r}")

print(f"\npages whose list name names the wrong country: {len(mismatched)}")
for path, name, declared, actual in mismatched[:10]:
    print(f"  {path:<50} {name!r}  declared={declared} actual={actual}")

drift = [r for r in results if r[1] for name, d, a in r[1] if d != a]
print(f"\npages where numberOfItems != actual item count: {len(drift)}")

with open("evidence/itemlist.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["path", "list_name", "number_of_items", "actual_items", "name_matches_country"])
    for path, lists, err in results:
        for name, declared, actual in (lists or []):
            seg = path.strip("/").split("/")[0]
            expected = COUNTRY_DA.get(seg)
            ok = "" if not expected else int(bool(name and expected in name))
            w.writerow([path, name, declared, actual, ok])
print("\nwrote evidence/itemlist.csv")
