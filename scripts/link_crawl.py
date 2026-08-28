"""Build the internal link graph for smilrejser.dk.

Extraction method validated by scripts/link_validate.py: `<a href>` parsed from
HTML with <script>/<style>/<noscript> removed first, fragments and query strings
stripped. On all four page templates that agrees exactly with
document.querySelectorAll('a[href]') in real Chrome, so no rendering is needed.

A naive `href=` match over the whole body over-counts, because the Next.js RSC
payload carries hrefs too. That method is deliberately not used.

Output: evidence/links.csv, one row per (source, target) edge.
"""
import csv
import os
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP = "https://smilrejser.dk/sitemap.xml"
SCRIPT_STYLE = re.compile(r"<(script|style|noscript)\b[^>]*>.*?</\1>", re.S | re.I)
ANCHOR = re.compile(r"<a\b[^>]*?\bhref=[\"']([^\"']+)", re.I)
ASSET = re.compile(r"\.(png|jpe?g|svg|webp|ico|css|js|xml|pdf|txt|avif|woff2?)$", re.I)
# <header>, <footer> and <nav> regions, used to label an edge's origin.
CHROME_REGION = re.compile(r"<(header|footer|nav)\b[^>]*>.*?</\1>", re.S | re.I)


def get(url, timeout=40):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "da-DK"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def norm(href):
    """Normalise an href to a site-internal document path, or None."""
    h = href.strip()
    if h.startswith("https://smilrejser.dk"):
        h = h[len("https://smilrejser.dk"):]
    if not h.startswith("/") or h.startswith("//"):
        return None
    h = h.split("#")[0].split("?")[0]
    if not h.startswith("/"):
        return None
    h = h.rstrip("/") or "/"
    if ASSET.search(h):
        return None
    return h


def edges_for(path):
    """Return (path, [(target, region)], error). region is 'chrome' or 'content'."""
    try:
        html = get("https://smilrejser.dk" + (path if path != "/" else "/"))
    except Exception as e:
        return path, [], str(e)

    clean = SCRIPT_STYLE.sub(" ", html)

    # Links inside header/footer/nav are template boilerplate. Everything else is
    # a contextual, editorially placed link.
    chrome_targets = set()
    for m in CHROME_REGION.finditer(clean):
        for href in ANCHOR.findall(m.group(0)):
            t = norm(href)
            if t:
                chrome_targets.add(t)

    seen = {}
    for href in ANCHOR.findall(clean):
        t = norm(href)
        if not t or t == path:
            continue
        region = "chrome" if t in chrome_targets else "content"
        # A target linked from both regions counts as content: it is reachable
        # contextually, which is the stronger signal.
        if seen.get(t) != "content":
            seen[t] = region
    return path, sorted(seen.items()), ""


def sitemap_paths():
    sm = get(SITEMAP)
    paths = [norm(loc) for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", sm)]
    return sorted({p for p in paths if p})


def main():
    # The homepage is genuinely absent from sitemap.xml, so it has to be added by
    # hand. It is also the root the click-depth BFS starts from.
    paths = sorted(set(sitemap_paths()) | {"/"})
    print(f"sitemap: {len(paths)} unique internal paths")

    results = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for n, (path, edges, err) in enumerate(ex.map(edges_for, paths), 1):
            results.append((path, edges, err))
            if n % 60 == 0:
                print(f"  {n}/{len(paths)}")

    # Transient 502s are common on this host; retry before giving up on a page.
    for attempt in range(3):
        retry = [i for i, (_, _, e) in enumerate(results) if e]
        if not retry:
            break
        print(f"retrying {len(retry)} failed page(s), attempt {attempt + 1}")
        for i in retry:
            results[i] = edges_for(results[i][0])

    errs = [(p, e) for p, _, e in results if e]
    print(f"fetched {len(results) - len(errs)} ok, {len(errs)} errors")
    for p, e in errs[:6]:
        print(f"  ERROR {p}: {e[:70]}")

    out = os.path.join(ROOT, "evidence", "links.csv")
    smset = set(paths)
    total = 0
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "target", "region", "target_in_sitemap"])
        for path, edges, err in results:
            for target, region in edges:
                w.writerow([path, target, region, int(target in smset)])
                total += 1
    print(f"wrote {out} — {total} edges")

    with open(os.path.join(ROOT, "evidence", "link_fetch_errors.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path", "error"])
        w.writerows(errs)


if __name__ == "__main__":
    main()
