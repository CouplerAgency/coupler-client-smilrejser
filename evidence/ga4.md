# GA4 analysis — smilrejser.dk

Property `smilrejser.dk - GA4` (account: Aller Leisure), 30 May to 27 August
2026, All Users. Two page-level UI exports supplied by the client.

**Absolute revenue figures are deliberately not recorded in this file.** This
repository is public and `evidence/` is served over GitHub Pages. Ratios,
percentages and session counts are here; the raw exports and the joined
per-page revenue table stay in `ga4/`, which is gitignored. Decide before
publishing whether the client is comfortable with any of it being public.

The deck (`index.html`) has not been changed. See "What this changes" below —
it should be.

## Headline: the checkout is the prize, not the catalogue

The audit's most prominent finding was that 45.8% of the trip catalogue cannot
be booked. GA4 says that is real but modest in revenue terms, and that a much
larger amount of money is being lost inside the checkout.

## The checkout funnel, including steps 4 and 5

The manual walk stopped at step 3, because advancing commits a real order
against live inventory. Page-level GA4 data measures all five steps.

Active users, not views, is the denominator: a user who resubmits a failing form
generates several views of the same step and would otherwise look like progress.

| step | users | % of checkout starts | lost vs previous |
|---|---|---|---|
| 1. Accommodation / rooms | 2,516 | 100% | — |
| 2. Add-ons | 704 | 28.0% | 72.0% |
| 3. Personal information | 720 | 28.6% | — |
| 4. Summary (Opsummering) | 223 | 8.9% | **69.0%** |
| 5. Payment (Betaling) | 117 | 4.7% | see note |
| Confirmation | 159 | 6.3% | — |

**71.4% of everyone who starts a booking never reaches the form where they
would type their name.** Of those who do, a further 69.0% never reach the
summary. Only 6.3% of checkout starts reach confirmation.

Both walls sit exactly where the automated walk got stuck. The walk failed at
step 1 because the default traveller count did not match the room selection and
the error message did not say so, and again at step 3 because required fields
gave no indication of what was missing. Those are the two largest losses in the
real funnel. The screenshots in the deck (slides 7 and 8) are pictures of the
two places the money leaves.

Add-ons is not a gate: step 2 has slightly fewer users than step 3, so it is
skipped for departures that have no add-ons.

Views per user by step — 1.63 at step 1, 1.71 at summary — is consistent with
users resubmitting forms that reject them without saying why.

### Note on step 5

Confirmation shows more users (159) than the payment page (117), which cannot
happen in a strict linear funnel. The most likely explanation is that payment is
handled by an external provider: users leave from summary, pay off-site, and
return to confirmation, so `/payment` is only rendered for some routes. The
47.5% figure at that step should therefore **not** be read as a drop-off. This
needs confirming with the dev team before anyone acts on it.

## What the unbookable catalogue actually costs

| | bookable trips | unbookable trips |
|---|---|---|
| pages | 69 | 60 |
| sessions (90d) | 26,511 | 5,297 |
| share of all sessions | 41.3% | 8.2% |
| revenue per session, indexed | 100 | **71** |
| median engagement per session | 95s | 74s |

Sessions landing on an unbookable trip are 16.7% of all trip-page sessions and
8.2% of all sessions. They earn 71% as much per session as sessions landing on a
bookable trip — a real gap, and the shortfall is not total, because many of those
visitors browse on to something they can buy.

Closing that gap entirely would be worth roughly **1.4% of the revenue booked in
this 90-day window**, on the optimistic assumption that these sessions could be
made to behave exactly like bookable-page sessions. Cheap to fix and worth
doing, but an order of magnitude smaller than the checkout opportunity, and
smaller than the deck's framing implies.

## Revenue by entry point, indexed to bookable trips = 100

`pages` counts every page of that type. A handful had no entry traffic in the
window (1 travel-type, 1 hub, 1 guide, 1 blog page), which does not affect the
session or revenue columns since those pages contribute zero to both.

| entry point | pages | sessions | share | rev/session (indexed) | median engagement |
|---|---|---|---|---|---|
| Homepage | 1 | 8,168 | 12.7% | **497** | 204s |
| Travel-type pages | 21 | 2,298 | 3.6% | **274** | 136s |
| Destination hubs | 54 | 4,479 | 7.0% | 151 | 98s |
| Bookable trips | 69 | 26,511 | 41.3% | 100 | 95s |
| Destination guides | 101 | 8,611 | 13.4% | 84 | 91s |
| Unbookable trips | 60 | 5,297 | 8.2% | 71 | 74s |
| Blog posts | 67 posts | 4,118 | 6.4% | **0** | 63s |

