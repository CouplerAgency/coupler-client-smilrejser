#!/usr/bin/env python3
"""
Capture the audit screenshot set at desktop and mobile, Danish locale, consent
suppressed.

Each entry is (slug, url, anchor_or_None). When an anchor is given the page is
scrolled to that element before the shot, which is how the departures-table
evidence is captured — the section sits well below the fold on a 2,500-word page.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Browser  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "shots")

BASE = "https://smilrejser.dk"

PAGES = [
    # slug, path, scroll-to selector (or None for top of page)
    ("home",            "/",                                              None),
    ("hub-italien",     "/italien",                                       None),
    ("trip-bookable",   "/portugal/nytaarsrejse-til-lissabon",            None),
    ("trip-bookable-dep", "/portugal/nytaarsrejse-til-lissabon",          "#TRAVEL_DEPARTURES"),
    ("trip-empty",      "/italien/madlavningskursus-paa-amalfikysten",    None),
    ("trip-empty-dep",  "/italien/madlavningskursus-paa-amalfikysten",    "#TRAVEL_DEPARTURES"),
    ("trip-empty-wait", "/italien/madlavningskursus-paa-amalfikysten",    "#TRAVEL_WAITLIST"),
    ("traveltype-vandre", "/vandreferier",                                None),
    ("editorial-milano",  "/italien/milano",                              None),
    ("rejsekalender",   "/rejsekalender",                                 None),
    ("faq",             "/faq",                                           None),
]

SCROLL_JS = """
(function(){
  var el = document.querySelector(%r);
  if(!el) return 'NOTFOUND';
  var y = el.getBoundingClientRect().top + window.pageYOffset - 90;
  window.scrollTo(0, y);
  return 'ok';
})();
"""


def run(label, width, height, mobile, port):
    b = Browser(width=width, height=height, mobile=mobile, port=port)
    results = []
    try:
        for slug, path, anchor in PAGES:
            name = "%s-%s.png" % (slug, label)
            dest = os.path.join(OUT, name)
            b.goto(BASE + path, settle=3.5)
            note = ""
            if anchor:
                r = b.eval(SCROLL_JS % anchor)
                if r == "NOTFOUND":
                    note = " [ANCHOR NOT FOUND: %s]" % anchor
                time.sleep(1.5)
            size = b.shot(dest)
            results.append((name, size, note))
            print("  %-34s %7d bytes%s" % (name, size, note), flush=True)
    finally:
        b.close()
    return results


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("desktop", "both"):
        print("=== DESKTOP 1440x1400 ===")
        run("desktop", 1440, 1400, False, 9341)
    if which in ("mobile", "both"):
        print("=== MOBILE 390x1500 ===")
        run("mobile", 390, 1500, True, 9342)


if __name__ == "__main__":
    main()
