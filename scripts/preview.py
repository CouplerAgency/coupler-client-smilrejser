#!/usr/bin/env python3
"""Render deck slides to .preview/ so they can be read back and checked.

Usage: preview.py [slide numbers...]   (default: a representative sample)
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Browser  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, ".preview")
DECK = "file://" + os.path.join(ROOT, "index.html")

DEFAULT = [1, 2, 4, 5, 7, 12, 14, 15]


def main():
    nums = [int(a) for a in sys.argv[1:]] or DEFAULT
    os.makedirs(OUT, exist_ok=True)
    b = Browser(1440, 1000, port=9421)
    try:
        for n in nums:
            # The deck reads location.hash once on load, and a hash-only change does
            # not reload, so bounce through about:blank to force a fresh init.
            b.goto("about:blank", settle=0.3)
            b.goto("%s#%d" % (DECK, n), settle=1.8)
            title = b.eval(
                "(function(){var s=document.querySelector('.slide.is-active');"
                "return s?s.dataset.title:'NO ACTIVE SLIDE';})()")
            h = b.eval("document.querySelector('.slide.is-active')"
                       ".scrollHeight")
            path = os.path.join(OUT, "slide%02d.png" % n)
            size = b.shot(path)
            print("  slide %2d  %-44s h=%spx  %d bytes"
                  % (n, (title or "")[:44], h, size))
    finally:
        b.close()


if __name__ == "__main__":
    main()
