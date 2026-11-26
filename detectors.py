"""LeakLens rules engine. Rules DECIDE; the LLM only explains (see explain.py)."""
import json, os, re
from datetime import date, timedelta
import pandas as pd
from difflib import SequenceMatcher

TODAY = date(2026, 11, 26)
LIMIT = 1_000_000
fmt = lambda x: f"KES {x:,.0f}"


def sev(kes, cust=False):
    return "high" if kes >= 1_000_000 or cust else "medium" if kes >= 200_000 else "low"


def F(det, title, v, kes, conf, evidence, reason, action, cust=False):
    return dict(detector=det, title=title, vendor_id=v["vendor_id"], vendor_name=v["vendor_name"], kes_impact=int(kes),
                confidence=conf, severity=sev(kes, cust), evidence=evidence, rule_reason=reason,
                suggested_action=action, explanation=None, status="open")


def ev(inv):
    return dict(label=inv["invoice_id"], detail=f"eTIMS {inv['etims_number']} · {fmt(inv['amount_kes'])} · paid {inv['paid_date']}")


def load(d):
    inv = pd.read_csv(f"{d}/invoices.csv", parse_dates=["invoice_date", "paid_date"])
    for c in ["invoice_date", "paid_date"]:
        inv[c] = inv[c].dt.date.astype(str)
    lic_cols = ["licence_id", "vendor_id", "product", "seats_paid", "seats_active_90d", "price_per_seat_kes_year", "renewal_date"]
    lic = pd.read_csv(f"{d}/licences.csv") if os.path.exists(f"{d}/licences.csv") else pd.DataFrame(columns=lic_cols)
    con = json.load(open(f"{d}/contracts_extracted.json")) if os.path.exists(f"{d}/contracts_extracted.json") else []
    return dict(vendors=pd.read_csv(f"{d}/vendors.csv", dtype=str), invoices=inv, licences=lic, contracts=con)


def detect_d1(dfs, V):
    out, seen = [], set()
    inv = dfs["invoices"]
    # (a) repeated eTIMS number
    for et, g in inv.groupby("etims_number"):
        if len(g) > 1 and g["amount_kes"].nunique() == 1:
            r = g.sort_values("paid_date").to_dict("records")
            seen.add(frozenset(x["invoice_id"] for x in r))
            out.append(F("D1_duplicate", "Same invoice paid twice", V[r[0]["vendor_id"]], r[0]["amount_kes"] * (len(r) - 1), 0.97,
                         [ev(x) for x in r], "same KRA eTIMS number and amount on two paid invoices", "request_credit_note"))
    # (b) same vendor + amount within 45 days, near-identical invoice ids
    for (vid, amt), g in inv.groupby(["vendor_id", "amount_kes"]):
        r = g.sort_values("invoice_date").to_dict("records")
        for a, b in zip(r, r[1:]):
            if frozenset([a["invoice_id"], b["invoice_id"]]) in seen:
                continue
            days = (date.fromisoformat(b["invoice_date"]) - date.fromisoformat(a["invoice_date"])).days
            sim = 100 * SequenceMatcher(None, re.sub(r"\W", "", a["invoice_id"]), re.sub(r"\W", "", b["invoice_id"])).ratio()
            if days <= 45 and sim >= 95:
                seen.add(frozenset([a["invoice_id"], b["invoice_id"]]))
                out.append(F("D1_duplicate", "Likely duplicate invoice", V[vid], amt, 0.85, [ev(a), ev(b)],
                             f"same vendor and amount {days} days apart; invoice numbers {sim:.0f}% similar", "hold_payment"))
    # (c) two vendor records sharing bank account / KRA PIN, same amount paid to both
    vend = dfs["vendors"]
    for key in ["bank_account"]:
        for _, g in vend.groupby(key):
            if len(g) < 2:
                continue
            ids = list(g["vendor_id"])
            sub = inv[inv["vendor_id"].isin(ids)]
            for amt, ga in sub.groupby("amount_kes"):
                if ga["vendor_id"].nunique() > 1:
                    r = ga.to_dict("records")
                    out.append(F("D1_duplicate", "Paid twice via a duplicate vendor record", V[max(ids)], amt, 0.9,
                                 [ev(x) for x in r] + [dict(label="Shared details", detail=f"{len(ids)} vendor records share bank account and KRA PIN")],
                                 "two vendor records with the same bank account and KRA PIN were each paid the same amount",
                                 "hold_payment"))
    return out


