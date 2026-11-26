"""Explanations + vendor emails. Cache first, then a live LLM, then a template fallback.
Provider: LEAKLENS_PROVIDER=claude|gemini, otherwise whichever key is set (ANTHROPIC_API_KEY or GEMINI_API_KEY/GOOGLE_API_KEY).
The LLM never decides anything: it only rewords what the rules found. Personal data is masked before sending."""
import json, os, re

# Load keys from a local .env file (gitignored). Lines like GEMINI_API_KEY=abc123
if os.path.exists(".env"):
    for line in open(".env", encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            if v.strip().strip('"'):
                os.environ.setdefault(k.strip(), v.strip().strip('"'))

CACHE = "cache/explanations.json"
MODEL = os.environ.get("LEAKLENS_MODEL", "claude-sonnet-5-5")
GEMINI_MODEL = os.environ.get("LEAKLENS_GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

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


def _prompt(f):
    return ("You explain procurement findings to an NCBA Bank procurement manager. The RULES already decided this is a "
              "finding; do not second-guess it and do not invent any numbers or facts not in the JSON.\n"
              "Return JSON with keys 'explanation' (2 plain sentences: why the rules flagged it and the cost or risk) and "
              "'vendor_email' (short, polite, firm email to the vendor citing the evidence, signed 'Procurement, NCBA Bank Kenya').\n\n"
              + _mask(f))


def _parse(t, source):
    d = json.loads(t[t.find("{"): t.rfind("}") + 1])
    return {"explanation": d["explanation"], "vendor_email": d["vendor_email"], "source": source}


def _claude(f):
    import anthropic
    c = anthropic.Anthropic(timeout=10)
    prompt = _prompt(f)
    r = c.messages.create(model=MODEL, max_tokens=600, messages=[{"role": "user", "content": prompt}])
    return _parse(r.content[0].text, "claude")


def _gemini(f):
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    body = {"contents": [{"parts": [{"text": _prompt(f)}]}],
            "generationConfig": {"responseMimeType": "application/json", "maxOutputTokens": 800}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY})
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.load(r)
    return _parse(d["candidates"][0]["content"]["parts"][0]["text"], "gemini")


def _providers():
    pref = os.environ.get("LEAKLENS_PROVIDER", "").lower()
    avail = {"claude": bool(os.environ.get("ANTHROPIC_API_KEY")), "gemini": bool(GEMINI_KEY)}
    order = [pref] + [p for p in ("claude", "gemini") if p != pref] if pref in avail else ["claude", "gemini"]
    return [p for p in order if avail[p]]


_SEEN = {}  # in-process memo so a failing provider isn't retried on every Streamlit rerun


def get_explanation(f):
    if f["finding_id"] in _SEEN:
        return _SEEN[f["finding_id"]]
    cache = _load()
    if f["finding_id"] in cache:
        return cache[f["finding_id"]]
    out = None
    for p in _providers():
        try:
            out = (_claude if p == "claude" else _gemini)(f)
            break
        except Exception:
            out = None
    out = out or _template(f)
    if out["source"] != "template":
        cache[f["finding_id"]] = out
        os.makedirs("cache", exist_ok=True)
        json.dump(cache, open(CACHE, "w"), indent=1)
    _SEEN[f["finding_id"]] = out
    return out


if __name__ == "__main__":  # pre-warm the cache before the demo
    for f in json.load(open("out/findings.json")):
        print(f["finding_id"], get_explanation(f)["source"])