Two things stand out.

**Category pages outperform product pages as entry points.** Travel-type pages
earn 2.7x per session what an individual trip page earns, and destination hubs
1.5x, despite far less traffic. Visitors who arrive at a browsable list convert
better than visitors dropped onto one trip. That argues for pointing more
acquisition spend at hubs and travel-type pages, and it is the opposite of the
usual instinct to drive traffic to the product page.

**The blog earns nothing.** 4,118 sessions, 6.4% of all traffic, zero revenue
and zero key events across 90 days, with the lowest engagement on the site at
63 seconds. It is not a conversion asset in its current form and has no internal
linking into bookable inventory worth speaking of (median 1 contextual inbound
link per post, from `linkgraph.md`).

Beware the attribution: revenue is credited to the session's landing page, so
the homepage's figure partly reflects that many buyers simply start there. It
measures entry points, not page quality.

## Dead URLs still taking traffic

GA4 records what visitors requested, so it exposes removed pages a sitemap crawl
cannot see. 20 paths return 404 while still receiving traffic, totalling 501
sessions, but one page is almost all of it:

| sessions | path | status |
|---|---|---|
| 432 | `/italien/trentino-og-dolomitterne` | 404 |
| 39 | `/italien/et-syditaliensk-eventyreventyr` | 404 |
| 11 | `/italien/smag-paa-amalfikysten` | 404 |

The remaining 17 are one or two sessions each — typos and truncated links, not
worth chasing. One redirect fixes 86% of the problem. Full list in
`dead_urls.csv`.

Also: `/solorejser` is live, takes traffic, and is missing from `sitemap.xml`,
alongside the homepage omission already noted in `linkgraph.md`.

## The orphan pages are not worth much

`linkgraph.md` found 26 pages with no inbound link from anywhere, holding 29,281
words. GA4 shows they attract **273 sessions in 90 days between them** — about
three a day. `/seniorrejser`, 6,206 words, gets 22 sessions.

(The 32,145-word figure in `linkgraph.md` covers a slightly wider set: 27 pages
with no in-content link and no nav link. The 26-page set here is the stricter
one — nothing links to them at all.)

So this is a genuine content-management problem and a negligible revenue one. It
belongs in a housekeeping backlog, not in the top five. Good to know before
anyone spends a sprint on it.

## What this changes about the deck

The deck's priority order was built without behavioural data and now looks
wrong in one important respect:

| finding | deck prominence | GA4 verdict |
|---|---|---|
| Checkout validation walls | Finding 4, action 2 | **Should be the headline.** 71% and 69% losses |
| 45.8% catalogue unbookable | headline finding | Real, but ~1.4% of window revenue |
| Category pages convert best | absent | New, actionable, free to exploit |
| Blog earns nothing | absent | 6.4% of traffic, zero revenue |
| Orphan pages | new in linkgraph.md | Negligible traffic, deprioritise |
| Dead URLs | absent | One redirect worth 432 sessions |

Recommendation: promote the checkout findings to the front, keep the catalogue
finding but reframe it with its true size, and add slides for the category-page
and blog findings.

## Caveats

1. **Small conversion volumes.** 201 key events and 159 confirmation users in 90
   days. Site-level and group-level rates are usable; per-page conversion rates
   are not, and none are quoted here.
2. **Landing-page attribution.** Revenue is session-scoped and credited to the
   entry page. It answers "which entry points precede revenue", not "which pages
   persuade".
3. **`page_title` is blank throughout the checkout**, exactly as predicted from
   the missing `document.title`. Every funnel figure here keys on `page_path`.
   Any GA4 exploration built on page titles will show the checkout as one
   undifferentiated blob until that is fixed.
4. **Seasonality.** 30 May to 27 August is the Danish summer. A tour operator
   selling autumn and winter departures may show a different pattern.
5. **Step 1 is not purely intent.** Some users click "Bestil" to see prices with
   no intention of buying, so not all of the 71.4% is a UX failure. The
   resubmission rate suggests a substantial part of it is.
6. **`view_item_list` and `select_item` are still not configured**, so which trip
   cards get impressions and clicks on hub pages remains unanswerable.

## Reproduce

Raw exports must be present in `ga4/` (not in version control).

```bash
python3 scripts/ga4_join.py     # traffic and revenue by page type
python3 scripts/ga4_funnel.py   # the five-step checkout funnel
python3 scripts/ga4_404.py      # -> evidence/dead_urls.csv
```
