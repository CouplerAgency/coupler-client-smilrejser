"""Find URLs that still receive traffic but no longer resolve.

GA4 records what visitors actually requested, so it exposes removed pages that a
sitemap crawl cannot see by definition. Any path with sessions and a 404 is
traffic being thrown away, and is fixable with a redirect.
"""
import csv
import os
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from ga4_join import E, G, norm, num, read_ga4  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

land, _ = read_ga4(G("landing_pages.csv"))
crawl = {r["path"] for r in csv.DictReader(open(E("crawl.csv")))}

sessions = {}
for r in land:
    p = norm(r["Landing page"])
    if p:
        sessions[p] = sessions.get(p, 0) + num(r["Sessions"])

# Booking and search paths are excluded by robots.txt and are expected to be
# absent from the crawl; they are not candidates for redirects.
candidates = sorted(
    (p for p in sessions
     if p not in crawl
     and not p.startswith("/booking")
     and p not in ("/soeg", "/findrejser")),
    key=lambda p: -sessions[p],
)
print(f"paths with traffic but not in the crawl: {len(candidates)}")


def status(p):
    req = urllib.request.Request(
        "https://smilrejser.dk" + p, method="HEAD",
        headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "da-DK"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return p, r.status, r.geturl()
    except urllib.error.HTTPError as e:
        return p, e.code, ""
    except Exception as e:
        return p, f"ERR {type(e).__name__}", ""


with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(status, candidates))

dead = [(p, c, sessions[p]) for p, c, _ in results if c == 404]
alive = [(p, c, sessions[p]) for p, c, _ in results if c == 200]
other = [(p, c, sessions[p]) for p, c, _ in results if c not in (200, 404)]

dead.sort(key=lambda t: -t[2])
alive.sort(key=lambda t: -t[2])

print(f"\n404 with traffic          {len(dead)}  "
      f"({sum(t[2] for t in dead):,.0f} sessions wasted)")
print(f"200 but not in sitemap    {len(alive)}  "
      f"({sum(t[2] for t in alive):,.0f} sessions)")
print(f"other status              {len(other)}")

print("\n" + "=" * 74)
print("DEAD URLS STILL RECEIVING TRAFFIC — redirect these")
print("=" * 74)
for p, _, s in dead:
    print(f"  {s:>6,.0f} sessions  {p}")

print("\n" + "=" * 74)
print("LIVE PAGES MISSING FROM THE SITEMAP")
print("=" * 74)
for p, _, s in alive[:20]:
    print(f"  {s:>6,.0f} sessions  {p}")
if len(alive) > 20:
    print(f"  … and {len(alive) - 20} more")

if other:
    print("\nnon-200/404 responses")
    for p, c, s in other:
        print(f"  {s:>6,.0f} sessions  HTTP {c}  {p}")

out = os.path.join(ROOT, "evidence", "dead_urls.csv")
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["path", "http_status", "sessions_90d", "action"])
    for p, c, s in dead:
        w.writerow([p, c, f"{s:.0f}", "redirect to closest live trip or hub"])
    for p, c, s in alive:
        w.writerow([p, c, f"{s:.0f}", "add to sitemap if indexable"])
print(f"\nwrote {out}")
print("(session counts only, no revenue — safe to commit)")
