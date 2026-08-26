#!/usr/bin/env python3
"""
Audit the public GTM container GTM-NKQTDQPX.

This is the one area where hard findings are possible with no client access at all,
because a GTM container is served publicly to every visitor. It tells us what the
site is currently capable of measuring — which is exactly the shopping list for the
moment analytics access is granted.

Parses the container for measurement IDs, tag types, triggers, paused tags and, most
importantly, whether ecommerce events exist for the booking funnel.
"""

import json
import os
import re
import ssl
import urllib.request
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "evidence", "gtm.md")
RAW = os.path.join(ROOT, "raw", "gtm.js")
CONTAINER = "GTM-NKQTDQPX"
URL = "https://www.googletagmanager.com/gtm.js?id=" + CONTAINER

# GTM's internal tag-type codes.
TAG_TYPES = {
    "__gaawe": "GA4 event",
    "__googtag": "Google tag (config)",
    "__gclidw": "Conversion Linker",
    "__cl": "Click listener (all elements)",
    "__lcl": "Click listener (links only)",
    "__fsl": "Form-submit listener",
    "__tl": "Timer listener",
    "__hl": "History-change listener",
    "__jel": "JS-error listener",
    "__evl": "Element-visibility listener",
    "__paused": "PAUSED tag",
    "__html": "Custom HTML",
    "__img": "Custom image pixel",
    "__awct": "Google Ads conversion",
    "__sp": "Google Ads remarketing",
    "__flc": "Floodlight counter",
    "__fls": "Floodlight sales",
    "__bzi": "LinkedIn Insight",
    "__twitter_website_tag": "X/Twitter pixel",
}

# GA4 recommended ecommerce events for a purchase funnel.
ECOM = ["view_item_list", "view_item", "select_item", "add_to_cart",
        "begin_checkout", "add_payment_info", "add_shipping_info",
        "purchase", "refund", "view_cart", "remove_from_cart",
        "generate_lead", "sign_up"]


def fetch():
    if os.path.exists(RAW) and os.path.getsize(RAW) > 100000:
        return open(RAW, encoding="utf-8", errors="replace").read()
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(
        req, timeout=45, context=ssl.create_default_context()).read()
    os.makedirs(os.path.dirname(RAW), exist_ok=True)
    with open(RAW, "wb") as f:
        f.write(data)
    return data.decode("utf-8", "replace")


