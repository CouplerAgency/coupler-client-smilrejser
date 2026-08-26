# GTM container audit — `GTM-NKQTDQPX`

Source: public `https://www.googletagmanager.com/gtm.js?id=GTM-NKQTDQPX`, fetched 2026-08-26 (583 KB).

A GTM container is served publicly to every visitor, so this can be audited in full
without any client account access. It defines the ceiling on what the site can
currently measure.

## This is a shared multi-brand container

The 9 GA4 measurement IDs are not duplication or drift. They are a hostname
lookup table: one shared container serves the whole Aller travel brand
portfolio and picks the right GA4 property and the right server-side endpoint
per domain. That is a deliberate and competent architecture.

| Hostname | GA4 property | Server-side endpoint |
|---|---|---|
| `smilrejser.dk` **<- this client** | `G-2STC9KYPG1` | `https://sgtm.smilrejser.dk` |
| `alive.dk` | `G-WG64HSYCZ4` | `https://sgtm.alive.dk` |
| `gaiatravel.dk` | `G-021KRVNK2Z` | `https://sgtm.gaiatravel.dk` |
| `nillesgislev.dk` | `G-8D6W4EQETM` | `https://sgtm.nillesgislev.dk/` |
| `reisebloggen.allertravel.no` | `G-2VHL3PTERD` | `https://sgtm.allertravel.no` |
| `www.allertravel.no` | `G-2VHL3PTERD` | `https://sgtm.allertravel.no` |
| `www.kulturrejser-europa.dk` | `G-CVDVFW9Z3Z` | `https://sgtm.kulturrejser-europa.dk` |
| `www.kulturresor-europa.se` | `G-RM89NKLHC2` | `https://sgtm.kulturresor-europa.se` |
| `www.nyhavn.dk` | `G-B8N9GBTNWF` | `https://sgtm.nyhavn.dk` |
| `www.smilrejser.dk` **<- this client** | `G-2STC9KYPG1` | `https://sgtm.smilrejser.dk` |
| `www.stjernegaard-rejser.dk` | `G-0910TZ3QH7` | `https://sgtm.stjernegaard-rejser.dk` |

**Smilrejser's own GA4 property is `G-2STC9KYPG1`.** That is the single ID to request
access to — not the container, and not the other brands' properties.

Two consequences worth stating plainly: any container change is a change to
**9 brands at once**, so it needs release discipline; and Smilrejser's data can
be isolated cleanly, because it has its own property and its own endpoint.

## Other measurement IDs

| ID | Type |
|---|---|
| _none_ | No Google Ads, Floodlight or DV360 IDs in the container |

## Tag and trigger types

| Code | Meaning | Count |
|---|---|---|
| `__gaawe` | GA4 event | 25 |
| `__html` | Custom HTML | 18 |
| `__cl` | Click listener (all elements) | 12 |
| `__lcl` | Click listener (links only) | 9 |
| `__fsl` | Form-submit listener | 8 |
| `__paused` | PAUSED tag | 6 |
| `__googtag` | Google tag (config) | 5 |
| `__hl` | History-change listener | 5 |
| `__tl` | Timer listener | 5 |
| `__bzi` | LinkedIn Insight | 4 |
| `__gclidw` | Conversion Linker | 1 |

Other codes present: `__aev`, `__analytics_storage`, `__awec`, `__baut`, `__c`, `__cid`, `__ctv`, `__cvt_`, `__dbg`, `__e`, `__f`, `__hid`, `__hjtc`, `__jsm`, `__module_features`, `__module_gtag`, `__module_object`, `__proto__`, `__r`, `__sdl`

## Events actually configured on tags

Extracted from `vtp_eventName` inside the container's `tags` array, so these are
configured tags rather than incidental references in the bundled GA4 runtime.

