"""Reconstruct the five-step checkout funnel from GA4 page data.

This closes the gap the audit could not: the manual walk stopped at step 3
because advancing commits a real order, so steps 4 and 5 were never assessed.
Page-level GA4 data measures all five.

Active users, not views, is the right denominator — a user who re-submits a
failing form generates several views of the same step and would otherwise look
like progress.

Note the checkout emits no document.title, so GA4's page_title dimension is
blank throughout. Everything here keys on page_path.
"""
import re
import sys
from collections import defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from ga4_join import G, num, read_ga4  # noqa: E402

PP = "Page path and screen class"
rows, meta = read_ga4(G("pages_screens.csv"))

steps = defaultdict(lambda: {"views": 0.0, "users": 0.0, "urls": 0})
for r in rows:
    p = r[PP].split("?")[0].rstrip("/")
    if "/booking" not in p:
        continue
    key = re.sub(r"/\d+", "/{id}", p)
    d = steps[key]
    d["views"] += num(r["Views"])
    d["users"] += num(r["Active users"])
    d["urls"] += 1

ORDER = [
    ("1. Accommodation / rooms", "/booking/travel/{id}/{id}/accommodation"),
    ("2. Add-ons", "/booking/travel/{id}/{id}/addons"),
    ("3. Personal information", "/booking/travel/{id}/{id}/personal-information"),
    ("4. Summary (Opsummering)", "/booking/travel/{id}/{id}/summary"),
    ("5. Payment (Betaling)", "/booking/travel/{id}/{id}/payment"),
    ("Confirmation", "/booking/travel/confirmation"),
]

print("=" * 88)
print(f"CHECKOUT FUNNEL — {meta.get('Property')}, "
      f"{meta.get('Start date')} to {meta.get('End date')}")
print("=" * 88)
print(f"{'step':<28}{'users':>8}{'views':>8}{'views/user':>12}"
      f"{'% of step 1':>13}{'drop from prev':>16}")

start = steps[ORDER[0][1]]["users"]
prev = None
for label, key in ORDER:
    d = steps.get(key)
    if not d:
        print(f"{label:<28}{'no data':>8}")
        continue
    u, v = d["users"], d["views"]
    share = u / start if start else 0
    drop = "" if prev is None else f"{(prev - u) / prev:>15.1%}" if prev else ""
    print(f"{label:<28}{u:>8,.0f}{v:>8,.0f}{v / u if u else 0:>12.2f}"
          f"{share:>12.1%}{drop:>16}")
    prev = u

conf = steps.get("/booking/travel/confirmation", {}).get("users", 0)
summary = steps.get("/booking/travel/{id}/{id}/summary", {}).get("users", 0)
step3 = steps.get("/booking/travel/{id}/{id}/personal-information", {}).get("users", 0)

print("\nother booking paths seen")
for k, v in sorted(steps.items(), key=lambda kv: -kv[1]["users"]):
    if k not in dict((b, a) for a, b in ORDER).keys() and k not in [b for _, b in ORDER]:
        print(f"  {k:<52}{v['users']:>7,.0f} users")

print("\n" + "=" * 88)
print("READING THE FUNNEL")
print("=" * 88)
print(f"checkout starts (step 1 users)        {start:,.0f}")
print(f"reached step 3                        {step3:,.0f}  "
      f"({step3 / start:.1%} of starts)")
print(f"reached step 4 (Summary)              {summary:,.0f}  "
      f"({summary / start:.1%} of starts)")
print(f"reached Confirmation                  {conf:,.0f}  "
      f"({conf / start:.1%} of starts)")

print("\nThe two largest losses:")
step2 = steps.get("/booking/travel/{id}/{id}/addons", {}).get("users", 0)
entry_to_3 = (start - step3) / start if start else 0
print(f"  step 1 -> step 3   {entry_to_3:.1%} of users lost before entering any details")
print(f"  step 3 -> step 4   {(step3 - summary) / step3:.1%} of users lost at the "
      f"personal-information form")
print(f"\n  step 2 (add-ons) has {step2:,.0f} users vs {step3:,.0f} at step 3, so add-ons")
print("  is skipped for some departures rather than being a hard gate.")

# Views per user is the tell for repeated failed submissions.
print("\nviews per user by step — above ~1.5 suggests repeated submissions")
for label, key in ORDER:
    d = steps.get(key)
    if d and d["users"]:
        vpu = d["views"] / d["users"]
        flag = "  <-- users resubmitting" if vpu > 1.5 else ""
        print(f"  {label:<28}{vpu:>6.2f}{flag}")

# Sensitivity, deliberately framed as illustrative rather than forecast.
land, _ = read_ga4(G("landing_pages.csv"))
revenue = sum(num(r["Total revenue"]) for r in land)
key_events = sum(num(r["Key events"]) for r in land)
aov = revenue / key_events if key_events else 0
print("\n" + "=" * 88)
print("SENSITIVITY — illustrative, not a forecast")
print("=" * 88)
print(f"revenue in window                     {revenue:,.0f} DKK")
print(f"key events (= confirmation views)     {key_events:,.0f}")
print(f"implied average order value           {aov:,.0f} DKK")
print(f"\ndownstream rate from step 3 to confirmation: {conf / step3:.1%}")
for pp in (5, 10, 20):
    extra_u = start * (pp / 100)
    extra_bookings = extra_u * (conf / step3) if step3 else 0
    print(f"  recovering {pp:>2}pp of the step 1->3 loss "
          f"= {extra_u:>6,.0f} more users to step 3 "
          f"= {extra_bookings:>5,.0f} bookings "
          f"= {extra_bookings * aov:>10,.0f} DKK per 90 days")
print("\nAssumes recovered users behave like current step-3 users, which is")
print("optimistic: the ones lost at a validation wall may be less committed.")
