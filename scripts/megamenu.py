"""Inventory the click-to-open navigation menu and check what it promotes.

The header menu injects links only after a real click on a nav trigger; hover
alone reveals nothing. Because a stray click can also navigate, each trigger is
tested on a freshly loaded page and the result is discarded if the location
changed. This is the only reliable way to enumerate the menu.

Two questions the static link graph cannot answer:
  1. Does the menu promote trips that cannot be booked?
  2. Does the menu link any of the pages the static crawl called orphaned?
"""
import csv
import os
import sys
import time

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from cdp import Browser  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = lambda *p: os.path.join(ROOT, "evidence", *p)  # noqa: E731

TRIGGER_SEL = ("header button, nav button, header [aria-haspopup], nav [aria-haspopup], "
               "header [aria-expanded], nav [aria-expanded]")

COUNT = """
Array.from(document.querySelectorAll('a[href]'))
  .map(a => a.getAttribute('href'))
  .filter(h => h && h.startsWith('/'))
  .map(h => h.split('#')[0].split('?')[0].replace(/\\/$/, '') || '/')
"""

N_TRIGGERS = f"document.querySelectorAll({TRIGGER_SEL!r}).length"

CLICK_NTH = """
(async (i) => {
  const els = document.querySelectorAll(%s);
  if (!els[i]) return {ok:false};
  const label = (els[i].textContent || '').trim().slice(0, 40);
  els[i].dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true}));
  await new Promise(r => setTimeout(r, 1200));
  return {ok:true, label, path: location.pathname};
})(%d)
""" % (repr(TRIGGER_SEL), 0)


def links_after_click(b, page, idx):
    """Load `page`, click trigger `idx`, return (label, revealed_links) or None."""
    b.goto("https://smilrejser.dk" + page)
    time.sleep(2.2)
    before = set(b.eval(COUNT) or [])
    js = CLICK_NTH.replace("})(0)", "})(%d)" % idx)
    res = b.eval(js) or {}
    if not res.get("ok"):
        return None
    time.sleep(0.8)
    after = set(b.eval(COUNT) or [])
    expected = page.rstrip("/") or "/"
    landed = (res.get("path") or "").rstrip("/") or "/"
    if landed != expected:
        return ("(navigated away)", set())
    return (res.get("label", ""), after - before)


tax = {r["path"]: r for r in csv.DictReader(open(E("page_taxonomy.csv")))}
lg = {r["path"]: r for r in csv.DictReader(open(E("linkgraph.csv")))}

PAGES = ["/", "/italien", "/portugal/nytaarsrejse-til-lissabon"]
per_page = {}

b = Browser()
try:
    for page in PAGES:
        b.goto("https://smilrejser.dk" + page)
        time.sleep(2.2)
        n = b.eval(N_TRIGGERS) or 0
        print(f"\n{page}  —  {n} nav triggers")
        found = set()
        for i in range(int(n)):
            out = links_after_click(b, page, i)
            if not out:
                continue
            label, revealed = out
            if revealed:
                print(f"    trigger {i} {label!r:<34} +{len(revealed)} links")
                found |= revealed
            elif label == "(navigated away)":
                print(f"    trigger {i} navigated away, skipped")
        per_page[page] = found
        print(f"  total revealed on {page}: {len(found)}")
finally:
    b.close()

sets = [v for v in per_page.values() if v]
common = set.intersection(*sets) if sets else set()
union = set.union(*sets) if sets else set()
print(f"\nrevealed on every sampled page : {len(common)}")
print(f"revealed on at least one page  : {len(union)}")
site_wide = bool(sets) and len(common) > 0.9 * len(union)
print("menu is the same site-wide" if site_wide else "menu differs between pages")

menu = sorted(union)
trips = [p for p in menu if tax.get(p, {}).get("kind") == "trip"]
bookable = [p for p in trips if "bookable" in tax[p]["departure_state"]]
empty = [p for p in trips if "empty" in tax[p]["departure_state"]]

all_trips = [p for p, r in tax.items() if r["kind"] == "trip"]
all_book = [p for p in all_trips if "bookable" in tax[p]["departure_state"]]
all_empty = [p for p in all_trips if "empty" in tax[p]["departure_state"]]

print("\n" + "=" * 74)
print("WHAT THE NAVIGATION MENU PROMOTES")
print("=" * 74)
print(f"menu links total                  {len(menu)}")
print(f"  trip pages                      {len(trips)}")
print(f"    bookable                      {len(bookable)}")
print(f"    CANNOT be booked              {len(empty)}")
if trips:
    print(f"\n  {len(empty)}/{len(trips)} = {len(empty) / len(trips):.1%} of trips in the "
          f"navigation menu cannot be booked")
if all_empty:
    print(f"  menu covers {len(empty)}/{len(all_empty)} = {len(empty) / len(all_empty):.0%} "
          f"of all unbookable trips on the site")
if all_book:
    print(f"  menu covers {len(bookable)}/{len(all_book)} = {len(bookable) / len(all_book):.0%} "
          f"of all bookable trips on the site")

orphans = [p for p, r in lg.items() if r["is_orphan"] == "1" and p != "/"]
rescued = sorted(set(orphans) & set(menu))
print(f"\nstatic-crawl orphans the menu does link : {len(rescued)}")
for p in rescued[:10]:
    print(f"    {p}")
print(f"orphans still unlinked anywhere         : {len(orphans) - len(rescued)}")

with open(E("megamenu.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["path", "kind", "departure_state", "static_graph_orphan"])
    for p in menu:
        r = tax.get(p, {})
        w.writerow([p, r.get("kind", ""), r.get("departure_state", ""),
                    lg.get(p, {}).get("is_orphan", "")])
print(f"\nwrote {E('megamenu.csv')} — {len(menu)} menu links")
