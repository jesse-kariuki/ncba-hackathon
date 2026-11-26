# P1: Data + Contracts + Pitch

**You own:**
- `generate_data.py`
- `extract_contracts.py`
- everything in `data/`
- `PITCH.md`
- the backup demo video

## Paste this into your Claude
> Read CLAUDE.md, CONTRACT.md and tasks/P1-data-contracts-pitch.md in this repo. I'm P1. Build generate_data.py exactly to the CONTRACT schemas, run it, check the output, update my STATUS.md row, then commit and push. Then do extract_contracts.py.

## 1. generate_data.py (push within 45 min, it's the critical path)
- Use a fixed `random.seed(42)` so the numbers are identical on every laptop.
- **Data size:** about 200 vendors with Kenyan-sounding company names (e.g. "Kilimani Office Supplies Ltd"), and about 5,000 invoices over **2025-12-01 → 2026-11-25**.
- Fake KRA PINs look like `P051234567X`. Fake eTIMS numbers must be unique, except where a duplicate is planted.
- **Licences:** 15 products, such as Microsoft 365, Adobe, Zoom, Webex, Teams Rooms, Salesforce and Jira.
- Write `data/contracts/<vendor_id>.txt` for the 25 biggest vendors, as short realistic contract prose.

### PLANT these leaks and record each one in `data/planted_leaks.json`
| Leak | Detector | What to plant |
|---|---|---|
| 9 duplicates | D1 | 3 with the same eTIMS number and amount, invoice number reformatted (`INV-2026-0418` vs `INV2026418`). 3 with the same vendor and amount within 45 days. 3 where two vendor records share a bank account and KRA PIN. |
| Overlap | D2 | 3 active video-conferencing vendors and 2 SMS gateways. |
| Idle seats | D3 | Microsoft 365: 4,000 paid, 2,900 active. Adobe: 300 paid, 110 active. Zoom: 500 paid, 60 active. |
| Contract | D4 | 2 auto-renewals with renewal dates in Dec 2026 and notice deadlines within 10 days of 2026-11-26. 1 vendor invoicing 20% above its contract rate. |
| Anomaly | D5 | 1 split purchase: 3 invoices of KES 960k–990k, same vendor, same week. 1 vendor with a month at 6 times its normal spend. |
| Vendor risk | D6 | 3 contracts with no data-protection clause, including one cloud vendor storing customer data in `IE`. |

**Target:** the planted KES total should land around **KES 40m**. Print a summary table at the end.

## 2. extract_contracts.py
- Turn `data/contracts/*.txt` into `data/contracts_extracted.json`, following the schema in CONTRACT.md.
- Use the Claude API if `ANTHROPIC_API_KEY` is set. Otherwise ask *your* Claude Code session to read the contracts and write the JSON once, then commit it. **The committed JSON is what the demo uses.**

## 3. PITCH.md and the deck (start once the data is pushed): 7 slides, 3 minutes
1. **Hook:** NCBA FY2025 operating costs were KES 37.5bn (up 17%). The cost-to-income ratio is about 52% and the target is 45%.
2. **Problem:** duplicate and erroneous payments run 0.8–2% of disbursements (APQC), and 46–53% of SaaS licences go unused (Zylo). 26% of Kenyan banks can't continuously monitor their vendors (CBK survey).
3. **Live demo** (P3 drives it).
4. **Reuse / Automate / Reduce / Eliminate** mapping (the table in docs/SOLUTION.md).
5. **Why NCBA and how it scales:** it serves the cost-to-income target and the CBK third-party rules, then rolls out regionally, then to LOOP BIZ+ SMEs.
6. **Compliance:** a human approves every action, personal data is masked before it goes to the LLM, and everything goes in an audit log.
7. **The ask:** a 3-month, read-only pilot on NCBA's past accounts-payable data.

Get the sources from docs/RESEARCH.md. **Say out loud that the demo numbers come from fake data.**

## 4. Backup video (at feature freeze, T+120)
Make a screen recording of the full demo, 2–3 minutes. Keep it on a laptop **and** a phone.
