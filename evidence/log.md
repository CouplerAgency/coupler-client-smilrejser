# Evidence log — Smilrejser CRO audit

Every claim in the deck traces to a row here. Rows marked `In deck: N` were verified but
did not make the final cut. Corrections are appended as new `CORRECTION` rows, never by
editing history.

Audit window: 2026-08-26. Site: https://smilrejser.dk/

## Verified claims

| Claim | Source | Date | In deck |
|---|---|---|---|
| `robots.txt` contains `Disallow: /booking/` | Live `https://smilrejser.dk/robots.txt` | 2026-08-26 | Y |
| `robots.txt` blocks search + all 6 filter params (`*soeg*`, `*dates=*`, `*destinationTags=*`, `*travelTypes=*`, `*transportTypes=*`, `*departureFrom=*`) | Live `https://smilrejser.dk/robots.txt` | 2026-08-26 | Y |
| Sitemap contains 420 URLs | `curl https://smilrejser.dk/sitemap.xml \| grep -c '<loc>'` | 2026-08-26 | Y |
| Sitemap composition: 68 blog, 55 italien, 39 portugal, 30 spanien, 14 england, 12 frankrig, 10 graekenland | Parsed from sitemap.xml `<loc>` paths | 2026-08-26 | Y |
| Homepage HTML is 2.67 MB (2,675,292 bytes) | `curl -w '%{size_download}' https://smilrejser.dk/` | 2026-08-26 | Y |
| Homepage TTFB 1.00s | `curl -w '%{time_starttransfer}'` | 2026-08-26 | Y |
| Trip page HTML 845 KB (844,763 bytes), TTFB 1.16s | `curl -w` on `/portugal/nytaarsrejse-til-lissabon` | 2026-08-26 | Y |
| Booking step 1 HTML 227 KB (227,089 bytes), TTFB 1.31s | `curl -w` on `/booking/travel/49000/6095/accommodation` | 2026-08-26 | Y |
| All 35 `<img>` tags on homepage carry `loading="lazy"` | `rg -c '<img'` = 35, `rg -c 'loading="lazy"'` = 35 | 2026-08-26 | Y |
| `fetchpriority="high"` appears zero times on homepage | `rg -c 'fetchpriority'` returns no case-sensitive match for high | 2026-08-26 | Y |
| Site logo is lazy-loaded at 176x40 | First `<img>` on homepage: `loading="lazy" width="176" height="40"` src `smilrejser_logo_long.svg` | 2026-08-26 | Y |
| GTM and Trustpilot are `rel=preload as=script`, own chunks are `fetchPriority="low"` | Homepage `<link rel="preload">` tags | 2026-08-26 | Y |
| GTM container ID is `GTM-NKQTDQPX` | Homepage inline GTM snippet | 2026-08-26 | Y |
| GTM container holds 9 distinct GA4 measurement IDs | Public `googletagmanager.com/gtm.js?id=GTM-NKQTDQPX` parsed for `G-` pattern | 2026-08-26 | Y |
| Container has 25 GA4 event tags (`__gaawe`), 5 Google tags (`__googtag`), 7 paused tags (`__paused`) | Public gtm.js tag-type counts | 2026-08-26 | Y |
| Cookiebot consent mode is configured (`wait_for_update`, `ads_data_redaction`, `url_passthrough`) | Public gtm.js | 2026-08-26 | Y |
| Homepage structured data is only `Organization` + `WebSite` (+PostalAddress, SearchAction) | 3 `ld+json` blocks on homepage | 2026-08-26 | Y |
| Trip page structured data includes `Product`, `Offer`, `AggregateOffer`, `FAQPage`, `BreadcrumbList` | 4 `ld+json` blocks on `/portugal/nytaarsrejse-til-lissabon` | 2026-08-26 | Y |
| Images served via imgix (`smilrejser-dk.imgix.net`) with `auto=format` | Homepage img src params | 2026-08-26 | Y |
| Booking funnel entry URL pattern is `/booking/travel/{travelId}/{departureId}/accommodation` | `href` on trip page | 2026-08-26 | Y |
| Site is Next.js App Router (`/_next/static/`, `_rsc=` param in robots) | Homepage asset paths + robots.txt | 2026-08-26 | Y |
| Client logo is a true-transparency SVG, colours `#083d3e` and `#5e9a69` | `assets/smilrejser-logo.svg` fill values | 2026-08-26 | N |

