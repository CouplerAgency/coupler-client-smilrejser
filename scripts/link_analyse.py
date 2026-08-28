"""Analyse the internal link graph and join it to departure state.

The question this exists to answer: are the 60 trip pages that cannot be booked
better or worse internally linked than the 69 that can? If the dead pages are
linked just as prominently, the site is actively steering traffic into dead ends.

Two inbound measures are reported separately, because mixing them is misleading:
  raw        — every internal link, nav and footer included
  contextual — links outside <header>/<footer>/<nav> only

Nav and footer links appear on all 421 pages, so raw counts are dominated by
template boilerplate and say nothing about editorial prominence.
"""
import csv
import os
import statistics
from collections import defaultdict, deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = lambda *p: os.path.join(ROOT, "evidence", *p)  # noqa: E731

edges = list(csv.DictReader(open(E("links.csv"))))
tax = {r["path"]: r for r in csv.DictReader(open(E("page_taxonomy.csv")))}
crawl = {r["path"]: r for r in csv.DictReader(open(E("crawl.csv")))}

# The header menu only injects its links after a click, so the static crawl never
# saw them. Fold them in as chrome edges or four pages are wrongly called orphans.
try:
    menu_links = {r["path"] for r in csv.DictReader(open(E("megamenu.csv")))}
except FileNotFoundError:
    menu_links = set()

pages = sorted(set(crawl) | {e["source"] for e in edges})
for target in menu_links:
    for source in pages:
        if source != target:
            edges.append({"source": source, "target": target, "region": "chrome",
                          "target_in_sitemap": "1"})
print(f"folded in {len(menu_links)} click-to-open menu targets as chrome edges")

# --- adjacency -------------------------------------------------------------
out_all, out_ctx = defaultdict(set), defaultdict(set)
in_all, in_ctx = defaultdict(set), defaultdict(set)
for e in edges:
    s, t, region = e["source"], e["target"], e["region"]
    out_all[s].add(t)
    in_all[t].add(s)
    if region == "content":
        out_ctx[s].add(t)
        in_ctx[t].add(s)

# --- click depth from the homepage ----------------------------------------
PAGESET = set(pages)


def bfs(adj, root="/"):
    """Depth over known pages only. Without the PAGESET guard this also walks
    /booking/... and /soeg?... targets and reports more reachable nodes than
    there are pages."""
    depth = {root: 0}
    q = deque([root])
    while q:
        u = q.popleft()
        for v in adj.get(u, ()):
            if v in PAGESET and v not in depth:
                depth[v] = depth[u] + 1
                q.append(v)
    return depth


depth_all = bfs(out_all)
depth_ctx = bfs(out_ctx)

print("=" * 78)
print("INTERNAL LINK GRAPH — smilrejser.dk")
print("=" * 78)
print(f"pages in graph          {len(pages)}")
print(f"edges total             {len(edges)}")
print(f"  nav/footer (chrome)   {sum(e['region'] == 'chrome' for e in edges)}")
print(f"  contextual (content)  {sum(e['region'] == 'content' for e in edges)}")

# Boilerplate targets: linked from nearly every page.
boiler = sorted((t for t in in_all if len(in_all[t]) > 0.9 * len(pages)),
                key=lambda t: -len(in_all[t]))
print(f"\ntargets linked from >90% of pages (template boilerplate): {len(boiler)}")
for t in boiler[:12]:
    print(f"  {len(in_all[t]):>4} inbound  {t}")

# --- reachability ----------------------------------------------------------
unreach_all = [p for p in pages if p not in depth_all]
unreach_ctx = [p for p in pages if p not in depth_ctx]
print(f"\nreachable from homepage, any link      {len(depth_all)} / {len(pages)}")
print(f"reachable from homepage, contextual    {len(depth_ctx)} / {len(pages)}")
print(f"UNREACHABLE by contextual links only   {len(unreach_ctx)}")

# Three distinct conditions, worth keeping apart. A page in the global nav has
# 420 inbound links and is trivially reachable, so calling it an orphan because
# no article links to it would be wrong.
boilerset = set(boiler)
truly_orphaned = [p for p in pages if len(in_all[p]) == 0]
nav_only = [p for p in pages
            if p != "/" and len(in_ctx[p]) == 0 and len(in_all[p]) > 0 and p in boilerset]
ctx_orphan_not_nav = [p for p in pages
                      if p != "/" and len(in_ctx[p]) == 0 and p not in boilerset]

print(f"\nlinked from nowhere at all (inbound_raw = 0)   {len(truly_orphaned)}")
for p in sorted(truly_orphaned)[:10]:
    print(f"        {p}")

print(f"reachable ONLY via global nav/footer          {len(nav_only)}")
print(f"      (these are fine — policy pages, FAQ, catalogue)")

print(f"\nNO contextual inbound link AND not in the nav  {len(ctx_orphan_not_nav)}")
print("      (real content assets nothing on the site points to)")
kinds = defaultdict(list)
for p in ctx_orphan_not_nav:
    k = tax.get(p, {}).get("kind") or crawl.get(p, {}).get("template") or "unknown"
    kinds[k].append(p)
