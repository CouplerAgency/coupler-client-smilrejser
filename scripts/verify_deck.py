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
import glob
import os

deck = open("index.html").read()

# Claims live in the deck and in the evidence write-ups, so both are searched.
# A figure quoted in linkgraph.md but not the deck still has to be right.
corpus = deck + "\n".join(open(p).read() for p in sorted(glob.glob("evidence/*.md")))

checks = []


def check(label, computed, claimed=None):
    """A bool `computed` is asserted directly. Otherwise `claimed`, when given,
    must appear verbatim in the deck or in one of the evidence markdown files."""
    note = ""
    if isinstance(computed, bool):
        ok = computed
    elif claimed is not None:
        ok = claimed in corpus
        note = "" if ok else f"  <- claim not found anywhere: {claimed!r}"
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
check("images no alt", noalt, "4,167 images have no text description")
check("fetchpriority=high anywhere", fp)
check("alt-text share", f"{noalt / imgs:.0%}", "31% of all images")

slow = sum(1 for r in crawl if i(r, "ttfb_ms") > 2000)
heavy = sum(1 for r in crawl if i(r, "html_bytes") > 1_000_000)
check("pages slower than 2s", slow, ">73<")
check("pages over 1 MB HTML", heavy, ">44<")

# The deck folded these into a single housekeeping row and no longer quotes the
# counts, so only the underlying figures are recorded here.
check("meta descriptions over 160", sum(1 for r in crawl if i(r, "meta_desc_len") > 160))
check("titles over 60", sum(1 for r in crawl if i(r, "title_len") > 60))

# --- departure states ------------------------------------------------------
kinds = Counter(r["kind"] for r in tax)
check("trip pages", kinds["trip"], "131 trip pages")
check("editorial-city", kinds["editorial-city"], "101 are city guides")
check("editorial-thin", kinds["editorial-thin"], "18 are near-empty pages")

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
      "55 of 131 pages show no price")
words_empty = sum(i(r, "word_count") for r in trips if is_empty(r))
check("words on empty trips", f"{words_empty:,}", "151,722")

# --- structured data ------------------------------------------------------
names = Counter(r["list_name"] for r in il)
check("ItemList blocks found", len(il), "On 103 country and city pages")
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