def main():
    js = fetch()

    # The container's own configuration lives in the "tags" array. Everything before
    # it is the bundled GTM/GA4 runtime, which references every standard ecommerce
    # event name whether or not this container uses one. Searching the whole file for
    # "purchase" therefore proves nothing; only vtp_eventName inside a tag does.
    tags_at = js.find('"tags":[')
    tags_blob = js[tags_at:] if tags_at > 0 else ""
    configured = Counter(re.findall(r'"vtp_eventName":"([^"]+)"', tags_blob))
    tag_funcs = Counter(re.findall(r'\{"function":"(__[a-z_]+)"', tags_blob))
    # Legacy Universal Analytics Enhanced Ecommerce dataLayer paths.
    ua_ecom = sorted(set(re.findall(
        r'"vtp_name":"(ecommerce\.[A-Za-z0-9_.]+)"', js)))
    paused = len(re.findall(r'"function":"__paused"', tags_blob))

    # The 9 GA4 IDs are selected by a hostname lookup table (__smm macro), not
    # fired all at once. Reconstruct the table so we can name the one property that
    # belongs to this client instead of implying nine properties are in play.
    def lookup_table(value_re):
        out = {}
        for m in re.finditer(
                r'\["map","key","([^"]+)","value","((?:[^"\\]|\\.)*)"\]', js):
            host, val = m.group(1), m.group(2).replace("\\/", "/")
            if re.match(value_re, val):
                out[host] = val
        return out

    ga_by_host = lookup_table(r"^G-")
    sgtm_by_host = lookup_table(r"^https?://")
    brand_map = {h: (ga_by_host.get(h), sgtm_by_host.get(h))
                 for h in set(ga_by_host) | set(sgtm_by_host)}
    smil_id = ga_by_host.get("smilrejser.dk") or ga_by_host.get("www.smilrejser.dk")
    smil_sgtm = sgtm_by_host.get("smilrejser.dk")

    ids = Counter(re.findall(r"\bG-[A-Z0-9]{9,10}\b", js))
    aw = Counter(re.findall(r"\bAW-\d{9,}\b", js))
    dc = Counter(re.findall(r"\bDC-\d+\b", js))
    gt = Counter(re.findall(r"\bGT-[A-Z0-9]{7,}\b", js))
    types = Counter(re.findall(r'"(__[a-z_]+)"', js))
    event_names = Counter(re.findall(r'"eventName":"([^"]+)"', js))
    # GA4 event tags carry their event name in the params blob too.
    ev2 = Counter(re.findall(r"eventName['\"]?\s*:\s*['\"]([a-z_0-9]+)['\"]", js))

    ecom_found = {e: configured[e] for e in ECOM if configured.get(e)}

    consent = {
        "cookiebot_referenced": len(re.findall(r"cookiebot", js, re.I)),
        "wait_for_update": len(re.findall(r"wait_for_update", js)),
        "ads_data_redaction": len(re.findall(r"ads_data_redaction", js, re.I)),
        "url_passthrough": len(re.findall(r"url_passthrough", js)),
        "ad_storage": len(re.findall(r"ad_storage", js)),
        "analytics_storage": len(re.findall(r"analytics_storage", js)),
    }

    lines = []
    a = lines.append
    a("# GTM container audit — `%s`\n" % CONTAINER)
    a("Source: public `%s`, fetched 2026-08-26 (%d KB).\n" % (URL, len(js) // 1024))
    a("A GTM container is served publicly to every visitor, so this can be audited "
      "in full\nwithout any client account access. It defines the ceiling on what "
      "the site can\ncurrently measure.\n")

    a("## This is a shared multi-brand container\n")
    a("The 9 GA4 measurement IDs are not duplication or drift. They are a hostname\n"
      "lookup table: one shared container serves the whole Aller travel brand\n"
      "portfolio and picks the right GA4 property and the right server-side endpoint\n"
      "per domain. That is a deliberate and competent architecture.\n")
    if brand_map:
        a("| Hostname | GA4 property | Server-side endpoint |")
        a("|---|---|---|")
        for host in sorted(brand_map, key=lambda h: (h != "smilrejser.dk", h)):
            ga, sg = brand_map[host]
            me = " **<- this client**" if "smilrejser" in host else ""
            a("| `%s`%s | `%s` | `%s` |" % (host, me, ga or "-", sg or "-"))
        a("")
    a("**Smilrejser's own GA4 property is `%s`.** That is the single ID to request\n"
      "access to — not the container, and not the other brands' properties.\n"
      % (smil_id or "unknown"))
    a("Two consequences worth stating plainly: any container change is a change to\n"
      "**%d brands at once**, so it needs release discipline; and Smilrejser's data can\n"
      "be isolated cleanly, because it has its own property and its own endpoint.\n"
      % len(set(v[0] for v in brand_map.values() if v[0])) if brand_map else "")

    a("## Other measurement IDs\n")
    a("| ID | Type |")
    a("|---|---|")
    for k in sorted(aw):
        a("| `%s` | Google Ads |" % k)
    for k in sorted(dc):
        a("| `%s` | Floodlight/DV360 |" % k)
    for k in sorted(gt):
        a("| `%s` | Google tag |" % k)
    if not (aw or dc or gt):
        a("| _none_ | No Google Ads, Floodlight or DV360 IDs in the container |")
    a("")

    a("## Tag and trigger types\n")
    a("| Code | Meaning | Count |")
    a("|---|---|---|")
    for code, n in types.most_common():
        if code in TAG_TYPES:
            a("| `%s` | %s | %d |" % (code, TAG_TYPES[code], n))
    a("")
    unknown = [c for c in types if c not in TAG_TYPES]
    if unknown:
        a("Other codes present: %s\n" % ", ".join("`%s`" % u for u in sorted(unknown)[:20]))

    a("## Events actually configured on tags\n")
    a("Extracted from `vtp_eventName` inside the container's `tags` array, so these are\n"
      "configured tags rather than incidental references in the bundled GA4 runtime.\n")
    a("| Event name | Tags |")
    a("|---|---|")
    for k, v in configured.most_common():
        mark = " (ecommerce)" if k in ECOM else ""
        a("| `%s`%s | %d |" % (k, mark, v))
    a("")

    a("### GA4 ecommerce funnel coverage\n")
    a("| Standard GA4 ecommerce event | Configured? |")
    a("|---|---|")
    for e in ECOM:
        a("| `%s` | %s |" % (e, "**yes**" if e in ecom_found else "no"))
    missing = [e for e in ECOM if e not in ecom_found]
    a("")
    a("Configured: %s\n" % (", ".join("`%s`" % e for e in ecom_found) or "none"))
    a("Not configured: %s\n" % ", ".join("`%s`" % e for e in missing))

    if ua_ecom:
        a("### Legacy Universal Analytics ecommerce variables\n")
        a("The container still reads Universal Analytics Enhanced Ecommerce dataLayer\n"
          "paths. UA stopped processing data in 2023, and GA4 expects a different\n"
          "`items[]` structure, so any tag depending on these reads an object that the\n"
          "site may no longer populate.\n")
        for v in ua_ecom:
            a("- `%s`" % v)
        a("")

    a("## Tag functions inside the tags array\n")
    a("| Code | Meaning | Count |")
    a("|---|---|---|")
    for code, n in tag_funcs.most_common():
        a("| `%s` | %s | %d |" % (code, TAG_TYPES.get(code, "unknown"), n))
    a("")
    a("Paused tags: **%d**\n" % paused)

    a("## Consent mode\n")
    a("| Signal | Occurrences |")
    a("|---|---|")
    for k, v in consent.items():
        a("| `%s` | %d |" % (k, v))
    a("")

    a("## Event names declared\n")
    allev = event_names + ev2
    if allev:
        a("| Event name | Count |")
        a("|---|---|")
        for k, v in allev.most_common(40):
            a("| `%s` | %d |" % (k, v))
    else:
        a("No `eventName` values could be extracted from the container body.")
    a("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("GA4 IDs (%d) are a per-hostname lookup table:" % len(ids))
    for host in sorted(brand_map):
        ga, sg = brand_map[host]
        print("   %-34s %-16s %s" % (host, ga or "-", sg or "-"))
    print()
    print("SMILREJSER property : %s" % smil_id)
    print("SMILREJSER sGTM     : %s" % smil_sgtm)
    print("Google Ads IDs: %s" % (", ".join(sorted(aw)) or "none"))
    print("Floodlight: %s" % (", ".join(sorted(dc)) or "none"))
    print()
    print("tag types:")
    for c, n in types.most_common():
        if c in TAG_TYPES:
            print("   %-24s %-34s %d" % (c, TAG_TYPES[c], n))
    print()
    print("CONFIGURED events (vtp_eventName in tags array): %d distinct" % len(configured))
    for k, v in configured.most_common():
        print("   %-28s %d%s" % (k, v, "   <- ecommerce" if k in ECOM else ""))
    print()
    print("ecommerce CONFIGURED: %s" % (", ".join(ecom_found) or "NONE"))
    print("ecommerce MISSING   : %s" % ", ".join(missing))
    print()
    print("legacy UA ecommerce vars: %d" % len(ua_ecom))
    for v in ua_ecom:
        print("   ", v)
    print()
    print("paused tags in container:", paused)
    print("consent:", json.dumps(consent))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
