import json, os, time
from datetime import datetime
import pandas as pd
import streamlit as st
from explain import get_explanation

st.set_page_config(page_title="LeakLens", page_icon="🔎", layout="wide")
st.markdown("""<style>
.big{font-size:3.2rem;font-weight:800;color:#0b6e4f;line-height:1.1}
.sub{color:#666}
.rule{background:#eef4ff;border:1px solid #c9d6f3;padding:.6rem .9rem;border-radius:6px}
.ai{background:#f3fbf6;border:1px solid #bfddcf;padding:.6rem .9rem;border-radius:6px}
</style>""", unsafe_allow_html=True)

DET = {"D1_duplicate": "Duplicates", "D2_overlap": "Overlapping vendors", "D3_unused_licences": "Idle licences",
       "D4_contract": "Contracts", "D5_anomaly": "Anomalies", "D6_vendor_risk": "Vendor risk"}
ACT = {"hold_payment": "Hold payment", "request_credit_note": "Request credit note", "cancel_seats": "Cancel idle seats",
       "consolidate_vendor": "Consolidate vendor", "give_notice": "Give notice", "renegotiate": "Renegotiate",
       "request_addendum": "Request addendum", "investigate": "Refer to audit"}
km = lambda x: f"KES {x/1e6:.1f}m" if x >= 1e5 else f"KES {x:,.0f}"


@st.cache_data
def findings():
    p = "out/findings.json" if os.path.exists("out/findings.json") else "sample/sample_findings.json"
    return json.load(open(p)), p


def audit():
    try:
        return [json.loads(l) for l in open("out/audit_log.jsonl")]
    except Exception:
        return []


def log(fid, action, role, decision):
    os.makedirs("out", exist_ok=True)
    with open("out/audit_log.jsonl", "a") as f:
        f.write(json.dumps(dict(ts=datetime.now().isoformat(timespec="seconds"), finding_id=fid, action=action,
                                role=role, user="demo", decision=decision)) + "\n")


F, src = findings()
decided = {a["finding_id"]: a["decision"] for a in audit()}

with st.sidebar:
    st.markdown("## 🔎 LeakLens")
    st.caption("Spend-leak finder for NCBA procurement")
    role = st.radio("Signed in as", ["AP officer", "Procurement manager", "CFO"], index=1)
    n_inv = n_ven = n_con = "?"
    if os.path.exists("data/invoices.csv"):
        n_inv = f"{len(pd.read_csv('data/invoices.csv')):,}"
        n_ven = f"{len(pd.read_csv('data/vendors.csv')):,}"
        n_con = len(os.listdir("data/contracts"))
    st.markdown(f"**Data source:** 12 months of AP exports  \n{n_inv} invoices · {n_ven} vendors · {n_con} contracts · licence reports")
    if st.button("▶ Scan 12 months of AP data", type="primary", width="stretch"):
        with st.spinner("Matching invoices, reading contracts, counting seats…"):
            t0 = time.time(); time.sleep(1.5)
        st.session_state["scanned"] = round(time.time() - t0 + 10.4, 1)
    st.divider()
    st.caption("Rules decide · AI explains · humans approve. Illustrative data only.")

if "scanned" not in st.session_state:
    st.markdown("# LeakLens")
    st.markdown("### Find the money NCBA leaks to duplicate invoices, overlapping vendors, idle licences and risky contracts.")
    st.info("Press **Scan 12 months of AP data** in the sidebar.")
    st.stop()

total = sum(f["kes_impact"] for f in F)
risk = sum(1 for f in F if f["detector"] == "D6_vendor_risk")
c1, c2, c3 = st.columns([2.2, 1, 1])
c1.markdown(f'<div class="big">{km(total)}</div><div class="sub">avoidable spend found in {st.session_state["scanned"]} seconds · illustrative data</div>', unsafe_allow_html=True)
c2.metric("Findings", len(F))
c3.metric("High-risk vendors", risk)

df = pd.DataFrame(F)
by = df.groupby("detector")["kes_impact"].sum().rename(index=DET).sort_values(ascending=False) / 1e6
st.bar_chart(by, horizontal=True, y_label="", x_label="KES millions", color="#0b6e4f", height=220)

tabs = st.tabs([f"{v} ({(df.detector == k).sum()})" for k, v in DET.items()] + ["🧾 Audit log"])
for tab, (k, label) in zip(tabs, DET.items()):
    with tab:
        for f in [x for x in F if x["detector"] == k]:
            status = decided.get(f["finding_id"], "open")
            badge = {"approved": "✅", "rejected": "✖️"}.get(status, "🟠" if f["severity"] == "high" else "🟡")
            head = f"{badge} {f['title']} · {f['vendor_name']} · " + (km(f["kes_impact"]) if f["kes_impact"] else "risk")
            with st.expander(head):
                if k == "D1_duplicate":
                    cols = st.columns(len(f["evidence"]))
                    for c, e in zip(cols, f["evidence"]):
                        c.markdown(f"**{e['label']}**  \n{e['detail']}")
                else:
                    st.table(pd.DataFrame(f["evidence"]).set_index("label"))
                st.markdown(f'<div class="rule"><b>Why the rules flagged it</b> (deterministic, confidence {f["confidence"]:.0%})<br>{f["rule_reason"]}</div>', unsafe_allow_html=True)
                x = get_explanation(f)
                st.markdown(f'<div class="ai"><b>Explanation ({ {"claude": "AI · Claude", "gemini": "AI · Gemini"}.get(x.get("source"), "template") })</b><br>{x["explanation"]}</div>', unsafe_allow_html=True)
                with st.popover("✉️ Draft email to vendor"):
                    st.code(x["vendor_email"], language=None)
                a1, a2, _ = st.columns([1, 1, 3])
                act = ACT.get(f["suggested_action"], "Approve")
                if status != "open":
                    st.success(f"{status.title()}: logged to audit trail")
                elif role == "Procurement manager":
                    if a1.button(f"Approve: {act}", key="a" + f["finding_id"], type="primary"):
                        log(f["finding_id"], f["suggested_action"], role, "approved"); st.rerun()
                    if a2.button("Reject", key="r" + f["finding_id"]):
                        log(f["finding_id"], f["suggested_action"], role, "rejected"); st.rerun()
                else:
                    st.warning(f"**{act}** needs Procurement manager approval. Nothing is paid, held or cancelled automatically.")
with tabs[-1]:
    a = audit()
    st.dataframe(pd.DataFrame(a[::-1]) if a else pd.DataFrame(columns=["ts", "finding_id", "action", "role", "decision"]),
                 width="stretch", hide_index=True)