## Crawl findings — 421 URLs, all HTTP 200

Method: `scripts/crawl.py` (pass 1, all 421), `scripts/trips_pass2.py` (pass 2, departure
states), `scripts/classify_pass3.py` (pass 3, structural classification). Raw output in
`evidence/crawl.csv`, `evidence/trips_departures.csv`, `evidence/page_taxonomy.csv`.

| Claim | Source | Date | In deck |
|---|---|---|---|
| All 421 crawled URLs return HTTP 200 — no broken pages, no redirect chains | `crawl.csv` status column | 2026-08-26 | Y |
| Of 250 trip-shaped URLs, only **131 are actually sellable trips** (have `data-id-section="TRAVEL_DEPARTURES"`) | `page_taxonomy.csv` kind column | 2026-08-26 | Y |
| **69 of 131 trip pages (52.7%) can be booked online**; 60 (45.8%) show "Afgange ikke tilgængelige"; 2 show no visible state | `page_taxonomy.csv` departure_state | 2026-08-26 | Y |
| The primary CTA "Bestil rejse" is `href="#TRAVEL_DEPARTURES"` — an in-page anchor, not a booking link — on **all 131** trip pages | `classify_pass3.py` book_cta_is_anchor = 131 | 2026-08-26 | Y |
| On the 60 empty trips, that CTA scrolls to a table rendering `<div ...text-center">Afgange ikke tilgængelige</div>` | Rendered DOM, `raw/rendered-zero.html`, verified with headless Chrome | 2026-08-26 | Y |
| The 60 empty trip pages carry **151,722 words** of copy, averaging 2,528 words each | `page_taxonomy.csv` word_count sum over state D | 2026-08-26 | Y |
| Empty trips concentrate in Italy (12), Portugal (9), Spain (8), river cruises (5) | `page_taxonomy.csv` grouped by country | 2026-08-26 | Y |
| 55 of 131 trip pages show no DKK price at all | 131 trips, 76 with price | 2026-08-26 | Y |
| **119 editorial pages sit on trip-shaped URLs** — 101 city/region pages, 18 stubs under 500 words | `page_taxonomy.csv` kind | 2026-08-26 | Y |
| **103 of 119 editorial pages emit `Product` schema** despite having no departures section and nothing to buy | `page_taxonomy.csv` has_product_schema by kind (87 city + 16 thin) | 2026-08-26 | Y |
| The design system already contains unused departure states: `DEPARTURE_SALE_ON_REQUEST_BTN` = "Forespørg", `DEPARTURE_SALE_WAITLIST_BTN` = "Venteliste", `DEPARTURE_NO_DEPARTURES` = "Afgange ikke tilgængelige" | i18n label dictionary in page payload | 2026-08-26 | Y |
| A waitlist section (`data-id-section="TRAVEL_WAITLIST"`) with "Kontakt mig ved nye rejsedatoer" exists below the empty table | Rendered DOM of `/italien/madlavningskursus-paa-amalfikysten` | 2026-08-26 | Y |
| Median TTFB across all 421 pages is 1,267 ms; p90 is 2,422 ms; max 6,242 ms | `crawl.csv` ttfb_ms | 2026-08-26 | Y |
| 73 of 421 pages exceed 2s TTFB; 41 pages ship over 1 MB of HTML | `crawl.csv` | 2026-08-26 | Y |
| **Travel-type pages are the worst template**: median TTFB 2,106 ms, median 1,050 KB HTML | `crawl.csv` grouped by template, n=21 | 2026-08-26 | Y |
| Largest single page is 8,073 KB of HTML (an info page) | `crawl.csv` max html_bytes | 2026-08-26 | Y |
| Across the site, 13,321 of 13,448 images are `loading="lazy"`; 127 eager; **zero** pages use `fetchpriority="high"` | `crawl.csv` sums | 2026-08-26 | Y |
| **4,167 of 13,448 images (31%) have no alt text** | `crawl.csv` img_missing_alt sum | 2026-08-26 | Y |
| 289 of 421 meta descriptions exceed 160 characters; 154 titles exceed 60 characters | `crawl.csv` | 2026-08-26 | Y |
| Trustpilot, Rejsegarantifonden and Travelife appear on all 421 pages | `crawl.csv` trust columns | 2026-08-26 | Y |
| Every page has a canonical tag; no page is missing an H1; only 1 page has multiple H1s | `crawl.csv` | 2026-08-26 | Y |