| Event name | Tags |
|---|---|
| `standard` | 18 |
| `signup_lecture` | 2 |
| `custom` | 2 |
| `gtm.timer` | 2 |
| `lead_form_submit` | 1 |
| `newsletter_form_submit` | 1 |
| `contact_form_submit` | 1 |
| `catalogue_form_submit` | 1 |
| `view_item` (ecommerce) | 1 |
| `add_to_cart` (ecommerce) | 1 |
| `begin_checkout` (ecommerce) | 1 |
| `add_payment_info` (ecommerce) | 1 |
| `add_shipping_info` (ecommerce) | 1 |
| `purchase` (ecommerce) | 1 |
| `site_search` | 1 |
| `click_tel` | 1 |
| `click_mail` | 1 |
| `click` | 1 |
| `initiate_filter` | 1 |
| `filter` | 1 |
| `interest_form_submit` | 1 |
| `purchase_giftcard` | 1 |
| `waitinglist_form_submit` | 1 |

### GA4 ecommerce funnel coverage

| Standard GA4 ecommerce event | Configured? |
|---|---|
| `view_item_list` | no |
| `view_item` | **yes** |
| `select_item` | no |
| `add_to_cart` | **yes** |
| `begin_checkout` | **yes** |
| `add_payment_info` | **yes** |
| `add_shipping_info` | **yes** |
| `purchase` | **yes** |
| `refund` | no |
| `view_cart` | no |
| `remove_from_cart` | no |
| `generate_lead` | no |
| `sign_up` | no |

Configured: `view_item`, `add_to_cart`, `begin_checkout`, `add_payment_info`, `add_shipping_info`, `purchase`

Not configured: `view_item_list`, `select_item`, `refund`, `view_cart`, `remove_from_cart`, `generate_lead`, `sign_up`

### Legacy Universal Analytics ecommerce variables

The container still reads Universal Analytics Enhanced Ecommerce dataLayer
paths. UA stopped processing data in 2023, and GA4 expects a different
`items[]` structure, so any tag depending on these reads an object that the
site may no longer populate.

- `ecommerce.currency`
- `ecommerce.items`
- `ecommerce.purchase.actionField.id`
- `ecommerce.purchase.actionField.revenue`
- `ecommerce.purchase.actionField.shipping`
- `ecommerce.purchase.products`
- `ecommerce.shipping`
- `ecommerce.transaction_id`
- `ecommerce.value`

## Tag functions inside the tags array

| Code | Meaning | Count |
|---|---|---|
| `__gaawe` | GA4 event | 21 |
| `__tg` | unknown | 21 |
| `__html` | Custom HTML | 15 |
| `__cl` | Click listener (all elements) | 9 |
| `__baut` | unknown | 8 |
| `__lcl` | Click listener (links only) | 6 |
| `__fsl` | Form-submit listener | 5 |
| `__paused` | PAUSED tag | 3 |
| `__sdl` | unknown | 3 |
| `__tl` | Timer listener | 2 |
| `__googtag` | Google tag (config) | 1 |
| `__hjtc` | unknown | 1 |
| `__bzi` | LinkedIn Insight | 1 |
| `__gclidw` | Conversion Linker | 1 |
| `__hl` | History-change listener | 1 |

Paused tags: **3**

## Consent mode

| Signal | Occurrences |
|---|---|
| `cookiebot_referenced` | 3 |
| `wait_for_update` | 4 |
| `ads_data_redaction` | 5 |
| `url_passthrough` | 3 |
| `ad_storage` | 72 |
| `analytics_storage` | 35 |

## Event names declared

| Event name | Count |
|---|---|
| `standard` | 18 |
| `load` | 2 |
| `signup_lecture` | 2 |
| `custom` | 2 |
| `lead_form_submit` | 1 |
| `newsletter_form_submit` | 1 |
| `contact_form_submit` | 1 |
| `catalogue_form_submit` | 1 |
| `view_item` | 1 |
| `add_to_cart` | 1 |
| `begin_checkout` | 1 |
| `add_payment_info` | 1 |
| `add_shipping_info` | 1 |
| `purchase` | 1 |
| `site_search` | 1 |
| `click_tel` | 1 |
| `click_mail` | 1 |
| `click` | 1 |
| `initiate_filter` | 1 |
| `filter` | 1 |
| `interest_form_submit` | 1 |
| `purchase_giftcard` | 1 |
| `waitinglist_form_submit` | 1 |