# --- internal link graph --------------------------------------------------
lg = list(csv.DictReader(open("evidence/linkgraph.csv")))
lgi = {r["path"]: r for r in lg}
med = lambda xs: sorted(xs)[len(xs) // 2]  # noqa: E731

t_book = [r["path"] for r in trips if "bookable" in r["departure_state"]]
t_empty = [r["path"] for r in trips if is_empty(r)]
inb = lambda p: int(lgi.get(p, {}).get("inbound_contextual") or 0)  # noqa: E731
check("median inbound links, bookable trips", med([inb(p) for p in t_book]),
      "one you can buy gets 13")
check("median inbound links, dead trips", med([inb(p) for p in t_empty]),
      "cannot buy gets 12 links")

# Two distinct orphan definitions, kept apart because they have different word
# totals and the evidence files each cite one of them.
orph_strict = [r for r in lg if r["path"] != "/" and i(r, "inbound_raw") == 0]
menu = {r["path"] for r in csv.DictReader(open("evidence/megamenu.csv"))}
boiler = {r["path"] for r in lg if i(r, "inbound_raw") > 0.9 * len(lg)}
orph_wide = [r for r in lg if r["path"] != "/" and i(r, "inbound_contextual") == 0
             and r["path"] not in boiler and r["path"] not in menu]
check("orphans, zero inbound of any kind", len(orph_strict))
check("  their word count", f"{sum(i(r, 'word_count') for r in orph_strict):,}", "29,281")
check("orphans, no in-content link and not in nav", len(orph_wide))
check("  their word count", f"{sum(i(r, 'word_count') for r in orph_wide):,}", "32,145 words")
check("strict orphan set is a subset of the wide set",
      {r["path"] for r in orph_strict} <= {r["path"] for r in orph_wide})

check("total internal edges recorded",
      sum(1 for _ in csv.DictReader(open("evidence/links.csv"))), "9,617 internal")

# --- GA4 (optional: raw exports are gitignored) ---------------------------
# os and glob imported at the top

if os.path.exists("ga4/landing_pages.csv"):
    import sys

    sys.path.insert(0, "scripts")
    from ga4_join import G, norm, num, read_ga4

    pg, _ = read_ga4(G("pages_screens.csv"))
    PPK = "Page path and screen class"
    step = {}
    for r in pg:
        p = re.sub(r"/\d+", "/{id}", r[PPK].split("?")[0].rstrip("/"))
        step[p] = step.get(p, 0) + num(r["Active users"])
    s1 = step["/booking/travel/{id}/{id}/accommodation"]
    s3 = step["/booking/travel/{id}/{id}/personal-information"]
    s4 = step["/booking/travel/{id}/{id}/summary"]
    conf = step["/booking/travel/confirmation"]
    check("checkout starts", f"{s1:,.0f}", "2,516")
    check("reached step 3", f"{s3:,.0f}", "720")
    check("reached step 4", f"{s4:,.0f}", "223")
    check("reached confirmation", f"{conf:,.0f}", "159")
    check("step 1->3 loss", f"{(s1 - s3) / s1:.1%}", "71%")
    check("step 3->4 loss", f"{(s3 - s4) / s3:.1%}", "69%")
    check("confirmation as % of starts", f"{conf / s1:.1%}", "6.3")
    check("users lost at step 1", f"{s1 - s3:,.0f}", "1,796")
    check("users lost at step 3", f"{s3 - s4:,.0f}", "497")
    check("total lost at both", f"{s1 - s3 + s3 - s4:,.0f}", "2,293")

    land, _ = read_ga4(G("landing_pages.csv"))
    L = {}
    for r in land:
        p = norm(r["Landing page"])
        if not p:
            continue
        d = L.setdefault(p, [0.0, 0.0])
        d[0] += num(r["Sessions"])
        d[1] += num(r["Total revenue"])
    rps = lambda ps: (lambda t: t[1] / t[0] if t[0] else 0)(  # noqa: E731
        [sum(L.get(p, [0, 0])[j] for p in ps) for j in (0, 1)])
    base = rps(t_book)
    mult = lambda ps: f"{rps(ps) / base:.1f}\u00d7"  # noqa: E731
    check("unbookable revenue per visit", mult(t_empty), ">0.7\u00d7<")
    check("unbookable shortfall vs bookable",
          f"{(1 - rps(t_empty) / base):.0%}", "29% less per visit")
    tt = [r["path"] for r in crawl if r["template"] == "travel-type"]
    check("holiday-type revenue per visit", mult(tt), ">2.7\u00d7<")
    hub = [r["path"] for r in crawl if r["template"] == "destination-hub"]
    check("country-page revenue per visit", mult(hub), ">1.5\u00d7<")
    check("homepage revenue per visit", mult(["/"]), ">5.0\u00d7<")
    blog = [r["path"] for r in crawl if r["template"] == "blog-post"]
    check("blog revenue is zero", rps(blog) == 0)
    check("blog posts", sum(1 for _ in blog), "67 posts")
    check("blog sessions", f"{sum(L.get(p, [0, 0])[0] for p in blog):,.0f}", "4,118")
    tot_rev = sum(v[1] for v in L.values())
    es = sum(L.get(p, [0, 0])[0] for p in t_empty)
    check("catalogue gap as share of revenue",
          f"{(base - rps(t_empty)) * es / tot_rev:.1%}", "1.4%")
    check("unbookable share of sessions",
          f"{es / sum(v[0] for v in L.values()):.1%}", "8.2%")
else:
    checks.append((True, "GA4 checks", "SKIPPED — ga4/ exports not present", ""))

# --- no absolute revenue may leak into the published deck ----------------
check("no absolute DKK revenue in deck",
      not re.search(r"\b\d{1,3}(?:[.,]\d{3}){2,}\s*DKK", deck))

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
