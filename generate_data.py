"""Generate fake NCBA procurement data with planted leaks (see CONTRACT.md)."""
import csv, json, os, random
from datetime import date, timedelta

random.seed(42)
D = "data"
os.makedirs(f"{D}/contracts", exist_ok=True)

PLACES = ["Kilimani", "Westlands", "Karen", "Upperhill", "Gigiri", "Lavington", "Kileleshwa", "Parklands",
          "Embakasi", "Thika", "Nakuru", "Mombasa", "Kisumu", "Eldoret", "Nyeri", "Machakos", "Rift Valley",
          "Savannah", "Lakeview", "Highlands", "Coastline", "Mlimani", "Jamhuri", "Uhuru", "Amani"]
KIND = {"office_supplies": "Office Supplies", "cloud_hosting": "Cloud Services", "software_licence": "Software",
        "security": "Security Services", "consulting": "Consulting", "facilities": "Facilities Management",
        "telecom": "Telecoms", "marketing": "Marketing Agency"}
MONTHS = [date(2025, 12, 1) + timedelta(days=31 * i) for i in range(12)]
MONTHS = [m.replace(day=1) for m in MONTHS]
LIMIT = 1_000_000

vendors, invoices, leaks, contracts = [], [], [], []
etims_n = [100000]


def etims():
    etims_n[0] += random.randint(1, 9)
    return f"KRAMW004202600{etims_n[0]}"


def kra():
    return f"P05{random.randint(1000000, 9999999)}{random.choice('ABCDEFGHJK')}"


def bank():
    return f"{random.choice(['0110', '0200', '0711', '1234'])}{random.randint(10**8, 10**9 - 1)}"


def add_vendor(vid, name, cat, country="KE"):
    v = dict(vendor_id=vid, vendor_name=name, category=cat, kra_pin=kra(), bank_account=bank(),
             country=country, onboarded_date=str(date(2022, 1, 1) + timedelta(days=random.randint(0, 900))))
    vendors.append(v)
    return v


def safe_amount(a):
    a = int(round(a, -1))
    return 870_000 + random.randint(0, 9000) * 1 if 880_000 <= a <= LIMIT else a  # keep normal data away from the split-purchase band


inv_counter = [0]


def add_invoice(vid, amount, d, desc, inv_id=None, et=None, paid_lag=None):
    inv_counter[0] += 1
    inv = dict(invoice_id=inv_id or f"INV-{vid}-{inv_counter[0]:05d}", etims_number=et or etims(), vendor_id=vid,
               amount_kes=int(amount), invoice_date=str(d), paid_date=str(d + timedelta(days=paid_lag or random.randint(7, 25))),
               description=desc, cost_centre=random.choice(["IT", "OPS", "HR", "FIN", "RETAIL", "TREASURY"]),
               approver=random.choice(["Officer A", "Officer B", "Officer C", "Officer D"]))
    invoices.append(inv)
    return inv


# ---------- normal vendors: one invoice a month, +-10% around a base ----------
base = {}
names_used = set()
for i in range(1, 241):
    vid = f"V{i:03d}"
    cat = random.choice(list(KIND))
    while True:
        name = f"{random.choice(PLACES)} {KIND[cat]} Ltd"
        if name not in names_used:
            break
        name = f"{random.choice(PLACES)} {random.choice(PLACES)} {KIND[cat]} Ltd"
        if name not in names_used:
            break
    names_used.add(name)
    add_vendor(vid, name, cat)
    base[vid] = random.choice([random.randint(40_000, 400_000), random.randint(400_000, 2_500_000)])
    for m in MONTHS:
        add_invoice(vid, safe_amount(base[vid] * random.uniform(0.9, 1.1)), m + timedelta(days=random.randint(0, 20)),
                    f"{KIND[cat]} - monthly")

# ---------- D2: overlapping vendors ----------
video = [("V301", "Zoom Video Communications (KE reseller)", 260_000), ("V302", "Webex by Cisco - Amani Tech Ltd", 255_000),
         ("V303", "Teams Rooms - Rift Valley Cloud Ltd", 370_000)]
sms = [("V304", "Savannah SMS Gateway Ltd", 150_000), ("V305", "Jamhuri Bulk SMS Ltd", 140_000)]
for vid, name, b in video:
    add_vendor(vid, name, "video_conferencing")
    for m in MONTHS:
        add_invoice(vid, b, m + timedelta(days=3), "Video conferencing subscription")
for vid, name, b in sms:
    add_vendor(vid, name, "sms_gateway")
    for m in MONTHS:
        add_invoice(vid, b, m + timedelta(days=5), "Bulk SMS bundle")
