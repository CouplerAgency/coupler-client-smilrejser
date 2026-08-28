"""Join GA4 page data to the structural audit.

Answers the question the whole audit has been pointing at: what does traffic
landing on the 60 unbookable trip pages actually cost?

Inputs (gitignored — this repo is public):
  ga4/landing_pages.csv  session-scoped, revenue attributed to entry page
  ga4/pages_screens.csv  pageview-scoped, engagement per page

Both are GA4 UI exports: a '#' preamble, then a header row, then data.
"""
import csv
import os
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
E = lambda *p: os.path.join(ROOT, "evidence", *p)  # noqa: E731
G = lambda *p: os.path.join(ROOT, "ga4", *p)  # noqa: E731


def read_ga4(path):
    """Strip the '#' preamble and return (rows, meta)."""
    meta = {}
    with open(path, encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    start = 0
    for i, ln in enumerate(lines):
        if ln.startswith("#"):
            m = re.match(r"#\s*([A-Za-z ]+):\s*(.+)", ln)
            if m:
                meta[m.group(1).strip()] = m.group(2).strip()
            continue
        if ln.strip():
            start = i
            break
    return list(csv.DictReader(lines[start:])), meta


def num(v):
    try:
        return float(str(v).replace(",", "").strip() or 0)
    except ValueError:
        return 0.0


def norm(p):
    """Match the normalisation used by the link crawler."""
    p = (p or "").strip()
    if p.startswith("https://smilrejser.dk"):
        p = p[len("https://smilrejser.dk"):]
    p = p.split("#")[0].split("?")[0]
    if not p.startswith("/"):
        return None
    return p.rstrip("/") or "/"


def main():
    land, meta_l = read_ga4(G("landing_pages.csv"))
    page, meta_p = read_ga4(G("pages_screens.csv"))

    print("=" * 84)
    print("GA4 JOIN — smilrejser.dk")
    print("=" * 84)
    print(f"property        {meta_l.get('Property')}")
    print(f"date range      {meta_l.get('Start date')} to {meta_l.get('End date')}")
    print(f"landing rows    {len(land)}")
    print(f"page rows       {len(page)}")

    LP = "Landing page"
    PP = "Page path and screen class"

    # --- data hygiene ---------------------------------------------------------
    notset = [r for r in land if r[LP].strip() == "(not set)"]
    print(f"\n'(not set)' landing rows: {len(notset)} "
          f"({sum(num(r['Sessions']) for r in notset):,.0f} sessions) — excluded")

    landing = {}
    for r in land:
        p = norm(r[LP])
        if p is None:
            continue
        d = landing.setdefault(p, {"sessions": 0.0, "users": 0.0, "new": 0.0,
                                   "key_events": 0.0, "revenue": 0.0, "engage": []})
        d["sessions"] += num(r["Sessions"])
        d["users"] += num(r["Active users"])
        d["new"] += num(r["New users"])
        d["key_events"] += num(r["Key events"])
        d["revenue"] += num(r["Total revenue"])
        d["engage"].append(num(r["Average engagement time per session"]))

    views = {}
    for r in page:
        p = norm(r[PP])
        if p is None:
            continue
        d = views.setdefault(p, {"views": 0.0, "users": 0.0, "events": 0.0,
                                 "engage": []})
        d["views"] += num(r["Views"])
        d["users"] += num(r["Active users"])
        d["events"] += num(r["Event count"])
        d["engage"].append(num(r["Average engagement time per active user"]))

    tot_sessions = sum(v["sessions"] for v in landing.values())
    tot_rev = sum(v["revenue"] for v in landing.values())
    tot_key = sum(v["key_events"] for v in landing.values())
    print(f"\ntotal sessions (matched paths)  {tot_sessions:,.0f}")
    print(f"total revenue                   {tot_rev:,.0f} DKK")
    print(f"total key events                {tot_key:,.0f}")

    # --- structural join ------------------------------------------------------
    tax = {r["path"]: r for r in csv.DictReader(open(E("page_taxonomy.csv")))}
    lg = {r["path"]: r for r in csv.DictReader(open(E("linkgraph.csv")))}
    crawl = {r["path"]: r for r in csv.DictReader(open(E("crawl.csv")))}

    matched = set(landing) & set(crawl)
    unmatched_ga = sorted(set(landing) - set(crawl),
                          key=lambda p: -landing[p]["sessions"])
    print(f"\nGA4 landing paths matching the crawl : {len(matched)} of {len(landing)}")
    print(f"GA4 paths not in the crawl           : {len(unmatched_ga)}")
    print("  biggest unmatched (these are real pages the audit never saw):")
    for p in unmatched_ga[:12]:
        print(f"    {landing[p]['sessions']:>8,.0f} sessions  {p}")

    crawled_no_traffic = [p for p in crawl if p not in landing]
    print(f"\ncrawled pages with zero landing sessions: {len(crawled_no_traffic)}")


    def group(paths, label):
        paths = [p for p in paths if p in landing]
        if not paths:
            return None
        s = sum(landing[p]["sessions"] for p in paths)
        rev = sum(landing[p]["revenue"] for p in paths)
        ke = sum(landing[p]["key_events"] for p in paths)
        eng = [e for p in paths for e in landing[p]["engage"] if e]
        return {
            "label": label, "n": len(paths), "sessions": s, "revenue": rev,
            "key_events": ke,
            "rev_per_session": rev / s if s else 0,
            "cvr": ke / s if s else 0,
            "engage": statistics.median(eng) if eng else 0,
        }


    trips = [p for p, r in tax.items() if r["kind"] == "trip"]
    bookable = [p for p in trips if "bookable" in tax[p]["departure_state"]]
    empty = [p for p in trips if "empty" in tax[p]["departure_state"]]

    rows = [
        group(bookable, "Bookable trips"),
        group(empty, "UNBOOKABLE trips"),
        group([p for p, r in tax.items() if r["kind"] == "editorial-city"], "Destination guides"),
        group([p for p, r in tax.items() if r["kind"] == "editorial-thin"], "Thin stubs"),
        group([p for p in crawl if p.startswith("/blog")], "Blog posts"),
        group([p for p in crawl if crawl[p]["template"] == "travel-type"], "Travel-type pages"),
        group([p for p in crawl if crawl[p]["template"] == "destination-hub"], "Destination hubs"),
        group(["/"], "Homepage"),
    ]

    print("\n" + "=" * 84)
    print("TRAFFIC AND REVENUE BY PAGE TYPE (revenue attributed to landing page)")
    print("=" * 84)
    print(f"{'group':<22}{'pages':>6}{'sessions':>11}{'% sess':>8}"
          f"{'revenue DKK':>14}{'rev/sess':>10}{'key ev':>8}{'CVR':>8}{'engage s':>10}")
    for r in rows:
        if not r:
            continue
        print(f"{r['label']:<22}{r['n']:>6}{r['sessions']:>11,.0f}"
              f"{r['sessions'] / tot_sessions * 100:>7.1f}%{r['revenue']:>14,.0f}"
              f"{r['rev_per_session']:>10,.0f}{r['key_events']:>8,.0f}"
              f"{r['cvr'] * 100:>7.2f}%{r['engage']:>10,.0f}")

    # --- the headline ---------------------------------------------------------
    b, e = group(bookable, "b"), group(empty, "e")
    print("\n" + "=" * 84)
    print("THE COST OF THE UNBOOKABLE CATALOGUE")
    print("=" * 84)
    print(f"sessions landing on a trip page that cannot be booked : {e['sessions']:,.0f}")
    print(f"  as a share of all sessions                          : {e['sessions'] / tot_sessions:.1%}")
    print(f"  as a share of all trip-page sessions                : "
          f"{e['sessions'] / (e['sessions'] + b['sessions']):.1%}")
    print(f"\nrevenue per session, bookable landing   : {b['rev_per_session']:,.0f} DKK")
    print(f"revenue per session, unbookable landing : {e['rev_per_session']:,.0f} DKK")
    if e["rev_per_session"] and b["rev_per_session"]:
        print(f"  ratio                                 : "
              f"{e['rev_per_session'] / b['rev_per_session']:.2f}x")
    gap = (b["rev_per_session"] - e["rev_per_session"]) * e["sessions"]
    print(f"\nIf unbookable-landing sessions converted at the bookable rate:")
    print(f"  additional revenue over the 90 days   : {gap:,.0f} DKK")
    print(f"  annualised                            : {gap * 365 / 90:,.0f} DKK")
    print("  (an upper bound, not a forecast — see caveats in the report)")

    print(f"\nkey-event rate, bookable   : {b['cvr']:.3%}")
    print(f"key-event rate, unbookable : {e['cvr']:.3%}")

    # Worst offenders: high traffic, cannot be booked.
    print("\nhighest-traffic pages that CANNOT be booked")
    top = sorted((p for p in empty if p in landing),
                 key=lambda p: -landing[p]["sessions"])[:15]
    for p in top:
        d = landing[p]
        print(f"  {d['sessions']:>7,.0f} sessions  {d['revenue']:>10,.0f} DKK  {p}")

    # --- do the orphans get traffic? -----------------------------------------
    print("\n" + "=" * 84)
    print("ORPHAN PAGES — do they get traffic despite no internal links?")
    print("=" * 84)
    orph = [p for p, r in lg.items()
            if r["is_orphan"] == "1" and p != "/" and int(r["inbound_raw"] or 0) == 0]
    with_traffic = [p for p in orph if p in landing]
    print(f"pages with zero inbound links of any kind : {len(orph)}")
    print(f"  of those, receiving landing sessions    : {len(with_traffic)}")
    print(f"  their combined sessions                 : "
          f"{sum(landing[p]['sessions'] for p in with_traffic):,.0f}")
    for p in sorted(with_traffic, key=lambda x: -landing[x]["sessions"])[:10]:
        d = landing[p]
        wc = crawl.get(p, {}).get("word_count", "?")
        print(f"    {d['sessions']:>6,.0f} sessions  {wc:>5} words  {p}")

    # --- per-page export (local only) ----------------------------------------
    out = G("joined.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path", "kind", "departure_state", "sessions", "active_users",
                    "key_events", "revenue_dkk", "views", "inbound_contextual",
                    "depth", "is_orphan", "word_count"])
        for p in sorted(set(landing) | set(views)):
            L = landing.get(p, {})
            V = views.get(p, {})
            t = tax.get(p, {})
            g = lg.get(p, {})
            w.writerow([p, t.get("kind", ""), t.get("departure_state", ""),
                        f"{L.get('sessions', 0):.0f}", f"{L.get('users', 0):.0f}",
                        f"{L.get('key_events', 0):.0f}", f"{L.get('revenue', 0):.2f}",
                        f"{V.get('views', 0):.0f}", g.get("inbound_contextual", ""),
                        g.get("depth_contextual", ""), g.get("is_orphan", ""),
                        crawl.get(p, {}).get("word_count", "")])
    print(f"\nwrote {out} (gitignored — contains revenue)")


if __name__ == "__main__":
    main()
