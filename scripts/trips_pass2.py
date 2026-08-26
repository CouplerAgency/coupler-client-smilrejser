#!/usr/bin/env python3
"""
Second pass over trip pages only, to settle the departures question definitively.

The phrase "Afgange ikke tilgængelige" appears in the i18n label dictionary of
EVERY page, bookable or not, so a naive substring search proves nothing. The
reliable signal is the *rendered* element:

    <div class="...text-center">Afgange ikke tilgængelige</div>

This pass records that rendered state alongside the count of unique /booking/
hrefs, so the two measures cross-validate each other. It also checks whether the
"Forespørg" (enquire) and "Venteliste" (waitlist) button states — which exist in
the design system's label dictionary — are ever actually rendered.
"""

import csv
import gzip
import os
import re
import ssl
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = os.path.join(ROOT, "evidence", "crawl.csv")
OUT = os.path.join(ROOT, "evidence", "trips_departures.csv")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/127.0 Safari/537.36")
CTX = ssl.create_default_context()

# Rendered DOM, not the label dictionary.
EMPTY_RENDERED = re.compile(r'text-center">Afgange ikke tilg[^<]*</div>')
# Label-dictionary occurrence, used only to prove the naive search is unreliable.
EMPTY_LABEL = re.compile(r'DEPARTURE_NO_DEPARTURES')
BTN_INQUIRY = re.compile(r'>\s*Forespørg\s*<')
BTN_WAITLIST = re.compile(r'>\s*Venteliste\s*<')
SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.S | re.I)


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
    trips = [r for r in csv.DictReader(open(IN, encoding="utf-8"))
             if r["template"] == "trip"]
    print("second pass over %d trip pages" % len(trips))
    done = [0]

    def work(r):
        html = fetch(r["url"])
        time.sleep(0.3)
        done[0] += 1
        if done[0] % 25 == 0:
            print("  %d/%d" % (done[0], len(trips)), flush=True)
        body = SCRIPT_RE.sub(" ", html)
        booking = len(set(re.findall(r'href="(/booking/[^"]+)"', body)))
        return {
            "url": r["url"],
            "path": r["path"],
            "country": r["top_segment"],
            "booking_links": booking,
            "empty_departures_rendered": int(bool(EMPTY_RENDERED.search(html))),
            "empty_label_present": int(bool(EMPTY_LABEL.search(html))),
            "btn_inquiry_rendered": int(bool(BTN_INQUIRY.search(body))),
            "btn_waitlist_rendered": int(bool(BTN_WAITLIST.search(body))),
            "has_price": r["has_price"],
            "price_min": r["price_min"],
            "word_count": r["word_count"],
            "has_product_schema": r["has_product_schema"],
        }

    with ThreadPoolExecutor(max_workers=4) as ex:
        rows = list(ex.map(work, trips))

    fields = list(rows[0].keys())
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    empty = sum(r["empty_departures_rendered"] for r in rows)
    nobook = sum(1 for r in rows if r["booking_links"] == 0)
    label = sum(r["empty_label_present"] for r in rows)
    agree = sum(1 for r in rows
                if r["empty_departures_rendered"] == (r["booking_links"] == 0))
    print()
    print("trip pages                                  : %d" % len(rows))
    print("empty departures table RENDERED             : %d" % empty)
    print("zero /booking/ hrefs                        : %d" % nobook)
    print("the two measures agree on                   : %d of %d" % (agree, len(rows)))
    print("label string present (unreliable detector)  : %d" % label)
    print("pages rendering 'Forespørg' button          : %d"
          % sum(r["btn_inquiry_rendered"] for r in rows))
    print("pages rendering 'Venteliste' button         : %d"
          % sum(r["btn_waitlist_rendered"] for r in rows))
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
