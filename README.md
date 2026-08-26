# Smilrejser — Conversion Rate Optimisation audit

A structural CRO audit of [smilrejser.dk](https://smilrejser.dk), an Aller travel (ALTR) brand.
Deliverable is `index.html`, a 19-slide Coupler deck. Internal — `noindex` in the document and
`Disallow: /` in `robots.txt`.

Performed 26 August 2026, before analytics access was granted. **Every figure in the deck comes
from a public, re-runnable measurement.** There is no conversion rate and no projected uplift
anywhere in it, because there was no data to support one.

## What was measured

| Track | Method | Output |
|---|---|---|
| Crawl | All 421 sitemap URLs — title, meta, headings, images, schema, CTA paths, price presence, TTFB | `evidence/crawl.csv` |
| Departure states | Every trip page re-fetched and classified by its **rendered** departures section, cross-validated against unique `/booking/` hrefs | `evidence/page_taxonomy.csv`, `evidence/trips_departures.csv` |
| Structured data | Genuine `ld+json` blocks only, parsed and walked so nested list members are seen | `evidence/schema_census.csv`, `evidence/itemlist.csv` |
| Visual | Real Chrome over the DevTools Protocol, Danish locale, consent pre-accepted, 1440×1400 and 390×1600 | `assets/shots/` |
| Funnel | Booking funnel walked with dummy data, field inventory and validation probe at each step, stopped before payment | `evidence/funnel.md` |
| Measurement | Public GTM container `GTM-NKQTDQPX` parsed for configured tags, events, consent mode, server-side routing | `evidence/gtm.md` |

`evidence/log.md` is the audit trail. It records the verified claims, what was explicitly **not**
measured and why, hypotheses that were investigated and disproven, and two logged corrections —
including one case where our own first-pass finding turned out to be a measurement artefact.

## Headline numbers

- **60 of 131** sellable trip pages render an empty departures table; the `Bestil rejse` button
  is an in-page anchor that scrolls the visitor to it.
- **151,722 words** of trip copy sit on those 60 pages.
- **103 of 103** destination pages tell Google their trip list is `"Rejser til Frankrig"`.
- **13,321 of 13,448** images are lazy-loaded, including every hero and the logo.
  `fetchpriority="high"` appears zero times across 421 pages.
- **6 of 8** GA4 ecommerce funnel events are already configured, through server-side tagging.

## Reproducing

Python 3 standard library only — no dependencies to install. Chrome must be present for anything
that renders.

```bash
python3 scripts/crawl.py           # crawl all sitemap URLs        -> evidence/crawl.csv
python3 scripts/classify_pass3.py  # structural page classification -> evidence/page_taxonomy.csv
python3 scripts/schema_census.py   # ld+json census                -> evidence/schema_census.csv
python3 scripts/itemlist_check.py  # ItemList names                -> evidence/itemlist.csv
python3 scripts/capture.py         # screenshots, both viewports   -> assets/shots/
python3 scripts/funnel.py          # funnel walk, stops before payment
python3 scripts/gtm_audit.py       # GTM container parse           -> evidence/gtm.md

python3 scripts/verify_deck.py     # recompute every deck number from the evidence
python3 scripts/preview.py 1 2 3   # render individual slides to .preview/ for inspection
```

`verify_deck.py` is the gate: it recomputes each headline figure from the CSVs and asserts the
deck agrees. Run it after any edit to `index.html`.

## Notes on method

Two things worth knowing if you extend this work:

1. **Never string-match the raw HTML on this site.** It is Next.js App Router, so the response
   body also contains the React Server Component payload, where i18n label dictionaries and
   serialised component props live. Searching it for `"@type":"Product"` or
   `"Afgange ikke tilgængelige"` produces false positives on every page. Both mistakes were made
   and caught here — see `evidence/log.md`, Corrections 1 and 2.
2. **Screaming Frog was the original plan and could not be used.** The local install is v24.3
   unlicensed; the free tier has no CLI, no headless mode, no JS rendering and no export. The
   purpose-built crawler replaced it and captures CRO fields Screaming Frog has no column for.
