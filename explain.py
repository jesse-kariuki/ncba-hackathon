"""Explanations + vendor emails. Cache first, live Claude only if ANTHROPIC_API_KEY is set, template fallback.
The LLM never decides anything: it only rewords what the rules found. Personal data is masked before sending."""
import json, os, re

CACHE = "cache/explanations.json"
MODEL = os.environ.get("LEAKLENS_MODEL", "claude-sonnet-5-5")

ACTION_TXT = {"hold_payment": "hold any further payment until this is resolved", "request_credit_note": "request a credit note",
              "cancel_seats": "cancel the idle seats at renewal", "consolidate_vendor": "consolidate onto one vendor",
              "give_notice": "give written notice before the deadline and renegotiate", "renegotiate": "renegotiate back to the contract rate",
              "request_addendum": "request a data-protection / audit addendum", "investigate": "refer to internal audit to investigate"}


def _load():
    try:
        return json.load(open(CACHE))
    except Exception:
        return {}


def _mask(f):
    s = json.dumps({k: f[k] for k in ("detector", "title", "vendor_name", "kes_impact", "evidence", "rule_reason", "suggested_action")})
    s = re.sub(r"\b\d{9,}\b", lambda m: "****" + m.group()[-4:], s)       # bank accounts
    s = re.sub(r"\bP05\d{7}[A-Z]\b", "P05*******", s)                       # KRA PINs
    s = re.sub(r"Officer [A-Z]", "an approver", s)                          # staff names
    return s


def _template(f):
    kes = f"KES {f['kes_impact']:,.0f}"
    why = f"The rules flagged this because: {f['rule_reason']}."
    impact = f" Estimated avoidable spend: {kes}." if f["kes_impact"] else " This is a compliance risk rather than a cost."
    exp = f"{why}{impact} Recommended next step: {ACTION_TXT.get(f['suggested_action'], 'review')}."
    ev = "\n".join(f"  - {e['label']}: {e['detail']}" for e in f["evidence"])
    email = (f"Subject: {f['title']} - request for review\n\nDear {f['vendor_name']} team,\n\n"
             f"During a routine review of our accounts we identified the following:\n{ev}\n\n"
             f"We would be grateful if you could {ACTION_TXT.get(f['suggested_action'], 'review this')} "
             f"and confirm within 5 working days.\n\nKind regards,\nProcurement, NCBA Bank Kenya")
    return {"explanation": exp, "vendor_email": email, "source": "template"}


def _live(f):
    import anthropic
    c = anthropic.Anthropic(timeout=10)
    prompt = ("You explain procurement findings to an NCBA Bank procurement manager. The RULES already decided this is a "
              "finding; do not second-guess it and do not invent any numbers or facts not in the JSON.\n"
              "Return JSON with keys 'explanation' (2 plain sentences: why the rules flagged it and the cost or risk) and "
              "'vendor_email' (short, polite, firm email to the vendor citing the evidence, signed 'Procurement, NCBA Bank Kenya').\n\n"
              + _mask(f))
    r = c.messages.create(model=MODEL, max_tokens=600, messages=[{"role": "user", "content": prompt}])
    t = r.content[0].text
    d = json.loads(t[t.find("{"): t.rfind("}") + 1])
    return {"explanation": d["explanation"], "vendor_email": d["vendor_email"], "source": "claude"}


def get_explanation(f):
    cache = _load()
    if f["finding_id"] in cache:
        return cache[f["finding_id"]]
    out = None
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            out = _live(f)
        except Exception:
            out = None
    out = out or _template(f)
    if out["source"] == "claude":
        cache[f["finding_id"]] = out
        os.makedirs("cache", exist_ok=True)
        json.dump(cache, open(CACHE, "w"), indent=1)
    return out


if __name__ == "__main__":  # pre-warm the cache before the demo
    for f in json.load(open("out/findings.json")):
        print(f["finding_id"], get_explanation(f)["source"])