## Booking funnel walkthrough

Method: `scripts/funnel.py` and `scripts/funnel_advance.py` driving real Chrome over CDP,
desktop 1440x1400 and mobile 390x1500, Danish locale. Entry
`/booking/travel/49000/6095/accommodation` (Nytårsrejse til Lissabon, 29.12.2026, 9.995 DKK).
Dummy data only, nothing submitted, no payment details ever entered.

| Claim | Source | Date | In deck |
|---|---|---|---|
| The funnel is 5 steps: **1 Overnatning, 2 Tilvalg, 3 Personlige oplysninger, 4 Opsummering, 5 Betaling** | Progress indicator, both viewports | 2026-08-26 | Y |
| **Step 1 ships in an invalid state.** Travellers defaults to 1, both room counters default to 0, so the step cannot be submitted as presented | Screenshot `funnel-1-overnatning-desktop.png` | 2026-08-26 | Y |
| Clicking "Videre" from that default state returns the error "Der opstod en fejl — Antallet af værelser og personer matcher ikke. Ret venligst til korrekt antal for at komme videre med din booking." | Screenshot `funnel-1-validation-desktop.png`, verbatim | 2026-08-26 | Y |
| **Step 3 holds 27 form fields** — traveller details, booker details, 2 insurance dropdowns, discount code, payment option, 2 consent checkboxes | Field inventory in `evidence/funnel.md` | 2026-08-26 | Y |
| **Not one field carries the HTML `required` attribute** (`required: false`, `aria-required: false` on all 27) even though 10 labels are marked `*` | Field inventory | 2026-08-26 | Y |
| **Validation errors read "Required" in English** on a Danish-language checkout | Step 3 empty-submit probe, 3 identical "Required" strings | 2026-08-26 | Y |
| **Two near-identical Gouda insurance dropdowns** sit adjacent: "Afbestillings- og rejseforsikring hos Gouda Rejseforsikring" and "Afbestillingsforsikring hos Gouda Rejseforsikring", both defaulting to "Rejsende 1 - Nej, tak" | Screenshot `funnel-3-still-blocked-desktop.png` | 2026-08-26 | Y |
| The single room selected as "Enkeltværelse" is billed in the summary as **"Dobbeltværelse til 1 person +995 DKK"** | Same screenshot, right-hand summary panel | 2026-08-26 | Y |
| **A discount-code field ("Din rabatkode") sits inside the checkout** | Step 3 field inventory | 2026-08-26 | Y |
| **No phone number anywhere in the funnel** (`has_phone: false` at every step), despite a `tel:` link on all 421 public pages | Field inventory, all steps both viewports | 2026-08-26 | Y |
| **Mobile hides the price.** Steps 1 and 2 report no visible total on mobile; desktop shows 10.090 DKK then 11.085 DKK | `evidence/funnel.md`, `price_visible` and `total` per viewport | 2026-08-26 | Y |
| **Mobile drops the step names** from the progress indicator: "1 Overnatning 2 3 4 5" versus all five labelled on desktop and tablet | Body text at 390px vs 768px vs 1440px | 2026-08-26 | Y |
| `document.title` is **empty on every funnel step** | `document.title` returned `''` at steps 1-3; re-verified 2026-08-31 with a 6s settle and four samples 2s apart, still `''`, and no `<title>` element present | 2026-08-26 | Y, but **withdrawn as a finding** — see CORRECTION 4 |
| Cancel is offered twice per step — "Annuller booking" top-left and "Annuller" bottom-left | Button inventory, every step | 2026-08-26 | Y |
| The +/- traveller and room counters have **no text and no `aria-label`** | Button inventory: 6 buttons with empty `txt` and `null` `aria` | 2026-08-26 | Y |
| Selecting a single room raises the total from 10.090 to 11.085 DKK (+995 single-room supplement) | Totals at step 1 vs step 2, desktop | 2026-08-26 | Y |

**Not observed: steps 4 and 5.** The walk reliably reached step 3 and filled it, but did not
advance to Opsummering. Rather than keep submitting against a live booking system holding
real inventory, the walk was stopped. Step 4 and the payment step are therefore **not
assessed in this audit** and no claim is made about them. Re-testing them properly needs a
staging environment or a test departure.

## Measurement readiness — container `GTM-NKQTDQPX`

