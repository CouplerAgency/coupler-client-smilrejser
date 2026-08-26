# Booking funnel walkthrough

Captured 2026-08-26. Entry: `https://smilrejser.dk/booking/travel/49000/6095/accommodation`

Funnel is 5 steps: **1 Overnatning -> 2 Tilvalg -> 3 Personlige oplysninger -> 4 Opsummering -> 5 Betaling**.

> The walk deliberately stops at step 4. Advancing to step 5 is what
> commits the order, so going further would risk creating a real booking
> and holding a real seat. No payment details were ever entered and
> nothing was submitted. All personal data used was obviously fake.


### Viewport: desktop (1440x1400)

**Step 1 — Overnatning**

```json
{
  "url": "/booking/travel/49000/6095/accommodation",
  "step": "1 Overnatning",
  "fields": [],
  "buttons": [
    {
      "t": "Annuller booking",
      "disabled": false
    },
    {
      "t": "Inkluderet i prisen",
      "disabled": false
    },
    {
      "t": "Videre",
      "disabled": false
    },
    {
      "t": "Tilbage",
      "disabled": false
    },
    {
      "t": "Annuller",
      "disabled": false
    }
  ],
  "price_visible": true,
  "total": "10.090 DKK",
  "has_terms": false,
  "has_phone": false,
  "has_progress": true,
  "heading": "Overnatning",
  "chars": 621
}
```

**Step 1 validation probe — advance with 0 rooms selected**

```json
{
  "blocked": true,
  "path_before": "/booking/travel/49000/6095/accommodation",
  "path_after": "/booking/travel/49000/6095/accommodation",
  "visible_errors": [
    "Nu kan du glæde dig Din rejse er næsten booket! Når bestillingen er gennemført, sender vi en bekræftelse til din mail.",
    "Der opstod en fejl Antallet af værelser og personer matcher ikke. Ret venligst til korrekt antal for at komme videre med din booking."
  ]
}
```

**Step 2 — Tilvalg**

```json
{
  "url": "/booking/travel/49000/6095/addons",
  "step": "2 Tilvalg",
  "fields": [],
  "buttons": [
    {
      "t": "Annuller booking",
      "disabled": false
    },
    {
      "t": "Overnatning",
      "disabled": false
    },
    {
      "t": "Læs mere",
      "disabled": false
    },
    {
      "t": "Vælg antal personer",
      "disabled": false
    },
    {
      "t": "Læs mere",
      "disabled": false
    },
    {
      "t": "Vælg antal personer",
      "disabled": false
    },
    {
      "t": "Læs mere",
      "disabled": false
    },
    {
      "t": "Vælg antal personer",
      "disabled": false
    },
    {
      "t": "Inkluderet i prisen",
      "disabled": false
    },
    {
      "t": "Videre",
      "disabled": false
    },
    {
      "t": "Tilbage",
      "disabled": false
    },
    {
      "t": "Annuller",
      "disabled": false
    }
  ],
  "price_visible": true,
  "total": "11.085 DKK",
  "has_terms": false,
  "has_phone": false,
  "has_progress": false,
  "heading": "Tilvalg",
  "chars": 767
}
```

**Step 3 — Personlige oplysninger (empty)**

```json
{
  "url": "/booking/travel/49000/6095/personal-information",
  "step": "3 Personlige",
  "fields": [
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.firstName",
      "label": "For- og mellemnavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.lastName",
      "label": "Efternavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.birthday",
      "label": "Fødselsdato - fx. 24-12-1975 *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.email",
      "label": "Email",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.dietaryRequests",
      "label": "Særlige ønsker til kost",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.emergencyContact",
      "label": "Kontaktperson i nødstilfælde",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.comment",
      "label": "Kommentar",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.firstName",
      "label": "For- og mellemnavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.lastName",
      "label": "Efternavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Adresse *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Postnummer *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "By *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.telephone",
      "label": "Telefonnummer *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.email",
      "label": "Email *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "previousTravelWithUs",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "previousTravelWithUs",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.specialRequests",
      "label": "Har du særlige ønsker?",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "checkbox",
      "name": "consentToTerms",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "checkbox",
      "name": "consentToMarketing",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Din rabatkode",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    }
  ],
  "buttons": [
    {
      "t": "Annuller booking",
      "disabled": false
    },
    {
      "t": "Overnatning",
      "disabled": false
    },
    {
      "t": "Tilvalg",
      "disabled": false
    },
    {
      "t": "Køn *",
      "disabled": false
    },
    {
      "t": "Danmark",
      "disabled": false
    },
    {
      "t": "Hvor har du hørt om denne rejse?",
      "disabled": false
    },
    {
      "t": "Anvend",
      "disabled": false
    },
    {
      "t": "Inkluderet i prisen",
      "disabled": false
    },
    {
      "t": "Videre",
      "disabled": false
    },
    {
      "t": "Tilbage",
      "disabled": false
    },
    {
      "t": "Annuller",
      "disabled": false
    }
  ],
  "price_visible": true,
  "total": "11.085 DKK",
  "has_terms": true,
  "has_phone": false,
  "has_progress": false,
  "heading": "Personlige oplysninger",
  "chars": 4442
}
```

