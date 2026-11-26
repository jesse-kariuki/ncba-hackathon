"""LeakLens API: FastAPI around the existing rules engine (detectors.py) and explainer (explain.py).
Run from the repo root:  uvicorn backend.main:app --reload --port 8000"""
import asyncio, io, json, os, shutil, sqlite3, sys, tempfile, time, zipfile
from datetime import datetime
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)  # explain.py / detectors.py use repo-relative paths

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import detectors, explain

DB = os.path.join(ROOT, "backend", "leaklens.db")
DEMO_DIR = os.path.join(ROOT, "data")

CATEGORIES = {  # brief wording -> detectors
    "duplicates": {"label": "Duplicate subscriptions & payments", "detectors": ["D1_duplicate", "D3_unused_licences"]},
    "overlap": {"label": "Overlapping vendor services", "detectors": ["D2_overlap"]},
    "contracts": {"label": "Contract inefficiencies", "detectors": ["D4_contract"]},
    "anomalies": {"label": "Spending anomalies", "detectors": ["D5_anomaly"]},
    "risk": {"label": "Vendor risk", "detectors": ["D6_vendor_risk"]},
}
DET2CAT = {d: k for k, v in CATEGORIES.items() for d in v["detectors"]}
ROLES = {"ap_officer": "AP officer", "procurement_manager": "Procurement manager", "cfo": "CFO"}

