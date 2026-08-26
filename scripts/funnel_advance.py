#!/usr/bin/env python3
"""
Reach step 4 (Opsummering) properly and stop there.

The first walk filled every text input but ignored the <select> elements, the
radio groups and the terms checkbox, so step 3 validation rejected it and the walk
never advanced. This fills the step the way a real customer would: valid Danish
date format, gender and country selected, a payment option chosen, terms accepted.

Still stops dead at step 4. Advancing from 4 to 5 (Betaling) is what commits the
order, so it is never clicked.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import Browser  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "assets", "shots")
START = "https://smilrejser.dk/booking/travel/49000/6095/accommodation"

BUMP = r"""
(function(want){
  var row = Array.from(document.querySelectorAll('li')).find(function(r){
    return r.textContent.indexOf(want)>=0 && r.querySelectorAll('button').length===2;});
  if(!row) return 'NOROW';
  var b=row.querySelectorAll('button')[1];
  if(b.disabled) return 'DISABLED';
  b.click(); return 'ok';
})(%s);
"""

CLICK = r"""
(function(label){
  var el = Array.from(document.querySelectorAll('button,a,[role=button]')).find(function(e){
    return (e.innerText||'').replace(/\s+/g,' ').trim().toLowerCase()===label.toLowerCase();});
  if(!el) return 'NOTFOUND';
  if(el.disabled) return 'DISABLED';
  el.scrollIntoView({block:'center'}); el.click(); return 'ok';
})(%s);
"""

FILL = r"""
(function(){
  var setVal = function(el, v){
    var d = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(el),'value');
    d && d.set ? d.set.call(el, v) : (el.value = v);
    el.dispatchEvent(new Event('input',{bubbles:true}));
    el.dispatchEvent(new Event('change',{bubbles:true}));
  };
  var log = {text:0, selects:0, radios:0, checks:0};

  // Text inputs, keyed off their visible label.
  // Select all inputs and filter on the .type PROPERTY, not an [type=text]
  // attribute selector: React omits the attribute, so the CSS selector matched
  // only the 3 fields that happened to declare it explicitly.
  Array.from(document.querySelectorAll('input,textarea'))
   .filter(function(e){ return ['text','email','tel','','search'].indexOf(e.type)>=0
                            || e.tagName==='TEXTAREA'; })
   .forEach(function(e){
    var lab='';
    if(e.id){var l=document.querySelector('label[for="'+e.id+'"]'); if(l) lab=l.innerText;}
    lab = (lab || e.placeholder || e.name || '').toLowerCase();
    var v = 'Test';
    if(/f\u00f8dselsdato|birthday/.test(lab))      v = '24-12-1975';
    else if(/for- og mellem|firstname/.test(lab))  v = 'Testfornavn';
    else if(/efternavn|lastname/.test(lab))        v = 'Testefternavn';
    else if(/email/.test(lab))                     v = 'audit-test@example.invalid';
    else if(/telefon/.test(lab))                   v = '20000000';
    else if(/adresse/.test(lab))                   v = 'Testvej 1';
    else if(/postnummer/.test(lab))                v = '2100';
    else if(/^by| by /.test(lab))                  v = 'K\u00f8benhavn';
    else if(/rabatkode/.test(lab))                 return;   // leave discount blank
    else if(/kost|n\u00f8dstilf|kommentar|\u00f8nsker/.test(lab)) return; // optional
    setVal(e, v); log.text++;
  });

  // Selects: pick the first real option.
  Array.from(document.querySelectorAll('select')).forEach(function(s){
    var opt = Array.from(s.options).find(function(o){ return o.value && !o.disabled; });
    if(opt){ setVal(s, opt.value); log.selects++; }
  });

  // Radio groups: choose the first option in each group.
  var groups = {};
  Array.from(document.querySelectorAll('input[type=radio]')).forEach(function(r){
    var k = r.name || 'anon';
    if(groups[k]) return;
    groups[k] = true; r.click(); log.radios++;
  });

  // Terms must be accepted; leave the marketing opt-in alone.
  Array.from(document.querySelectorAll('input[type=checkbox]')).forEach(function(c){
    if((c.name||'').toLowerCase().indexOf('marketing')>=0) return;
    if(!c.checked){ c.click(); log.checks++; }
  });
  return JSON.stringify(log);
})();
"""

INV = r"""
(function(){
  var body=document.body.innerText.replace(/\s+/g,' ');
  return JSON.stringify({
    path:location.pathname, title:document.title, h1:(document.querySelector('h1')||{}).innerText||'',
    total:(body.match(/Samlet pris\s*([\d.]+\s*DKK)/)||[])[1]||'',
    has_phone:!!document.querySelector('a[href^="tel:"]'),
    has_terms:/betingelser|afbestilling|fortrydelse/i.test(body),
    chars:body.length, excerpt:body.slice(0,700)
  });
})();
"""


def snap(b, name, label):
    p = os.path.join(SHOTS, "funnel-%s-%s.png" % (name, label))
    b.eval("window.scrollTo(0,1);void document.body.offsetHeight;")
    time.sleep(0.6)
    b.eval("window.scrollTo(0,0);void document.body.offsetHeight;")
    time.sleep(1.2)
    print("    shot %-40s %7d bytes" % (os.path.basename(p), b.shot(p)))


def wait_for(b, expr, want, timeout=30, label=""):
    """Poll until a JS expression reaches the wanted value.

    Fixed sleeps are not enough here: this is a hydrating React funnel and the
    step-3 form arrives in pieces. An earlier run filled only 3 of ~20 fields
    because it typed before the form existed.
    """
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = b.eval(expr)
        if isinstance(want, int) and isinstance(last, (int, float)) and last >= want:
            return last
        if last == want:
            return last
        time.sleep(0.8)
    print("    WARN wait_for(%s) gave up at %r (wanted %r)" % (label, last, want))
    return last


def advance(b, step_name, expect_path):
    """Click Videre and wait for the URL to actually change."""
    b.eval(CLICK % json.dumps("Videre"))
    deadline = time.time() + 25
    while time.time() < deadline:
        if expect_path in (b.eval("location.pathname") or ""):
            time.sleep(2.5)
            return True
        time.sleep(0.8)
    print("    WARN did not reach %s (%s)" % (step_name, expect_path))
    return False


def run(label, w, h, mobile, port):
    b = Browser(width=w, height=h, mobile=mobile, port=port)
    out = {}
    try:
        b.goto(START, settle=5)
        wait_for(b, "document.querySelectorAll('li').length", 4, label="step1 rooms")
        print("    room:", b.eval(BUMP % json.dumps("Enkeltværelse")))
        time.sleep(2)
        advance(b, "step 2 Tilvalg", "/addons")
        advance(b, "step 3 Personlige", "/personal-information")
        # Wait for the form itself, not just the route.
        wait_for(b, "document.querySelectorAll('input,select').length", 20,
                 label="step3 form")
        time.sleep(1.5)
        print("    step3 fill:", b.eval(FILL))
        time.sleep(2.5)
        snap(b, "3-filled-valid", label)
        b.eval(CLICK % json.dumps("Videre"))
        time.sleep(5)

        inv = json.loads(b.eval(INV))
        out = inv
        print("    now at:", inv["path"], "| h1:", repr(inv["h1"]),
              "| title:", repr(inv["title"]))
        if inv["path"].endswith("summary") or "psummering" in inv["h1"]:
            snap(b, "4-opsummering", label)
            print("    reached step 4. STOPPING. Nothing confirmed.")
        else:
            snap(b, "3-still-blocked", label)
            errs = b.eval(
                "JSON.stringify(Array.from(document.querySelectorAll("
                "'[role=alert],[class*=error],[class*=Error]')).map(e=>"
                "(e.innerText||'').replace(/\\s+/g,' ').trim()).filter(t=>t).slice(0,8))")
            out["errors"] = json.loads(errs or "[]")
            print("    still on step 3. errors:", out["errors"])
    finally:
        b.close()
    return out


if __name__ == "__main__":
    res = {}
    print("=== DESKTOP ===")
    res["desktop"] = run("desktop", 1440, 1400, False, 9391)
    print("=== MOBILE ===")
    res["mobile"] = run("mobile", 390, 1500, True, 9392)
    with open(os.path.join(ROOT, "evidence", "funnel_final_state.json"), "w",
              encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print("wrote evidence/funnel_final_state.json")