leaks.append(dict(leak_id="L10", detector="D2_overlap", vendor_id="V301", kes_impact=(260_000 + 255_000) * 12))
leaks.append(dict(leak_id="L11", detector="D2_overlap", vendor_id="V305", kes_impact=150_000 * 12))

# ---------- D1: duplicates ----------
normal_invs = [x for x in invoices if x["vendor_id"] < "V241"]
picks = random.sample(normal_invs, 9)
for k, orig in enumerate(picks[:3]):  # (a) same eTIMS, reformatted invoice id
    d = date.fromisoformat(orig["invoice_date"])
    dup = add_invoice(orig["vendor_id"], orig["amount_kes"], d + timedelta(days=12), orig["description"],
                      inv_id=orig["invoice_id"].replace("-", ""), et=orig["etims_number"])
    leaks.append(dict(leak_id=f"L0{k+1}", detector="D1_duplicate", vendor_id=orig["vendor_id"],
                      invoice_ids=[orig["invoice_id"], dup["invoice_id"]], kes_impact=orig["amount_kes"]))
for k, orig in enumerate(picks[3:6]):  # (b) same vendor+amount within 45 days, near-identical id, new eTIMS
    d = date.fromisoformat(orig["invoice_date"])
    dup = add_invoice(orig["vendor_id"], orig["amount_kes"], d + timedelta(days=20), orig["description"],
                      inv_id=orig["invoice_id"] + "A")
    leaks.append(dict(leak_id=f"L0{k+4}", detector="D1_duplicate", vendor_id=orig["vendor_id"],
                      invoice_ids=[orig["invoice_id"], dup["invoice_id"]], kes_impact=orig["amount_kes"]))
for k, orig in enumerate(picks[6:9]):  # (c) shadow vendor record sharing bank account + KRA PIN
    real = next(v for v in vendors if v["vendor_id"] == orig["vendor_id"])
    sid = f"V9{k+1:02d}"
    shadow = add_vendor(sid, real["vendor_name"].replace(" Ltd", " Limited"), real["category"])
    shadow["bank_account"], shadow["kra_pin"] = real["bank_account"], real["kra_pin"]
    d = date.fromisoformat(orig["invoice_date"])
    dup = add_invoice(sid, orig["amount_kes"], d + timedelta(days=9), orig["description"])
    leaks.append(dict(leak_id=f"L0{k+7}", detector="D1_duplicate", vendor_id=sid,
                      invoice_ids=[orig["invoice_id"], dup["invoice_id"]], kes_impact=orig["amount_kes"]))

# ---------- D5: split purchase + spike ----------
add_vendor("V306", "Westlands IT Consulting Ltd", "consulting")
for m in MONTHS:
    add_invoice("V306", safe_amount(400_000 * random.uniform(0.9, 1.1)), m + timedelta(days=14), "Consulting - monthly")
split = [add_invoice("V306", a, date(2026, 9, 8) + timedelta(days=i), "Core banking integration support")
         for i, a in enumerate([980_000, 975_000, 955_000])]
leaks.append(dict(leak_id="L20", detector="D5_anomaly", vendor_id="V306", invoice_ids=[s["invoice_id"] for s in split],
                  kes_impact=sum(s["amount_kes"] for s in split)))
add_vendor("V307", "Lavington Facilities Management Ltd", "facilities")
for m in MONTHS:
    amt = 1_800_000 if m == date(2026, 7, 1) else safe_amount(300_000 * random.uniform(0.95, 1.05))
    add_invoice("V307", amt, m + timedelta(days=10), "Facilities - monthly" if amt < 1e6 else "Facilities - 'emergency works'")
leaks.append(dict(leak_id="L21", detector="D5_anomaly", vendor_id="V307", kes_impact=1_500_000))

# ---------- D4 + D6: contracts ----------
add_vendor("V308", "CloudNest Hosting Ltd", "cloud_hosting", country="IE")
for m in MONTHS:
    add_invoice("V308", 600_000, m + timedelta(days=2), "Customer data platform hosting")  # overcharged vs 500k contract