app = FastAPI(title="LeakLens API", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ---------------- storage ----------------
def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with db() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS scans(id INTEGER PRIMARY KEY, created TEXT, source TEXT, n_invoices INT, n_vendors INT,
            n_contracts INT, n_licences INT, total_kes INT, seconds REAL, data_dir TEXT);
        CREATE TABLE IF NOT EXISTS findings(scan_id INT, finding_id TEXT, body TEXT, status TEXT, PRIMARY KEY(scan_id, finding_id));
        CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, ts TEXT, scan_id INT, finding_id TEXT, action TEXT,
            role TEXT, user TEXT, decision TEXT, comment TEXT, kes_impact INT);
        """)


def latest_scan_id():
    with db() as c:
        r = c.execute("SELECT id FROM scans ORDER BY id DESC LIMIT 1").fetchone()
    if not r:
        run_scan(DEMO_DIR, "demo")
        return latest_scan_id()
    return r["id"]


def scan_row(sid):
    with db() as c:
        r = c.execute("SELECT * FROM scans WHERE id=?", (sid,)).fetchone()
    if not r:
        raise HTTPException(404, "scan not found")
    return dict(r)


def load_findings(sid):
    with db() as c:
        rows = c.execute("SELECT body, status FROM findings WHERE scan_id=?", (sid,)).fetchall()
    out = []
    for r in rows:
        f = json.loads(r["body"])
        f["status"] = r["status"]
        f["category"] = DET2CAT.get(f["detector"], "other")
        out.append(f)
    out.sort(key=lambda x: (-x["kes_impact"], x["finding_id"]))
    return out


def count_rows(path):
    try:
        return max(sum(1 for _ in open(path, encoding="utf-8")) - 1, 0)
    except Exception:
        return 0


def run_scan(data_dir, source):
    t0 = time.time()
    try:
        F = detectors.run_all(data_dir, out_path=None)
    except KeyError as e:
        raise HTTPException(400, f"Missing column in uploaded data: {e}. See CONTRACT.md for the expected columns.")
    except FileNotFoundError as e:
        raise HTTPException(400, f"Missing file: {os.path.basename(str(e.filename))}")
    secs = round(time.time() - t0, 2)
    n_con = 0
    if os.path.exists(f"{data_dir}/contracts_extracted.json"):
        n_con = len(json.load(open(f"{data_dir}/contracts_extracted.json")))
    with db() as c:
        cur = c.execute("INSERT INTO scans(created, source, n_invoices, n_vendors, n_contracts, n_licences, total_kes, seconds, data_dir)"
                        " VALUES(?,?,?,?,?,?,?,?,?)",
                        (datetime.now().isoformat(timespec="seconds"), source, count_rows(f"{data_dir}/invoices.csv"),
                         count_rows(f"{data_dir}/vendors.csv"), n_con, count_rows(f"{data_dir}/licences.csv"),
                         int(sum(f["kes_impact"] for f in F)), secs, data_dir))
        sid = cur.lastrowid
        c.executemany("INSERT INTO findings VALUES(?,?,?,?)",
                      [(sid, f["finding_id"], json.dumps(f, default=str), "open") for f in F])
    return sid


# ---------------- API ----------------
@app.on_event("startup")
def _startup():
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True, "ai_providers": explain._providers() or ["template"]}


@app.post("/api/scan")
async def scan(vendors: Optional[UploadFile] = File(None), invoices: Optional[UploadFile] = File(None),
               licences: Optional[UploadFile] = File(None), contracts: Optional[UploadFile] = File(None)):
    """No files -> scan the built-in demo dataset. Otherwise vendors.csv + invoices.csv are required;
    licences.csv and contracts_extracted.json are optional."""
    if not vendors and not invoices:
        sid = run_scan(DEMO_DIR, "demo")
    else:
        if not (vendors and invoices):
            raise HTTPException(400, "Upload at least vendors.csv and invoices.csv")
        d = tempfile.mkdtemp(prefix="leaklens_", dir=os.path.join(ROOT, "backend"))
        for up, name in [(vendors, "vendors.csv"), (invoices, "invoices.csv"), (licences, "licences.csv"),
                         (contracts, "contracts_extracted.json")]:
            if up:
                with open(os.path.join(d, name), "wb") as fh:
                    fh.write(await up.read())
        sid = run_scan(d, "upload")
    return summary(sid)


@app.get("/api/summary")
def summary(scan_id: Optional[int] = None):
    sid = scan_id or latest_scan_id()
    s, F = scan_row(sid), load_findings(sid)
    cats = []
    for k, v in CATEGORIES.items():
        fs = [f for f in F if f["category"] == k]
        cats.append({"key": k, "label": v["label"], "count": len(fs), "kes": sum(f["kes_impact"] for f in fs),
                     "high": sum(1 for f in fs if f["severity"] == "high")})
    approved = [f for f in F if f["status"] == "approved"]
    return {
        "scan": {k: s[k] for k in ("id", "created", "source", "n_invoices", "n_vendors", "n_contracts", "n_licences", "seconds")},
        "total_kes": s["total_kes"], "n_findings": len(F),
        "high_risk_vendors": sum(1 for f in F if f["detector"] == "D6_vendor_risk"),
        "categories": cats,
        "top_actions": [{"finding_id": f["finding_id"], "title": f["title"], "vendor_name": f["vendor_name"],
                         "kes_impact": f["kes_impact"], "suggested_action": f["suggested_action"]}
                        for f in F if f["status"] == "open"][:5],
        "savings": {"found_kes": s["total_kes"], "approved_kes": sum(f["kes_impact"] for f in approved),
                    "approved_count": len(approved),
                    "rejected_count": sum(1 for f in F if f["status"] == "rejected"),
                    "open_count": sum(1 for f in F if f["status"] == "open")},
        "theme": {"reuse": "AP exports, KRA eTIMS, contracts and licence reports you already have",
                  "automate": f"{s['n_invoices']:,} invoices matched and {s['n_contracts']} contracts read in {s['seconds']}s",
                  "reduce": f"KES {s['total_kes']/1e6:.1f}m avoidable spend identified",
                  "eliminate": "Duplicates stopped before payment, redundant tools and missed renewal deadlines"},
    }


@app.get("/api/findings")
def findings(category: Optional[str] = None, status: Optional[str] = None, q: Optional[str] = None):
    F = load_findings(latest_scan_id())
    if category:
        F = [f for f in F if f["category"] == category]
    if status:
        F = [f for f in F if f["status"] == status]
    if q:
        F = [f for f in F if q.lower() in (f["title"] + f["vendor_name"]).lower()]
    return F


def get_finding(fid):
    for f in load_findings(latest_scan_id()):
        if f["finding_id"] == fid:
            return f
    raise HTTPException(404, "finding not found")


@app.get("/api/findings/{fid}")
def finding(fid: str):
    return get_finding(fid)


@app.get("/api/findings/{fid}/explain")
def explain_finding(fid: str):
    f = get_finding(fid)
    x = explain.get_explanation(f)
    return {"finding_id": fid, **x}


@app.get("/api/findings/{fid}/explain/stream")
async def explain_stream(fid: str):
    """Server-sent events: streams the explanation word by word, then the source label."""
    f = get_finding(fid)
    x = explain.get_explanation(f)

    async def gen():
        for w in x["explanation"].split(" "):
            yield f"data: {json.dumps({'token': w + ' '})}\n\n"
            await asyncio.sleep(0.03)
        yield f"data: {json.dumps({'done': True, 'source': x.get('source', 'template'), 'vendor_email': x['vendor_email']})}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")


class Decision(BaseModel):
    role: str
    decision: str  # approved | rejected
    comment: str = ""
    user: str = "demo"


@app.post("/api/findings/{fid}/decision")
def decide(fid: str, d: Decision):
    if d.role != "procurement_manager":
        raise HTTPException(403, "Needs Procurement manager approval. Nothing is paid, held or cancelled automatically.")
    if d.decision not in ("approved", "rejected"):
        raise HTTPException(400, "decision must be approved or rejected")
    f = get_finding(fid)
    if f["status"] != "open":
        raise HTTPException(409, f"Already {f['status']}")
    sid = latest_scan_id()
    with db() as c:
        c.execute("UPDATE findings SET status=? WHERE scan_id=? AND finding_id=?", (d.decision, sid, fid))
        c.execute("INSERT INTO audit(ts, scan_id, finding_id, action, role, user, decision, comment, kes_impact) VALUES(?,?,?,?,?,?,?,?,?)",
                  (datetime.now().isoformat(timespec="seconds"), sid, fid, f["suggested_action"], ROLES[d.role], d.user,
                   d.decision, d.comment, f["kes_impact"]))
    return get_finding(fid)


@app.get("/api/audit")
def audit():
    with db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM audit ORDER BY id DESC").fetchall()]


@app.get("/api/vendors/{vid}")
def vendor(vid: str):
    s = scan_row(latest_scan_id())
    d = s["data_dir"]
    v = pd.read_csv(f"{d}/vendors.csv", dtype=str)
    row = v[v["vendor_id"] == vid]
    if row.empty:
        raise HTTPException(404, "vendor not found")
    inv = pd.read_csv(f"{d}/invoices.csv")
    inv = inv[inv["vendor_id"] == vid]
    monthly = inv.groupby(inv["invoice_date"].str[:7])["amount_kes"].sum()
    contract = None
    if os.path.exists(f"{d}/contracts_extracted.json"):
        contract = next((c for c in json.load(open(f"{d}/contracts_extracted.json")) if c["vendor_id"] == vid), None)
    vend = row.iloc[0].to_dict()
    vend["bank_account"] = "****" + str(vend["bank_account"])[-4:]
    return {"vendor": vend, "annual_spend_kes": int(inv["amount_kes"].sum()), "n_invoices": len(inv),
            "monthly_spend": [{"month": m, "kes": int(k)} for m, k in monthly.items()],
            "contract": contract, "findings": [f for f in load_findings(s["id"]) if f["vendor_id"] == vid]}


@app.get("/api/demo-data.zip")
def demo_zip():
    """Sample files so a judge can try the upload flow."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for n in ("vendors.csv", "invoices.csv", "licences.csv", "contracts_extracted.json"):
            z.write(os.path.join(DEMO_DIR, n), n)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip",
                             headers={"Content-Disposition": "attachment; filename=leaklens-demo-data.zip"})


@app.post("/api/reset")
def reset():
    """Start the demo fresh: clear decisions and the audit log, rescan the demo data."""
    with db() as c:
        c.executescript("DELETE FROM audit; DELETE FROM findings; DELETE FROM scans;")
    for p in os.listdir(os.path.join(ROOT, "backend")):
        if p.startswith("leaklens_"):
            shutil.rmtree(os.path.join(ROOT, "backend", p), ignore_errors=True)
    run_scan(DEMO_DIR, "demo")
    return {"ok": True}