**Step 3 validation probe — submit empty**

```json
{
  "blocked": true,
  "visible_errors": [
    "Required",
    "Required",
    "Required"
  ]
}
```

**Final state reached — still step 3 (walk stops here, nothing confirmed)**

> Labelled "step 4" in an earlier draft. It is not. The payload below shows
> `"step": "3 Personlige"` and the URL still on `/personal-information`. Two required
> fields would not accept scripted input — the `Køn` (gender) select and `Fødselsdato`
> (date of birth) — so the walk never advanced to Opsummering. Steps 4 and 5 are
> therefore **not assessed**, and the deck says so.

```json
{
  "url": "/booking/travel/49000/6095/personal-information",
  "step": "3 Personlige",
  "fields": [
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.firstName",
      "label": "For- og mellemnavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.lastName",
      "label": "Efternavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.birthday",
      "label": "Fødselsdato - fx. 24-12-1975 *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.email",
      "label": "Email",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.dietaryRequests",
      "label": "Særlige ønsker til kost",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.emergencyContact",
      "label": "Kontaktperson i nødstilfælde",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.comment",
      "label": "Kommentar",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.firstName",
      "label": "For- og mellemnavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.lastName",
      "label": "Efternavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Adresse *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Postnummer *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "By *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.telephone",
      "label": "Telefonnummer *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.email",
      "label": "Email *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "previousTravelWithUs",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "previousTravelWithUs",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.specialRequests",
      "label": "Har du særlige ønsker?",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "checkbox",
      "name": "consentToTerms",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "checkbox",
      "name": "consentToMarketing",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Din rabatkode",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    }
  ],
  "buttons": [
    {
      "t": "Annuller booking",
      "disabled": false
    },
    {
      "t": "Overnatning",
      "disabled": false
    },
    {
      "t": "Tilvalg",
      "disabled": false
    },
    {
      "t": "Køn *",
      "disabled": false
    },
    {
      "t": "Danmark",
      "disabled": false
    },
    {
      "t": "Hvor har du hørt om denne rejse?",
      "disabled": false
    },
    {
      "t": "Anvend",
      "disabled": false
    },
    {
      "t": "Inkluderet i prisen",
      "disabled": false
    },
    {
      "t": "Videre",
      "disabled": false
    },
    {
      "t": "Tilbage",
      "disabled": false
    },
    {
      "t": "Annuller",
      "disabled": false
    }
  ],
  "price_visible": true,
  "total": "11.085 DKK",
  "has_terms": true,
  "has_phone": false,
  "has_progress": false,
  "heading": "Personlige oplysninger",
  "chars": 4574
}
```


### Viewport: mobile (390x1500)

**Step 1 — Overnatning**

```json
{
  "url": "/booking/travel/49000/6095/accommodation",
  "step": "1 Overnatning",
  "fields": [],
  "buttons": [
    {
      "t": "Annuller booking",
      "disabled": false
    },
    {
      "t": "Opsummering",
      "disabled": false
    },
    {
      "t": "Videre",
      "disabled": false
    },
    {
      "t": "Tilbage",
      "disabled": false
    },
    {
      "t": "Annuller",
      "disabled": false
    }
  ],
  "price_visible": false,
  "total": "",
  "has_terms": false,
  "has_phone": false,
  "has_progress": true,
  "heading": "Overnatning",
  "chars": 326
}
```

**Step 1 validation probe — advance with 0 rooms selected**

```json
{
  "blocked": true,
  "path_before": "/booking/travel/49000/6095/accommodation",
  "path_after": "/booking/travel/49000/6095/accommodation",
  "visible_errors": [
    "Nu kan du glæde dig Din rejse er næsten booket! Når bestillingen er gennemført, sender vi en bekræftelse til din mail.",
    "Der opstod en fejl Antallet af værelser og personer matcher ikke. Ret venligst til korrekt antal for at komme videre med din booking."
  ]
}
```

**Step 2 — Tilvalg**

```json
{
  "url": "/booking/travel/49000/6095/addons",
  "step": "2 Tilvalg",
  "fields": [],
  "buttons": [
    {
      "t": "Annuller booking",
      "disabled": false
    },
    {
      "t": "Læs mere",
      "disabled": false
    },
    {
      "t": "Vælg antal personer",
      "disabled": false
    },
    {
      "t": "Læs mere",
      "disabled": false
    },
    {
      "t": "Vælg antal personer",
      "disabled": false
    },
    {
      "t": "Læs mere",
      "disabled": false
    },
    {
      "t": "Vælg antal personer",
      "disabled": false
    },
    {
      "t": "Opsummering",
      "disabled": false
    },
    {
      "t": "Videre",
      "disabled": false
    },
    {
      "t": "Tilbage",
      "disabled": false
    },
    {
      "t": "Annuller",
      "disabled": false
    }
  ],
  "price_visible": false,
  "total": "",
  "has_terms": false,
  "has_phone": false,
  "has_progress": false,
  "heading": "Tilvalg",
  "chars": 395
}
```