def contract(vid, rate, auto=False, renew="2027-06-30", notice=60, esc=5, dp=True, exit_=True, audit=True,
             cust=False, loc="KE"):
    c = dict(vendor_id=vid, contract_rate_kes=rate, rate_unit="month", auto_renew=auto, renewal_date=renew,
             notice_days=notice, annual_escalation_pct=esc, has_data_protection_clause=dp, has_exit_clause=exit_,
             has_audit_rights_clause=audit, processes_customer_data=cust, data_location=loc)
    contracts.append(c)
    name = next(v["vendor_name"] for v in vendors if v["vendor_id"] == vid)
    txt = (f"MASTER SERVICES AGREEMENT between NCBA Bank Kenya PLC and {name}.\n"
           f"1. Fees: KES {rate:,} per month, payable within 30 days of a valid KRA eTIMS invoice.\n"
           f"2. Term: this agreement {'renews automatically' if auto else 'expires'} on {renew}"
           f"{f' unless either party gives {notice} days written notice' if auto else ''}.\n"
           f"3. Price review: fees increase by {esc}% on each anniversary.\n"
           + ("4. Data protection: the Supplier shall comply with the Data Protection Act 2019 and process personal data only on NCBA's written instructions.\n" if dp else "")
           + ("5. Exit: NCBA may terminate on 90 days notice; the Supplier shall support transition.\n" if exit_ else "")
           + ("6. Audit: NCBA and the Central Bank of Kenya may audit the Supplier's controls.\n" if audit else "")
           + (f"7. Data location: customer data is hosted in {loc}.\n" if cust else ""))
    with open(f"{D}/contracts/{vid}.txt", "w", encoding="utf-8") as f:
        f.write(txt)


for vid in random.sample([v["vendor_id"] for v in vendors if v["vendor_id"] < "V241"], 18):
    contract(vid, round(base[vid], -3), auto=random.random() < 0.5, renew=f"2027-0{random.randint(3, 9)}-30",
             esc=random.randint(3, 6))
contract("V304", 150_000, auto=True, renew="2026-12-19", notice=14, esc=12)        # D4 renewal + escalation
contract("V303", 370_000, auto=True, renew="2026-12-20", notice=21, esc=4)         # D4 renewal
contract("V308", 500_000, esc=5, dp=False, audit=False, cust=True, loc="IE")        # D4 overcharge + D6
contract("V305", 140_000, esc=5, dp=False)                                           # D6
contract("V306", 400_000, esc=5, dp=False, exit_=False)                              # D6
leaks += [dict(leak_id="L30", detector="D4_contract", vendor_id="V304", kes_impact=int(150_000 * 12 * 0.12)),
          dict(leak_id="L31", detector="D4_contract", vendor_id="V303", kes_impact=int(370_000 * 12 * 0.04)),
          dict(leak_id="L32", detector="D4_contract", vendor_id="V308", kes_impact=100_000 * 12),
          dict(leak_id="L40", detector="D6_vendor_risk", vendor_id="V308", kes_impact=0),
          dict(leak_id="L41", detector="D6_vendor_risk", vendor_id="V305", kes_impact=0),
          dict(leak_id="L42", detector="D6_vendor_risk", vendor_id="V306", kes_impact=0)]

# ---------- D3: licences ----------
lic = [("Microsoft 365 E3", "V303", 4000, 2900, 18_000, "2027-01-31"),
       ("Adobe Acrobat Pro", "V303", 300, 180, 48_000, "2027-03-31"),
       ("Salesforce Service Cloud", "V303", 200, 140, 120_000, "2027-02-28"),
       ("Jira Software", "V303", 400, 392, 9_000, "2027-05-31"),
       ("Power BI Pro", "V303", 250, 244, 14_000, "2027-01-31"),
       ("ServiceNow ITSM", "V303", 120, 118, 95_000, "2027-06-30"),
       ("DocuSign", "V303", 150, 147, 30_000, "2027-04-30")]
licences = []
for i, (p, vid, paid, act, price, ren) in enumerate(lic, 1):
    licences.append(dict(licence_id=f"LIC{i:02d}", vendor_id=vid, product=p, seats_paid=paid, seats_active_90d=act,
                         price_per_seat_kes_year=price, renewal_date=ren))
    if (paid - act) / paid > 0.1:
        leaks.append(dict(leak_id=f"L5{i}", detector="D3_unused_licences", vendor_id=vid, product=p,
                          kes_impact=(paid - act) * price))


def write(name, rows):
    with open(f"{D}/{name}", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


write("vendors.csv", vendors)
write("invoices.csv", invoices)
write("licences.csv", licences)
json.dump(contracts, open(f"{D}/contracts_extracted.json", "w"), indent=1)
json.dump(leaks, open(f"{D}/planted_leaks.json", "w"), indent=1)
print(f"{len(vendors)} vendors, {len(invoices)} invoices, {len(contracts)} contracts, {len(licences)} licences")
print(f"{len(leaks)} planted leaks, KES {sum(l['kes_impact'] for l in leaks)/1e6:.1f}m")