for k, ps in sorted(kinds.items(), key=lambda kv: -len(kv[1])):
    print(f"  {len(ps):>4}  {k}")
    ranked = sorted(ps, key=lambda x: -int(crawl.get(x, {}).get("word_count") or 0))
    for p in ranked[:6]:
        wc = crawl.get(p, {}).get("word_count", "?")
        print(f"          {wc:>5} words  {p}")
    if len(ps) > 6:
        print(f"          … and {len(ps) - 6} more")

stranded = sum(int(crawl.get(p, {}).get("word_count") or 0) for p in ctx_orphan_not_nav)
print(f"\n  words stranded on those {len(ctx_orphan_not_nav)} pages: {stranded:,}")

# --- depth distribution ---------------------------------------------------
print("\nclick depth from homepage (contextual links only)")
dist = defaultdict(int)
for p in pages:
    d = depth_ctx.get(p)
    dist["unreachable" if d is None else d] += 1
for d in sorted(dist, key=lambda x: (isinstance(x, str), x)):
    print(f"  depth {str(d):<12} {dist[d]:>4} pages")


# --- the core question: dead vs bookable ----------------------------------
def summarise(label, paths):
    if not paths:
        return
    raw = [len(in_all[p]) for p in paths]
    ctx = [len(in_ctx[p]) for p in paths]
    dep = [depth_ctx[p] for p in paths if p in depth_ctx]
    print(f"  {label:<34} n={len(paths):>4}  "
          f"raw med={statistics.median(raw):>5.1f}  "
          f"ctx med={statistics.median(ctx):>5.1f}  "
          f"ctx mean={statistics.mean(ctx):>5.1f}  "
          f"orphans={sum(1 for c in ctx if c == 0):>3}  "
          f"depth med={statistics.median(dep) if dep else float('nan'):>4.1f}")


trips = [p for p, r in tax.items() if r["kind"] == "trip" and p in crawl]
bookable = [p for p in trips if "bookable" in tax[p]["departure_state"]]
empty = [p for p in trips if "empty" in tax[p]["departure_state"]]
other = [p for p in trips if p not in bookable and p not in empty]

print("\n" + "=" * 78)
print("THE QUESTION: are unbookable trips linked as prominently as bookable ones?")
print("=" * 78)
summarise("BOOKABLE trips", bookable)
summarise("EMPTY (unbookable) trips", empty)
summarise("no visible departure state", other)
summarise("destination guides (editorial-city)",
          [p for p, r in tax.items() if r["kind"] == "editorial-city" and p in crawl])
summarise("thin stubs (editorial-thin)",
          [p for p, r in tax.items() if r["kind"] == "editorial-thin" and p in crawl])
blog = [p for p in crawl if p.startswith("/blog")]
summarise("blog posts", blog)

def classify(p):
    """Best available label for a page, preferring the structural taxonomy."""
    k = tax.get(p, {}).get("kind")
    if k:
        return k
    return crawl.get(p, {}).get("template") or "unknown"


# Where do links to empty trips come from?
def by_source(paths):
    d = defaultdict(int)
    for p in paths:
        for s in in_ctx[p]:
            d[classify(s)] += 1
    return d


src_e, src_b = by_source(empty), by_source(bookable)
print("\nwhere contextual links come from, PER PAGE (so the group sizes cannot mislead)")
print(f"  {'source page type':<22} {'-> bookable (n=69)':>20} {'-> unbookable (n=60)':>22}")
for k in sorted(set(src_e) | set(src_b), key=lambda x: -(src_b.get(x, 0) + src_e.get(x, 0))):
    pb = src_b.get(k, 0) / len(bookable)
    pe = src_e.get(k, 0) / len(empty)
    flag = ""
    if pb > 0 and pe == 0:
        flag = "  <-- never links to dead trips"
    print(f"  {k:<22} {pb:>20.2f} {pe:>22.2f}{flag}")

# Most-linked pages overall, contextually.
print("\nmost contextually linked pages on the site")
top = sorted(pages, key=lambda p: -len(in_ctx[p]))[:14]
for p in top:
    r = tax.get(p, {})
    state = r.get("departure_state", "")
    tag = ""
    if "empty" in state:
        tag = "  <-- CANNOT BE BOOKED"
    elif "bookable" in state:
        tag = "  (bookable)"
    print(f"  {len(in_ctx[p]):>4} inbound  {p}{tag}")

# --- per-page export ------------------------------------------------------
with open(E("linkgraph.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["path", "kind", "departure_state", "inbound_raw", "inbound_contextual",
                "outbound_contextual", "depth_contextual", "is_orphan", "word_count"])
    for p in pages:
        r = tax.get(p, {})
        d = depth_ctx.get(p)
        w.writerow([p, r.get("kind", ""), r.get("departure_state", ""),
                    len(in_all[p]), len(in_ctx[p]), len(out_ctx[p]),
                    "" if d is None else d, int(len(in_ctx[p]) == 0),
                    crawl.get(p, {}).get("word_count", "")])
print(f"\nwrote {E('linkgraph.csv')}")
