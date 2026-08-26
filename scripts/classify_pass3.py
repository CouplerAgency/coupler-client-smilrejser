#!/usr/bin/env python3
"""
Third pass: classify the 250 URL-guessed "trip" pages by STRUCTURE, not by URL shape.

Pass 2 revealed that a URL of the form /{country}/{slug} is not necessarily a trip.
/italien/milano and /england/london are city inspiration pages, and
/jul-og-nytaar/julerejser is a 177-word category stub — none of them have a
departures table, yet several carry Product schema.

The structural signal is the departures section itself:
    data-id-section="TRAVEL_DEPARTURES"
A page with that section is a sellable trip. A page without it is editorial,
regardless of what its URL looks like or what schema it emits.
"""

import csv
import gzip
import os
import re
import ssl
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = os.path.join(ROOT, "evidence", "crawl.csv")
DEP = os.path.join(ROOT, "evidence", "trips_departures.csv")
OUT = os.path.join(ROOT, "evidence", "page_taxonomy.csv")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0 Safari/537.36")
CTX = ssl.create_default_context()

HAS_DEPARTURES = re.compile(r'data-id-section="TRAVEL_DEPARTURES"')
HAS_WAITLIST = re.compile(r'data-id-section="TRAVEL_WAITLIST"')
BOOK_CTA_ANCHOR = re.compile(r'href="#TRAVEL_DEPARTURES"')


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Encoding": "gzip", "Accept-Language": "da-DK"})
    try:
        with urllib.request.urlopen(req, timeout=45, context=CTX) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return raw.decode("utf-8", "replace")
    except Exception:
        return ""


def main():
    base = {r["path"]: r for r in csv.DictReader(open(IN, encoding="utf-8"))}
    dep = {r["path"]: r for r in csv.DictReader(open(DEP, encoding="utf-8"))}
    paths = list(dep.keys())
    print("structural pass over %d pages" % len(paths))
    done = [0]

    def work(p):
        r = base[p]
        html = fetch(r["url"])
        time.sleep(0.3)
        done[0] += 1
        if done[0] % 25 == 0:
            print("  %d/%d" % (done[0], len(paths)), flush=True)
        d = dep[p]
        has_dep = bool(HAS_DEPARTURES.search(html))
        if not has_dep:
            kind = "editorial-thin" if int(r["word_count"]) < 500 else "editorial-city"
            state = "n/a — no departures section"
        else:
            kind = "trip"
            if int(d["booking_links"]) > 0:
                state = "A bookable online"
            elif d["btn_inquiry_rendered"] == "1":
                state = "B on request (Forespørg)"
            elif d["btn_waitlist_rendered"] == "1":
                state = "C waitlist (Venteliste)"
            elif d["empty_departures_rendered"] == "1":
                state = "D empty (Afgange ikke tilgængelige)"
            else:
                state = "E departures section, no visible state"
        return {
            "path": p,
            "country": r["top_segment"],
            "kind": kind,
            "departure_state": state,
            "has_departures_section": int(has_dep),
            "has_waitlist_section": int(bool(HAS_WAITLIST.search(html))),
            "book_cta_is_anchor": int(bool(BOOK_CTA_ANCHOR.search(html))),
            "booking_links": d["booking_links"],
            "has_price": r["has_price"],
            "price_min": r["price_min"],
            "word_count": r["word_count"],
            "has_product_schema": r["has_product_schema"],
            "title_len": r["title_len"],
            "meta_desc_len": r["meta_desc_len"],
        }

    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(work, paths))

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    print()
    print("KIND:")
    for k, v in Counter(r["kind"] for r in rows).most_common():
        print("  %-18s %3d" % (k, v))
    print()
    print("DEPARTURE STATE (trips only):")
    trips = [r for r in rows if r["kind"] == "trip"]
    for k, v in sorted(Counter(r["departure_state"] for r in trips).items()):
        print("  %-40s %3d  (%.1f%% of %d trips)" % (k, v, 100 * v / len(trips), len(trips)))
    print()
    print("Product schema on editorial pages: %d of %d"
          % (sum(1 for r in rows if r["kind"].startswith("editorial")
                 and r["has_product_schema"] == "1"),
             sum(1 for r in rows if r["kind"].startswith("editorial"))))
    print("'Bestil rejse' CTA is an in-page anchor on: %d pages"
          % sum(r["book_cta_is_anchor"] for r in rows))
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