def detect_d2(dfs, V):
    out, inv = [], dfs["invoices"]
    recent = inv[inv["invoice_date"] >= str(TODAY - timedelta(days=90))]
    yr = inv.groupby("vendor_id")["amount_kes"].sum()
    for cat, label in [("video_conferencing", "video-conferencing tools"), ("sms_gateway", "SMS gateways")]:
        ids = [v for v in dfs["vendors"][dfs["vendors"]["category"] == cat]["vendor_id"] if v in set(recent["vendor_id"])]
        if len(ids) >= 2:
            spend = yr[ids].sort_values()
            keep = spend.index[-1] if cat == "video_conferencing" else spend.index[0]
            cut = spend.drop(keep)
            out.append(F("D2_overlap", f"{len(ids)} {label} paid for the same job", V[cut.index[0]], cut.sum(), 0.9,
                         [dict(label=V[i]["vendor_name"], detail=f"{fmt(spend[i])} / yr" + (" (keep)" if i == keep else ""))
                          for i in spend.index],
                         f"{len(ids)} active vendors in category {cat}; consolidate to one", "consolidate_vendor"))
    return out


def detect_d3(dfs, V):
    out = []
    for r in dfs["licences"].to_dict("records"):
        idle = r["seats_paid"] - r["seats_active_90d"]
        if idle / r["seats_paid"] > 0.10:
            kes = idle * r["price_per_seat_kes_year"]
            out.append(F("D3_unused_licences", f"{idle:,} idle {r['product']} seats", V[r["vendor_id"]], kes, 0.95,
                         [dict(label="Seats paid", detail=f"{r['seats_paid']:,}"), dict(label="Active last 90 days", detail=f"{r['seats_active_90d']:,}"),
                          dict(label="Price per seat / year", detail=fmt(r["price_per_seat_kes_year"])), dict(label="Renewal", detail=r["renewal_date"])],
                         f"{idle:,} seats with no sign-in in 90 days × {fmt(r['price_per_seat_kes_year'])}", "cancel_seats"))
    return out


def detect_d4(dfs, V):
    out, inv = [], dfs["invoices"]
    for c in dfs["contracts"]:
        v = V[c["vendor_id"]]
        annual = c["contract_rate_kes"] * 12
        renew = date.fromisoformat(c["renewal_date"])
        deadline = renew - timedelta(days=c["notice_days"])
        if c["auto_renew"] and 0 <= (deadline - TODAY).days <= 30:
            kes = annual * c["annual_escalation_pct"] / 100
            out.append(F("D4_contract", f"Auto-renews in {(renew-TODAY).days} days, notice deadline in {(deadline-TODAY).days}", v, kes, 0.92,
                         [dict(label="Renewal date", detail=c["renewal_date"]), dict(label="Notice period", detail=f"{c['notice_days']} days → give notice by {deadline}"),
                          dict(label="Price increase on renewal", detail=f"{c['annual_escalation_pct']}%")],
                         f"auto-renews; notice deadline {deadline} is within 30 days; {c['annual_escalation_pct']}% increase applies",
                         "give_notice"))
        monthly = inv[inv["vendor_id"] == c["vendor_id"]].groupby(inv["invoice_date"].str[:7])["amount_kes"].sum()
        if len(monthly) and monthly.median() > c["contract_rate_kes"] * 1.12:
            over = (monthly.median() - c["contract_rate_kes"]) * 12
            out.append(F("D4_contract", "Billed above the contract rate", v, over, 0.9,
                         [dict(label="Contract rate", detail=f"{fmt(c['contract_rate_kes'])} / month"),
                          dict(label="Typical month billed", detail=f"{fmt(monthly.median())} / month")],
                         f"typical monthly invoice {monthly.median()/c['contract_rate_kes']-1:.0%} above contract rate", "renegotiate"))
    return out


