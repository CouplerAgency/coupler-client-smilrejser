#!/usr/bin/env python3
"""
Walk the Smilrejser booking funnel and screenshot every step.

Funnel: 1 Overnatning -> 2 Tilvalg -> 3 Personlige oplysninger -> 4 Opsummering
        -> 5 Betaling

SAFETY. The walk stops at step 4 (Opsummering) and never confirms. Advancing from
4 to 5 is what commits the order to the payment provider, so going further risks
creating a real booking and holding a real seat. All personal data is obviously
fake. Nothing is submitted.

Also records, per step: field inventory, which fields are required, whether a
price stays visible, whether cancellation terms are reachable, and what validation
does when the step is submitted empty.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Browser  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "assets", "shots")
REPORT = os.path.join(ROOT, "evidence", "funnel.md")

START = "https://smilrejser.dk/booking/travel/49000/6095/accommodation"

DUMMY = {
    "fornavn": "Testfornavn", "efternavn": "Testefternavn",
    "navn": "Testfornavn Testefternavn",
    "email": "audit-test@example.invalid",
    "mail": "audit-test@example.invalid",
    "telefon": "00000000", "phone": "00000000", "tlf": "00000000",
    "adresse": "Testvej 1", "postnummer": "1000", "by": "København",
    "zip": "1000", "city": "København",
}

CLICK_BY_TEXT = r"""
(function(label){
  var els = Array.from(document.querySelectorAll('button,a,[role=button]'));
  var el = els.find(function(e){
    var t = (e.innerText||'').replace(/\s+/g,' ').trim().toLowerCase();
    return t === label.toLowerCase();
  });
  if(!el) return 'NOTFOUND';
  if(el.disabled) return 'DISABLED';
  el.scrollIntoView({block:'center'});
  el.click();
  return 'clicked';
})(%s);
"""

# The traveller/room pickers are +/- buttons with NO text and NO aria-label, so they
# can only be reached structurally. Each room type is one <li> holding exactly two
# buttons: [decrement, increment]. Target the <li> by its label text, then take the
# second button. Scoping to the enclosing <ul> instead picks up the Dobbeltværelse
# increment, which is disabled on this departure, and the click silently does nothing.
BUMP_ROOM = r"""
(function(want){
  var lis = Array.from(document.querySelectorAll('li'));
  var row = lis.find(function(r){
    return r.textContent.indexOf(want) >= 0
        && r.querySelectorAll('button').length === 2;
  });
  if(!row) return 'NOROW';
  var btns = row.querySelectorAll('button');
  var plus = btns[1];
  if(plus.disabled) return 'DISABLED';
  plus.scrollIntoView({block:'center'});
  plus.click();
  return 'bumped';
})(%s);
"""

INVENTORY = r"""
(function(){
  var f = Array.from(document.querySelectorAll('input,select,textarea'))
    .filter(function(e){ return e.type!=='hidden'; })
    .map(function(e){
      var lab='';
      if(e.id){ var l=document.querySelector('label[for="'+e.id+'"]'); if(l) lab=l.innerText.trim(); }
      if(!lab && e.placeholder) lab=e.placeholder;
      if(!lab && e.getAttribute('aria-label')) lab=e.getAttribute('aria-label');
      return {tag:e.tagName.toLowerCase(), type:e.type||'', name:e.name||e.id||'',
              label:(lab||'').replace(/\s+/g,' ').slice(0,60),
              required:!!e.required, aria:e.getAttribute('aria-required')==='true'};
    });
  var btns = Array.from(document.querySelectorAll('button'))
    .map(function(b){return {t:(b.innerText||'').replace(/\s+/g,' ').trim(),
                             disabled:b.disabled};})
    .filter(function(b){return b.t;});
  var body = document.body.innerText.replace(/\s+/g,' ');
  return JSON.stringify({
    url: location.pathname,
    step: (body.match(/\b([1-5])\s+(Overnatning|Tilvalg|Personlige|Opsummering|Betaling)/)||[])[0]||'',
    fields: f, buttons: btns,
    price_visible: /Samlet pris|DKK/.test(body),
    total: (body.match(/Samlet pris\s*([\d.]+\s*DKK)/)||[])[1]||'',
    has_terms: /betingelser|afbestilling|fortrydelse/i.test(body),
    has_phone: !!document.querySelector('a[href^="tel:"]'),
    has_progress: /1\s*Overnatning/.test(body),
    heading: (document.querySelector('h1')||{}).innerText||'',
    chars: body.length
  });
})();
"""


def snap(b, name, label):
    path = os.path.join(SHOTS, "funnel-%s-%s.png" % (name, label))
    # Force a repaint before capturing. At 390px wide the first capture after
    # navigation intermittently came back as a blank white page below the header
    # even though the DOM was fully populated (verified: 326 chars of text, 12
    # buttons). Nudging the scroll position and waiting a beat makes it reliable.
    b.eval("window.scrollTo(0,1); void document.body.offsetHeight;")
    time.sleep(0.6)
    b.eval("window.scrollTo(0,0); void document.body.offsetHeight;")
    time.sleep(1.2)
    size = b.shot(path)
    print("    shot %-42s %7d bytes" % (os.path.basename(path), size))
    return path


def walk(label, width, height, mobile, port, log):
    b = Browser(width=width, height=height, mobile=mobile, port=port)
    try:
        b.goto(START, settle=5)
        log.append(("### Viewport: %s (%dx%d)" % (label, width, height), None))

        # ---- STEP 1: Overnatning -------------------------------------------
        inv = json.loads(b.eval(INVENTORY))
        snap(b, "1-overnatning", label)
        log.append(("Step 1 — Overnatning", inv))

        # Validation probe: try to advance with zero rooms selected.
        before = b.eval("location.pathname")
        b.eval(CLICK_BY_TEXT % json.dumps("Videre"))
        time.sleep(2.5)
        after = b.eval("location.pathname")
        blocked = (before == after)
        err = b.eval(
            "JSON.stringify(Array.from(document.querySelectorAll("
            "'[role=alert],[class*=error],[class*=Error],[aria-invalid=true]'))"
            ".map(e=>(e.innerText||'').replace(/\\s+/g,' ').trim()).filter(t=>t).slice(0,5))")
        log.append(("Step 1 validation probe — advance with 0 rooms selected", {
            "blocked": blocked, "path_before": before, "path_after": after,
            "visible_errors": json.loads(err or "[]")}))
        if blocked:
            snap(b, "1-validation", label)

        # Select a room, then advance properly. Try single room first; this
        # departure has only one left and the double-room control is disabled.
        r = b.eval(BUMP_ROOM % json.dumps("Enkeltværelse"))
        if r != "bumped":
            r = "single=%s; double=%s" % (
                r, b.eval(BUMP_ROOM % json.dumps("Dobbeltværelse")))
        print("    room picker:", r)
        time.sleep(2)
        snap(b, "1-room-selected", label)
        b.eval(CLICK_BY_TEXT % json.dumps("Videre"))
        time.sleep(4)

        # ---- STEP 2: Tilvalg -----------------------------------------------
        inv = json.loads(b.eval(INVENTORY))
        snap(b, "2-tilvalg", label)
        log.append(("Step 2 — Tilvalg", inv))
        b.eval(CLICK_BY_TEXT % json.dumps("Videre"))
        time.sleep(4)

        # ---- STEP 3: Personlige oplysninger --------------------------------
        inv = json.loads(b.eval(INVENTORY))
        snap(b, "3-personlige-empty", label)
        log.append(("Step 3 — Personlige oplysninger (empty)", inv))

        # Validation probe on the data-entry step.
        before = b.eval("location.pathname")
        b.eval(CLICK_BY_TEXT % json.dumps("Videre"))
        time.sleep(2.5)
        err = b.eval(
            "JSON.stringify(Array.from(document.querySelectorAll("
            "'[role=alert],[class*=error],[class*=Error],[aria-invalid=true]'))"
            ".map(e=>(e.innerText||'').replace(/\\s+/g,' ').trim()).filter(t=>t).slice(0,8))")
        log.append(("Step 3 validation probe — submit empty", {
            "blocked": before == b.eval("location.pathname"),
            "visible_errors": json.loads(err or "[]")}))
        snap(b, "3-validation", label)

        # Fill with obviously fake data.
        filled = b.eval(r"""
        (function(map){
          var n=0;
          Array.from(document.querySelectorAll('input,textarea')).forEach(function(e){
            if(e.type==='hidden') return;
            var key=((e.name||e.id||e.placeholder||'')+'').toLowerCase();
            if(e.type==='checkbox'){ if(!e.checked){e.click();} n++; return; }
            if(e.type==='radio'){ return; }
            var val=null;
            Object.keys(map).forEach(function(k){ if(!val && key.indexOf(k)>=0) val=map[k]; });
            if(!val && e.type==='email') val=map['email'];
            if(!val && e.type==='tel') val=map['telefon'];
            if(!val) val='Test';
            var d=Object.getOwnPropertyDescriptor(
              Object.getPrototypeOf(e),'value');
            d && d.set ? d.set.call(e,val) : (e.value=val);
            e.dispatchEvent(new Event('input',{bubbles:true}));
            e.dispatchEvent(new Event('change',{bubbles:true}));
            n++;
          });
          return n;
        })(%s);
        """ % json.dumps(DUMMY))
        print("    filled %s fields with dummy data" % filled)
        time.sleep(2)
        snap(b, "3-personlige-filled", label)
        b.eval(CLICK_BY_TEXT % json.dumps("Videre"))
        time.sleep(4.5)

        # ---- STEP 4: Opsummering. HARD STOP. -------------------------------
        inv = json.loads(b.eval(INVENTORY))
        snap(b, "4-opsummering", label)
        log.append(("Step 4 — Opsummering (walk stops here, nothing confirmed)", inv))
        print("    STOPPED at step 4. No payment step entered, no order confirmed.")
    finally:
        b.close()


def main():
    log = []
    print("=== DESKTOP funnel walk ===")
    walk("desktop", 1440, 1400, False, 9361, log)
    print("=== MOBILE funnel walk ===")
    walk("mobile", 390, 1500, True, 9362, log)

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("# Booking funnel walkthrough\n\n")
        f.write("Captured 2026-08-26. Entry: `%s`\n\n" % START)
        f.write("Funnel is 5 steps: **1 Overnatning -> 2 Tilvalg -> "
                "3 Personlige oplysninger -> 4 Opsummering -> 5 Betaling**.\n\n")
        f.write("> The walk deliberately stops at step 4. Advancing to step 5 is what\n"
                "> commits the order, so going further would risk creating a real booking\n"
                "> and holding a real seat. No payment details were ever entered and\n"
                "> nothing was submitted. All personal data used was obviously fake.\n\n")
        for title, data in log:
            if data is None:
                f.write("\n%s\n\n" % title)
                continue
            f.write("**%s**\n\n" % title)
            f.write("```json\n%s\n```\n\n" % json.dumps(data, indent=2,
                                                        ensure_ascii=False))
    print("wrote", REPORT)


if __name__ == "__main__":
    main()