Method: `scripts/gtm_audit.py` parsing the public container JS. Full output in
`evidence/gtm.md`. Only the container's own `tags` array is trusted; the bundled GA4
runtime references every standard event name regardless of configuration.

| Claim | Source | Date | In deck |
|---|---|---|---|
| One shared container serves **10 Aller travel hostnames**, selecting GA4 property and server-side endpoint per host via an `__smm` lookup macro | `macros` array, hostname->value maps | 2026-08-26 | Y |
| **Smilrejser's GA4 property is `G-2STC9KYPG1`** | Lookup table entries `smilrejser.dk` and `www.smilrejser.dk` | 2026-08-26 | Y |
| **Server-side GTM is live** at `sgtm.smilrejser.dk`; `/healthy` returns HTTP 200 in 0.22s, DNS resolves to `eue.stape.net` (Stape) | `curl` + `dig` | 2026-08-26 | Y |
| Consent Mode is properly wired: `wait_for_update`, `ads_data_redaction`, `url_passthrough`, `ad_storage`, `analytics_storage`, Cookiebot referenced | Container consent config | 2026-08-26 | Y |
| Enhanced-conversion PII is hashed client-side: `form_data.email_sha256`, `form_data.phone_number_sha256` | Container macros | 2026-08-26 | Y |
| **The GA4 ecommerce funnel is configured**: `view_item`, `add_to_cart`, `begin_checkout`, `add_payment_info`, `add_shipping_info`, `purchase` — plus `purchase_giftcard` | `vtp_eventName` inside `tags` array | 2026-08-26 | Y |
| Lead and engagement events configured: `waitinglist_form_submit`, `newsletter_form_submit`, `contact_form_submit`, `catalogue_form_submit`, `interest_form_submit`, `lead_form_submit`, `signup_lecture`, `site_search`, `click_tel`, `click_mail`, `initiate_filter`, `filter` | Same | 2026-08-26 | Y |
| **`view_item_list` and `select_item` are NOT configured** — the two events that would show which trips are seen in listings and which get clicked | Absent from `vtp_eventName` set | 2026-08-26 | Y |
| Also unconfigured: `view_cart`, `remove_from_cart`, `refund`, `generate_lead`, `sign_up` | Same | 2026-08-26 | Y |
| **9 legacy Universal Analytics Enhanced Ecommerce dataLayer variables remain**: `ecommerce.purchase.actionField.revenue`, `.id`, `.shipping`, `ecommerce.purchase.products`, `ecommerce.items`, `ecommerce.currency`, `ecommerce.value`, `ecommerce.transaction_id`, `ecommerce.shipping` | `vtp_name` values | 2026-08-26 | Y |
| Container holds 25 GA4 event tags, 18 Custom HTML tags, 5 Google tag configs, 4 LinkedIn Insight tags, 1 Conversion Linker | Tag function counts | 2026-08-26 | Y |
| **3 paused tags** inside the tags array (6 `__paused` references across the file) | `"function":"__paused"` in tags array | 2026-08-26 | Y |
| No Google Ads conversion IDs (`AW-`) or Floodlight IDs (`DC-`) in the container | Regex over full container | 2026-08-26 | Y |

**CORRECTION 3 — 2026-08-26.** (Numbered out of sequence because it belongs with the
measurement evidence above; corrections 1 and 2 are in the Corrections section below.)
The pre-read framed "nine GA4 measurement IDs in one
container" as a finding, implying fragmented or duplicated tracking. That framing is wrong.
The IDs are a hostname lookup table for ten sibling brands, each with its own GA4 property
and its own server-side endpoint. It is a deliberate multi-brand architecture, and the
measurement stack is the **strongest** part of the setup audited here, not a weakness. The
genuine gaps are narrow and specific: `view_item_list`, `select_item`, and legacy UA
variables left behind. Two practical consequences do follow from the shared container: any
change ships to ten brands at once, and Smilrejser's data is nonetheless cleanly isolatable.

Also corrected: an initial string-search of the whole container found `purchase` 12 times and
`add_to_cart` 7 times, which would have supported either conclusion. Those counts are
meaningless — GTM bundles the GA4 runtime, which names every standard ecommerce event.
Only `vtp_eventName` inside the `tags` array reflects configuration.

## Investigated and rejected as findings

Recorded so these are not re-raised later, and so the deck cannot be accused of missing them.