def detect_d5(dfs, V):
    out, inv = [], dfs["invoices"]
    near = inv[(inv["amount_kes"] >= 0.9 * LIMIT) & (inv["amount_kes"] < LIMIT)]
    for vid, g in near.groupby("vendor_id"):
        r = g.sort_values("invoice_date").to_dict("records")
        if len(r) >= 2 and (date.fromisoformat(r[-1]["invoice_date"]) - date.fromisoformat(r[0]["invoice_date"])).days <= 7:
            out.append(F("D5_anomaly", "Purchase split under the approval limit", V[vid], sum(x["amount_kes"] for x in r), 0.88,
                         [dict(label=x["invoice_id"], detail=f"{fmt(x['amount_kes'])} · {x['invoice_date']}") for x in r],
                         f"{len(r)} invoices within 7 days, each 90–100% of the {fmt(LIMIT)} approval limit", "investigate"))
    m = inv.assign(month=inv["invoice_date"].str[:7]).groupby(["vendor_id", "month"])["amount_kes"].sum().reset_index()
    for vid, g in m.groupby("vendor_id"):
        if len(g) < 6:
            continue
        med = g["amount_kes"].median()
        top = g.loc[g["amount_kes"].idxmax()]
        if top["amount_kes"] > 4 * med and vid not in {o["vendor_id"] for o in out}:
            out.append(F("D5_anomaly", f"Spend spike: {top['amount_kes']/med:.1f}× normal in {top['month']}", V[vid], top["amount_kes"] - med, 0.8,
                         [dict(label=top["month"], detail=fmt(top["amount_kes"])), dict(label="Typical month", detail=fmt(med))],
                         f"month spend {top['amount_kes']/med:.1f}× the vendor's median month", "investigate"))
    return out


def detect_d6(dfs, V):
    out = []
    for c in dfs["contracts"]:
        gaps = [n for k, n in [("has_data_protection_clause", "data-protection"), ("has_exit_clause", "exit"),
                               ("has_audit_rights_clause", "audit-rights")] if not c[k]]
        abroad = c["processes_customer_data"] and c["data_location"] != "KE"
        if gaps or abroad:
            t = "No " + ", ".join(gaps) + " clause" if gaps else "Customer data outside Kenya"
            if gaps and abroad:
                t += f"; customer data stored in {c['data_location']}"
            evd = [dict(label="Missing clauses", detail=", ".join(gaps) or "none")]
            if c["processes_customer_data"]:
                evd.append(dict(label="Customer data location", detail=c["data_location"]))
            out.append(F("D6_vendor_risk", t, V[c["vendor_id"]], 0, 0.93, evd,
                         "contract checked against Data Protection Act 2019 and CBK third-party guidance",
                         "request_addendum", cust=c["processes_customer_data"]))
    return out


def run_all(data_dir="data", out_path="out/findings.json"):
    dfs = load(data_dir)
    V = {r["vendor_id"]: r for r in dfs["vendors"].to_dict("records")}
    f = []
    for d in (detect_d1, detect_d2, detect_d3, detect_d4, detect_d5, detect_d6):
        f += d(dfs, V)
    f.sort(key=lambda x: (-x["kes_impact"], x["detector"]))
    for i, x in enumerate(f, 1):
        x["finding_id"] = f"F-{i:04d}"
    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        json.dump(f, open(out_path, "w"), indent=1, default=str)
    return f


if __name__ == "__main__":
    f = run_all()
    print(f"{len(f)} findings, KES {sum(x['kes_impact'] for x in f)/1e6:.1f}m")
    for x in f:
        print(f"{x["finding_id"]} {x['detector']:<20} {x['kes_impact']:>12,} {x['title']}")
