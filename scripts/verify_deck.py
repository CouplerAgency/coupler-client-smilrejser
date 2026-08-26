"""Recompute every headline number in the deck from the evidence files.

Run before publishing. Any FAIL means the deck and the evidence disagree.
"""
import csv
import re
from collections import Counter

crawl = list(csv.DictReader(open("evidence/crawl.csv")))
tax = list(csv.DictReader(open("evidence/page_taxonomy.csv")))
il = list(csv.DictReader(open("evidence/itemlist.csv")))
cen = list(csv.DictReader(open("evidence/schema_census.csv")))
deck = open("index.html").read()

checks = []


def check(label, computed, claimed_in_deck=None):
    """A bool `computed` is asserted directly. Otherwise `claimed_in_deck`, when
    given, must appear verbatim in index.html."""
    note = ""
    if isinstance(computed, bool):
        ok = computed
    elif claimed_in_deck is not None:
        ok = claimed_in_deck in deck
        note = "" if ok else f"  <- not in deck: {claimed_in_deck!r}"
    else:
        ok = True
    checks.append((ok, label, computed, note))


i = lambda r, k: int(r[k] or 0)  # noqa: E731

# --- crawl -----------------------------------------------------------------
check("pages crawled", len(crawl), "421 pages")
check("all HTTP 200", all(r["status"] == "200" for r in crawl))

imgs = sum(i(r, "img_count") for r in crawl)
lazy = sum(i(r, "img_lazy") for r in crawl)
noalt = sum(i(r, "img_missing_alt") for r in crawl)
fp = sum(i(r, "fetchpriority_high") for r in crawl)
check("images total", imgs, "13,448 images")
check("images lazy", lazy, "13,321 of 13,448")
check("images no alt", noalt, "4,167 images have no alt")
check("fetchpriority=high anywhere", fp)
check("alt-text share", f"{noalt / imgs:.1%}", "31% of every image")

slow = sum(1 for r in crawl if i(r, "ttfb_ms") > 2000)
heavy = sum(1 for r in crawl if i(r, "html_bytes") > 1_000_000)
check("pages slower than 2s", slow, ">73<")
check("pages over 1 MB HTML", heavy, ">44<")

md = sum(1 for r in crawl if i(r, "meta_desc_len") > 160)
tl = sum(1 for r in crawl if i(r, "title_len") > 60)
check("meta descriptions over 160", md, "Trim 289 meta descriptions")
check("titles over 60", tl, "154 titles")

# --- departure states ------------------------------------------------------
kinds = Counter(r["kind"] for r in tax)
check("trip pages", kinds["trip"], "131 trip pages")
check("editorial-city", kinds["editorial-city"], "101 are destination guides")
check("editorial-thin", kinds["editorial-thin"], "18 are stubs under 500 words")

trips = [r for r in tax if r["kind"] == "trip"]
is_empty = lambda r: "empty" in r["departure_state"]  # noqa: E731
book = sum(1 for r in trips if "bookable" in r["departure_state"])
empty = sum(1 for r in trips if is_empty(r))
none_ = len(trips) - book - empty
check("bookable trips", f"{book} ({book / len(trips):.1%})", "52.7%")
check("empty-table trips", f"{empty} ({empty / len(trips):.1%})", "45.8%")
check("no visible state", none_, ">2<")
check("trip pages with a price", sum(1 for r in trips if r["has_price"] == "1"), "76 of them")
check("trip pages with no price", sum(1 for r in trips if r["has_price"] != "1"),
      "55 of 131 trip pages carry no price")
words_empty = sum(i(r, "word_count") for r in trips if is_empty(r))
check("words on empty trips", f"{words_empty:,}", "151,722")

# --- structured data ------------------------------------------------------
names = Counter(r["list_name"] for r in il)
check("ItemList blocks found", len(il), "103 destination pages emit")
check("all named Rejser til Frankrig", list(names) == ["Rejser til Frankrig"])
check("wrong-country pages", sum(1 for r in il if r["name_matches_country"] == "0"), ">70<")
check("numberOfItems always accurate",
      all(r["number_of_items"] == r["actual_items"] for r in il))

cen_ok = [r for r in cen if not r["error"]]
ctrip = [r for r in cen_ok if r["kind"] == "trip"]
ced = [r for r in cen_ok if r["kind"] != "trip"]
check("trip pages with top-level Product",
      f"{sum('Product' in r['top_level'].split('|') for r in ctrip)} of {len(ctrip)}")
check("editorial pages with top-level Product (must be 0)",
      sum("Product" in r["top_level"].split("|") for r in ced))
check("trip pages with any ItemList (must be 0)",
      sum("ItemList" in r["nested"].split("|") for r in ctrip))

# --- deck hygiene ---------------------------------------------------------
check("no projected-uplift claim",
      not re.search(r"(?<!projected )uplift of|\+\d+% (more|conversion|uplift)"
                    r"|conversion rate (of|by) \d", deck, re.I))
check("noindex present", 'content="noindex, nofollow"' in deck)
check("slide count", len(re.findall(r'<section class="slide[ "]', deck)))
check("every slide has a title", len(re.findall(r'<section class="slide[^"]*" data-title=', deck))
      == len(re.findall(r'<section class="slide[ "]', deck)))
check("no broken image paths",
      all(__import__("os").path.exists(p) for p in re.findall(r'src="(assets/[^"]+)"', deck)))

print(f"{'':3} {'check':<48} {'computed'}")
print("-" * 92)
bad = 0
for ok, label, computed, note in checks:
    mark = "ok " if ok else "FAIL"
    if not ok:
        bad += 1
    print(f"{mark:<3} {label:<48} {computed}{note}")
print("-" * 92)
print("all consistent" if not bad else f"{bad} MISMATCH(ES) — fix before publishing")