| Suspected issue | What we checked | Verdict |
|---|---|---|
| Consent banner appears in **Norwegian** on a Danish site | First headless capture rendered "Denne nettsiden anvender cookies / Ikke tillat / Egenskaper". Re-rendered with `--lang=da-DK --accept-lang=da-DK,da`, which produced "Vi bruger cookies" | **Not a client bug.** Cookiebot auto-detects from `Accept-Language`. The Norwegian text was an artefact of this Mac's own locale. All audit screenshots are therefore captured with an explicit Danish locale. |
| Trip pages missing `Product` schema | 129 of 129 fetched trip pages emit top-level `Product` in a real ld+json block | **Clean, and a strength.** |
| Editorial pages emitting `Product` schema | Raised as a finding in pass 1, then disproven — see Correction 2. Editorial pages emit `Collection` and `TouristDestination`; `Product` only appears nested as a list member | **Not a bug.** Correct markup for a listing page. Replaced by the hardcoded `ItemList` name finding. |
| Broken links / redirect chains | All 421 sitemap URLs returned HTTP 200 | **Clean.** No finding. |
| Missing canonicals or H1s | 421 of 421 have canonical and exactly one H1 (1 exception) | **Clean.** No finding. |
| Missing trust signals | Trustpilot, Rejsegarantifonden, Travelife on all 421 pages | **Clean, and a genuine strength.** |

## Explicitly NOT measured

| Gap | Why | Consequence for this audit |
|---|---|---|
| Google Analytics / GA4 data | No account access granted yet | No conversion rates, no traffic figures, no funnel drop-off percentages anywhere in the deck |
| Google Search Console | No access | No impression, click or query data; SEO findings are structural only |
| Google Ads / Meta Ads | No access | No CPA, ROAS or landing-page-level paid performance |
| Session recordings / heatmaps | No tool installed that we can read | No behavioural evidence; all UX findings are heuristic or structural |
| Revenue, PAX, AOV | Client-side systems (Travelize) | No financial impact modelling, no projected uplift figures |
| A/B test history | Unknown | Cannot say whether any of this has been tested before |
| Screaming Frog crawl | Local install is v24.3 **unlicensed** (`"licenced": false` in sf-analytics) — free tier has no CLI, no headless, no JS rendering, no export | Replaced with purpose-built crawler over the 420 sitemap URLs |

## Corrections

Seven in total across the audit. Corrections 1, 2 and 4 are below, correction 3 sits with the
measurement evidence above, and three more from the internal-link work are documented at the
foot of `linkgraph.md` — including one striking finding that turned out to be an artefact of
the measurement script and never reached the deck.

**CORRECTION 4 — 2026-08-31.** The deck carried a finding, and a *Critical*-rated action,
saying the five booking steps had no page title and recommending we add one. Smilrejser
pointed out that the booking steps are titled, with what reads as a breadcrumb in the header.
They are right about what matters, and the finding has been removed from the deck.

What we measured was correct as far as it went. Re-checked on 2026-08-31 in a real browser
with a six-second settle and four title samples two seconds apart, `document.title` is `''`
on `/booking/travel/49000/6095/accommodation` and there is no `<title>` element in the
document at all. A control trip page in the same session returned
`"Nytårsrejse til Lissabon | Fejr nytår i Portugals hovedstad"`, so the measurement method
was sound.

What we got wrong was the significance, in two ways.

1. *We described a reporting gap as if it were a customer-facing one.* The booking page
   renders a numbered progress bar in its header — `1 Overnatning 2 Tilvalg 3 Personlige
   oplysninger 4 Opsummering 5 Betaling` — with all five steps named on desktop. A customer
   always knows which step they are on. Writing "give each booking step a page title" reads
   as plainly false to anyone with the site open, because the step names are right there.
2. *We rated it Critical.* It cost no customer anything. The only consequence was that our
   own funnel had to be keyed on `page_path` rather than `page_title`, which took no extra
   effort and changed none of the numbers. A tidiness item for analytics reporting does not
   belong beside defects that turn buyers away.

Consequences of the removal: the action list drops from 17 items to 16 and is renumbered
throughout; the phase-1 total falls from ten hours to nine; the checkout proposal drops from
nine changes to eight. No measured figure in the deck changes — the 71.4% and 69.0% drops,
the 2,516 starts and the 159 confirmations were all derived from `page_path` and never
depended on titles.