**Step 3 — Personlige oplysninger (empty)**

```json
{
  "url": "/booking/travel/49000/6095/personal-information",
  "step": "3 Personlige",
  "fields": [
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.firstName",
      "label": "For- og mellemnavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.lastName",
      "label": "Efternavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.birthday",
      "label": "Fødselsdato - fx. 24-12-1975 *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.email",
      "label": "Email",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.dietaryRequests",
      "label": "Særlige ønsker til kost",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.emergencyContact",
      "label": "Kontaktperson i nødstilfælde",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.comment",
      "label": "Kommentar",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.firstName",
      "label": "For- og mellemnavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.lastName",
      "label": "Efternavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Adresse *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Postnummer *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "By *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.telephone",
      "label": "Telefonnummer *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.email",
      "label": "Email *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "previousTravelWithUs",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "previousTravelWithUs",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.specialRequests",
      "label": "Har du særlige ønsker?",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "checkbox",
      "name": "consentToTerms",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "checkbox",
      "name": "consentToMarketing",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Din rabatkode",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    }
  ],
  "buttons": [
    {
      "t": "Annuller booking",
      "disabled": false
    },
    {
      "t": "Køn *",
      "disabled": false
    },
    {
      "t": "Danmark",
      "disabled": false
    },
    {
      "t": "Hvor har du hørt om denne rejse?",
      "disabled": false
    },
    {
      "t": "Anvend",
      "disabled": false
    },
    {
      "t": "Opsummering",
      "disabled": false
    },
    {
      "t": "Videre",
      "disabled": false
    },
    {
      "t": "Tilbage",
      "disabled": false
    },
    {
      "t": "Annuller",
      "disabled": false
    }
  ],
  "price_visible": true,
  "total": "",
  "has_terms": true,
  "has_phone": false,
  "has_progress": false,
  "heading": "Personlige oplysninger",
  "chars": 3826
}
```

**Step 3 validation probe — submit empty**

```json
{
  "blocked": true,
  "visible_errors": [
    "Required",
    "Required",
    "Required"
  ]
}
```

**Final state reached — still step 3 (walk stops here, nothing confirmed)**

> Labelled "step 4" in an earlier draft. It is not. The payload below shows
> `"step": "3 Personlige"` and the URL still on `/personal-information`. Two required
> fields would not accept scripted input — the `Køn` (gender) select and `Fødselsdato`
> (date of birth) — so the walk never advanced to Opsummering. Steps 4 and 5 are
> therefore **not assessed**, and the deck says so.

```json
{
  "url": "/booking/travel/49000/6095/personal-information",
  "step": "3 Personlige",
  "fields": [
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.firstName",
      "label": "For- og mellemnavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.lastName",
      "label": "Efternavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.birthday",
      "label": "Fødselsdato - fx. 24-12-1975 *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.email",
      "label": "Email",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.dietaryRequests",
      "label": "Særlige ønsker til kost",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.emergencyContact",
      "label": "Kontaktperson i nødstilfælde",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "travelers.0.comment",
      "label": "Kommentar",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.firstName",
      "label": "For- og mellemnavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.lastName",
      "label": "Efternavn *",
      "required": false,
      "aria": false
    },
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Adresse *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Postnummer *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "By *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.telephone",
      "label": "Telefonnummer *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.email",
      "label": "Email *",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "previousTravelWithUs",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "previousTravelWithUs",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "select",
      "type": "select-one",
      "name": "",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "booker.specialRequests",
      "label": "Har du særlige ønsker?",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "checkbox",
      "name": "consentToTerms",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "checkbox",
      "name": "consentToMarketing",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "text",
      "name": "input",
      "label": "Din rabatkode",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    },
    {
      "tag": "input",
      "type": "radio",
      "name": "paymentOption",
      "label": "",
      "required": false,
      "aria": false
    }
  ],
  "buttons": [
    {
      "t": "Annuller booking",
      "disabled": false
    },
    {
      "t": "Køn *",
      "disabled": false
    },
    {
      "t": "Danmark",
      "disabled": false
    },
    {
      "t": "Hvor har du hørt om denne rejse?",
      "disabled": false
    },
    {
      "t": "Anvend",
      "disabled": false
    },
    {
      "t": "Opsummering",
      "disabled": false
    },
    {
      "t": "Videre",
      "disabled": false
    },
    {
      "t": "Tilbage",
      "disabled": false
    },
    {
      "t": "Annuller",
      "disabled": false
    }
  ],
  "price_visible": true,
  "total": "",
  "has_terms": true,
  "has_phone": false,
  "has_progress": false,
  "heading": "Personlige oplysninger",
  "chars": 3862
}
```

