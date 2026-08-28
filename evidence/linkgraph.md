# Internal link graph — smilrejser.dk

Added after the main audit, to fill the one gap a licensed Screaming Frog crawl
would have covered: internal link distribution, click depth and orphan pages.

The deck (`index.html`) was deliberately **not** modified. This is data only.

## Method

`scripts/link_crawl.py` fetched all 420 sitemap URLs plus the homepage and
extracted `<a href>` targets from HTML with `<script>`, `<style>` and
`<noscript>` removed, then stripped fragments and query strings.

`scripts/link_validate.py` justifies that choice. On four page templates the
static extraction agrees exactly with `document.querySelectorAll('a[href]')` in
real Chrome:

| page | naive `href=` | `<a>` after script strip | rendered DOM |
|---|---|---|---|
| homepage | 47 | 46 | 46 |
| bookable trip | 17 | 15 | 15 |
| empty trip | 16 | 14 | 14 |
| destination guide | 27 | 25 | 25 |

A naive `href=` match over the whole body over-counts, because the Next.js RSC
payload carries hrefs too. That is the same trap behind Corrections 1 and 2 in
`log.md`, so it was checked before crawling rather than after.

Edges are split into two regions, because mixing them destroys the signal:

- **chrome** — inside `<header>`, `<footer>` or `<nav>`; appears on all 421 pages
- **contextual** — everywhere else; editorially placed

Totals: **9,617 static edges** across 421 pages, 3,823 contextual and 5,794
chrome. Plus 77 menu links folded in (see below).

## The question this was built to answer

Are the 60 trip pages that cannot be booked less prominently linked than the 69
that can? If they are linked identically, the site is steering its own traffic
into dead ends.

**They are linked identically.**

| group | n | contextual inbound, median | mean | click depth, median | orphans |
|---|---|---|---|---|---|
| Bookable trips | 69 | 13.0 | 13.4 | 2 | 0 |
| **Unbookable trips** | **60** | **12.0** | **12.0** | **2** | **0** |
| No visible departure state | 2 | 16.0 | 16.0 | 2 | 0 |
| Destination guides | 101 | 3.0 | 5.3 | 2 | 9 |
| Thin stubs | 18 | 0.0 | 3.4 | 2 | 12 |
| Blog posts | 68 | 1.0 | 1.2 | 2 | 0 |

A dead trip page carries a median of 12 contextual inbound links against 13 for
a bookable one, and both sit a median of two clicks from the homepage. Nothing
in the internal linking distinguishes a trip you can buy from one you cannot.

Normalised per target page, so the unequal group sizes cannot mislead:

| links from | → bookable (n=69) | → unbookable (n=60) |
|---|---|---|
| travel-type pages | 6.71 | 4.82 |
| destination guides | 2.68 | 2.67 |
| destination hubs | 2.10 | 2.45 |
| info pages | 1.42 | 1.65 |
| thin stubs | 0.26 | 0.30 |
| other trips | 0.12 | 0.08 |
| homepage | 0.14 | **0.00** |

Two mild points in the site's favour: travel-type pages link bookable trips
about 39% more often per page, and the homepage links only bookable trips. The
effect is real but small, and it is swamped by the hub and guide pages, which
show no preference at all.

## Orphan pages

Three conditions worth keeping apart. A page in the global footer has 420
inbound links, so calling it orphaned because no article links to it is wrong.

| condition | count |
|---|---|
| Linked from nowhere at all (inbound = 0, nav included) | **26** |
| Reachable only via global nav/footer — expected, fine | 16 |
| No contextual inbound link and not in the nav | **27** |

Those 27 pages hold **32,145 words** that nothing on the site points to. The
worst cases:

| words | page | type |
|---|---|---|
| 6,206 | `/seniorrejser` | travel-type |
| 4,873 | `/europa/kulturrejser` | destination guide |
| 2,864 | `/flyrejser` | info |
| 2,241 | `/belgien/bruxelles` | destination guide |
| 2,052 | `/marokko/rabat` | destination guide |
| 1,948 | `/belgien/antwerpen` | destination guide |
| 1,920 | `/marokko/tanger` | destination guide |
| 1,762 | `/mellemoesten` | destination hub |
| 1,675 | `/kina/beijing` | destination guide |

`/seniorrejser` is the standout: 6,206 words on a travel-type page aimed at what
is plausibly the core demographic, with no inbound link from anywhere, nav
included. The Belgium and Morocco city guides suggest destinations that were
dropped from the programme while their content stayed behind.

This is a different problem from the 60 dead trip pages. Those are over-exposed;
these are invisible.

## Click depth

Contextual links only, from the homepage:

| depth | pages |
|---|---|
| 0 | 1 |
| 1 | 32 |
| 2 | 289 |
| 3 | 50 |
| 4 | 2 |
| unreachable | 47 |

Of the 374 pages reachable by contextual links, 322 (86%) are within two clicks
and none is deeper than four. The site is genuinely shallow, which is a
strength — no trip is buried.

## Navigation menu

The header menu is **click-to-open, not hover**: dispatching hover events reveals
nothing, while a real click injects the panel. It carries 77 links, 60 of which
appear on every page sampled, and they are all category, hub and info pages.
**No individual trip is linked from the navigation menu.**

Two consequences. First, four pages the static crawl called orphans are in fact
linked here (`/inspiration`, `/naturrejser/solfoermoerkelsesrejser`,
`/om-os/job`, `/tryghed`), and they are excluded from the counts above. Second,
links injected only on click are not reliably discovered by search crawlers, so
the menu should not be assumed to carry link equity.

## Homepage is missing from sitemap.xml

`sitemap.xml` lists 420 URLs and the homepage is not among them:

```
curl -s https://smilrejser.dk/sitemap.xml | grep -c '<loc>https://smilrejser.dk/\?</loc>'
0
```

Harmless for a site this well linked, but it is a one-line fix and the sitemap is
generated, so something in the generator is skipping the root.

## Reproduce

```bash
python3 scripts/link_validate.py     # justify static extraction
python3 scripts/link_crawl.py        # -> evidence/links.csv
python3 scripts/megamenu.py          # -> evidence/megamenu.csv
python3 scripts/link_analyse.py      # -> evidence/linkgraph.csv + this analysis
```

## Corrections made while building this

**Fragment normalisation.** The first validation run reported the static parse
missing nine links on `/portugal/porto`. It was measuring itself wrong: static
hrefs had `#TRAVEL_DEPARTURES` stripped, rendered ones did not, so one link
counted as two. Fixed before crawling.

**A wrong mega-menu finding, caught before it reached the deck.** An early run
clicked each nav trigger in sequence without reloading and reported 121 trip
links in the menu, 60 of them unbookable — a striking finding that was entirely
false. One of the triggers was a plain link, so the run navigated onto a
travel-type page and then counted that page's trip listings as menu contents.
Re-testing each trigger on a freshly loaded page, and discarding any result where
`location.pathname` changed, gives the true answer: the menu holds 77 category
links and no trips at all.

**Off-graph BFS.** The reachability count initially exceeded the number of pages,
because the traversal followed `/booking/...` and `/soeg?...` targets that are not
pages in the crawl set. Restricted to known pages.