One thing genuinely worth noting, and now recorded only here rather than as a
recommendation: on mobile the same progress bar shows only step 1 by name and renders the
rest as bare numbers. That is a real customer-facing gap, and it is already covered by
finding 6 and its action, which is about the mobile booking experience.


**CORRECTION 1 — 2026-08-26.** First pass concluded "181 of 250 trip pages (72%) cannot be
booked". That was wrong twice over, and both errors were caught by verifying the mechanism
before writing the finding.

1. *Wrong denominator.* 119 of those 250 URLs are not trip pages at all — they are city
   inspiration pages and category stubs that have no departures section. Classifying by URL
   shape (`/{country}/{slug}`) produced the error; classifying by the presence of
   `data-id-section="TRAVEL_DEPARTURES"` fixed it.
2. *Wrong detector.* Searching the HTML for the string "Afgange ikke tilgængelige" matches
   every page on the site, because the phrase lives in the i18n label dictionary that ships
   in every payload. The reliable signal is the rendered element
   `<div ...text-center">Afgange ikke tilgængelige</div>`. Naive matching claimed 131 pages;
   the rendered-element check found 60.

Corrected figure: **of 131 genuinely sellable trip pages, 69 (52.7%) are bookable online and
60 (45.8%) render an empty departures table.** Cross-validated against the count of unique
`/booking/` hrefs, which agrees on every page.

**Note on "Forespørg".** Pass 2 found 85 pages showing a "Forespørg" (enquire) button with no
booking link, which looked like a third page-level state. It is not: 74 of those are
editorial city pages listing related trips, where "Forespørg" belongs to an individual trip
card. Departure state is a per-departure property, not a per-page one, so no page-level claim
is made about it.

**CORRECTION 2 — 2026-08-26.** First pass concluded "103 of 119 editorial pages emit `Product`
schema while having nothing to sell". **That was wrong, and the finding has been replaced.**

The crawler set `has_product_schema` by regex-matching `"@type"\s*:\s*"Product"` anywhere in
the response body (`scripts/crawl.py`, line 153). On a Next.js App Router site the response
body also contains the React Server Component payload, where schema objects appear as
serialised component props. Matching there says nothing about what is emitted to a crawler.

Re-checked with `scripts/schema_census.py`, which parses only genuine
`<script type="application/ld+json">` blocks and walks nesting so list members are seen.
248 of 250 trip-shaped URLs fetched successfully:

| Page class | Pages | Top-level `Product` | Top-level types actually emitted |
|---|---|---|---|
| trip | 129 | **129** | `Product`, `BreadcrumbList`, `AggregateOffer`; `FAQPage` on 56 |
| editorial-city | 101 | **0** | `Collection`, `TouristDestination`, `BreadcrumbList`; `ItemList` on 87 |
| editorial-thin | 18 | **0** | `Collection`, `TouristDestination`, `BreadcrumbList`; `ItemList` on 16 |

So editorial pages **never** claim to be products. They emit `Collection` and
`TouristDestination`, which is correct for a destination guide. `Product` appears on them only
as a nested `ItemList` → `ListItem` → `item`, describing each linked trip — conventional,
correct markup for a listing page. The original finding was an artefact of the detector.

**The real defect, found while re-checking.** All 103 pages that emit an `ItemList` name it
`"Rejser til Frankrig"` ("Trips to France"). One hardcoded string, on pages about Porto,
Marrakech, Madrid, Salzburg and Azores. Verified by fetching all 103 individually
(`scripts/itemlist_check.py`, output `evidence/itemlist.csv`):

- 103 of 103 `ItemList` blocks carry that exact name — no page uses any other string.
- 70 of them sit under a country segment that is demonstrably not France. The remaining 33 sit
  on themed URLs (`/europa/kulturrejser`, `/jul-og-nytaar/...`) with no country in the path to
  compare against, so they are counted as unverifiable rather than wrong.
- `numberOfItems` matches the actual item count on all 103, and the `Product` names inside are
  the correct trips for the page. The surrounding implementation is sound; one string is not.
- Trip pages emit no `ItemList` at all, so the bug is confined to destination pages.

Lesson applied to the rest of the audit: on this site, no claim about emitted markup is made
from a raw-HTML string match. Every schema claim in the deck now comes from a parsed ld+json
block, and the departure-state claims come from the rendered DOM.
