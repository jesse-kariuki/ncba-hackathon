# Solution for challenge #6: "LeakLens", a spend-leak finder for NCBA procurement

## One-line pitch
LeakLens reads NCBA's invoices, contracts and licence lists. Fixed rules find duplicate payments, overlapping vendors, unused seats and risky contracts, and AI explains each finding and drafts the fix. Nothing is paid, held or cancelled without a manager's approval.

## The problem (the opening hook)
- NCBA's FY2025 operating costs were **KES 37.5bn, up 17%**. The cost-to-income ratio is about **52%** and the target is **45%**.
- Industry benchmarks: duplicate and erroneous payments are **0.8–2% of disbursements** (APQC), and **46–53% of SaaS licences go unused or underused** (Zylo).
- That works out to **KES 8–20m lost per KES 1bn of vendor spend**, from duplicates alone.
- CBK's draft guidance on third-party tech vendors (consultation closed 7 Nov 2026) says banks must monitor their vendors. A CBK survey found **26% of banks can't**.
- Today procurement and accounts payable catch these leaks by hand, with spreadsheets and annual audits, *after* the money has gone.

## Users
- **Procurement manager.** Sees the findings, approves actions and negotiates with vendors.
- **Accounts payable officer.** Gets a "hold before you pay" warning on a suspected duplicate.
- **CFO / Group COO.** Sees one headline number: KES recoverable, with a trend.
- **Third-party risk / compliance.** Sees vendor risk flags.

## How it works
```
CSV / ERP export ─► Normalise ─► RULES ENGINE (decides) ─► Findings + KES impact ─► LLM (explains, drafts) ─► Dashboard ─► Human approves ─► Audit log
   invoices          vendor name     6 detectors, each with        score, evidence        plain-English reason,     KES headline,    hold / email /
   vendors           matching,       a threshold you can tune                                vendor email,            drill-down       cancel seat
   contracts (text)  currency→KES                                                             clause extraction
   licences + usage
```
**Fixed rules make every decision and the AI never does**, the same pattern as JobBridge. The AI has three jobs:
1. Pull contract terms out of the contract text into JSON: renewal date, notice period, rate and the clauses that are present.
2. Explain each finding in plain English.
3. Draft the email to the vendor or the cancellation request.

## The 6 detectors (one per phrase in the challenge brief)
| # | Detector | Rule (deterministic) | Brief wording it covers |
|---|---|---|---|
| D1 | **Duplicate invoice** | Same vendor and amount within 45 days; **or** invoice numbers that match fuzzily (INV-0042 vs INV42); **or** the same amount paid to two vendor records that share a bank account or KRA PIN. Check the **KRA eTIMS invoice number** first, because a repeated eTIMS number means a certain duplicate. | duplicate subscriptions |
| D2 | **Overlapping vendors** | 2 or more active vendors in the same category, e.g. 3 video-conferencing tools or 2 SMS gateways. | overlapping vendor services |
| D3 | **Unused licences** | Seats paid for minus users active in the last 90 days, multiplied by the price per seat. | duplicate subscriptions / waste |
| D4 | **Contract inefficiency** | Auto-renewal within 60 days of its deadline; invoiced rate above the contract rate; an annual price increase above inflation; an SLA credit owed but never claimed. | contract inefficiencies |
| D5 | **Spending anomaly** | A month more than 3 standard deviations above that vendor's average; **split purchases** just under an approval limit (e.g. 3 invoices of KES 990k against a KES 1m limit); a new vendor sharing a bank account with an employee. | spending anomalies |
| D6 | **Third-party risk** | The contract has no data-protection clause, no exit clause, or no audit-rights clause; or the vendor processes customer data outside Kenya. Aligned to the CBK third-party guidance and the Data Protection Act. | *(our extra, which adds a compliance angle)* |

Each finding stores: `id, detector, vendor, kes_impact, confidence, evidence[], explanation, suggested_action, status (open/approved/rejected), approver, timestamp`.

## Fake data (generated with deliberately planted leaks, so the demo numbers are fixed)
- **12 months of data:** about 5,000 invoices, about 200 vendors, 25 contracts as text, and 15 software licences with usage.
- **Planted leaks:**
  - 9 duplicate invoices, including one with a repeated eTIMS number and one paid to two vendor records sharing a bank account
  - 3 video-conferencing tools
  - 2 SMS gateways
  - 1,400 idle Microsoft 365 / Adobe seats
  - 2 auto-renewals about to trigger
  - 1 rate above the contract price
  - 1 set of split purchases
  - 3 contracts with no data-protection clause

```json
{"finding_id":"F-0007","detector":"D1_duplicate","vendor":"Acme Office Supplies Ltd",
 "kes_impact":1840000,"confidence":0.97,
 "evidence":[{"invoice":"INV-2026-0418","etims":"KRAMW0042026000318","amount":1840000,"paid":"2026-03-04"},
             {"invoice":"INV2026418","etims":"KRAMW0042026000318","amount":1840000,"paid":"2026-03-19"}],
 "explanation":"Same KRA eTIMS number and amount paid twice, 15 days apart. The second invoice reformatted the invoice number.",
 "suggested_action":"Request a credit note and hold future payments until it is resolved.","status":"open"}
```

## Demo flow (5 screens, about 3 minutes)
1. **Load the data.** Show "12 months of accounts-payable data: 4,812 invoices, 214 vendors, 25 contracts", then press **Scan**.
2. **This is the AHA moment.** The headline reads **"KES 41.2m avoidable spend found in 12 seconds"**, broken down by detector, with a separate "3 high-risk vendors" counter. Say out loud that the data is illustrative.
3. **Open a duplicate.** Show the two invoices side by side, with the matching eTIMS number highlighted and the AI's plain-English reason underneath.
4. **Show licences and overlaps.**
   - 3 video tools: keep one and save KES X a year.
   - 1,400 idle seats: cancel them at renewal.
   - Contract alert: "Auto-renews in 23 days. The notice deadline is in 8."
5. **Take action.**
   - Show the AI-drafted email to the vendor.
   - Press **"Hold payment"**. It needs the procurement manager's approval (switch role in the app), then writes an entry to the audit log.
   - The vendor risk card shows "No data-protection clause. Request an addendum."

## Theme mapping (one slide)
| Verb | What LeakLens does | Before → after (illustrative) |
|---|---|---|
| **Reuse** | Reuses existing ERP and accounts-payable exports, contract PDFs, licence admin reports and KRA eTIMS data. No new system of record. | No new data entry. |
| **Automate** | Matches invoices, extracts contract terms, counts seat usage and drafts vendor emails. | Weeks of manual audit become minutes. |
| **Reduce** | Reduces avoidable spend, duplicate payments, money spent on idle seats, and vendor risk. | Measured as KES recovered per month. |
| **Eliminate** | Eliminates duplicate payments before they go out, redundant tools, missed renewal deadlines and blind spots on third-party risk. | Every leak is caught *before* payment. |

## Why NCBA, the business case and scale
- **Why NCBA:** it serves the cost-to-income target of 45% and the new CBK third-party vendor rules. One tool covers cost and compliance.
- **Business case:** it pays for itself if it finds 0.1% of vendor spend. The benchmarks above suggest 0.8–2% is plausible for duplicates alone.
- **Scale, phase 1:** the group's own spend across Kenya, Uganda, Rwanda and Tanzania. This fits the regional pillar.
- **Scale, phase 2 (the revenue angle):** offer it to NCBA's **SME customers on LOOP BIZ+** as a "find your business's spend leaks" feature, which deepens customer loyalty. This turns a cost tool into a product that makes money.

## Compliance and security
- No payment is changed without a named approver. The detectors only flag. Every action is logged.
- Vendor and employee personal data is masked before any text goes to the LLM, and the tool runs in a Kenyan or private-cloud deployment. This covers the Data Protection Act 2019 and Regulations 2021.
- Role-based access: AP officer, procurement manager, CFO.
- It fits the CBK outsourcing guideline and the draft third-party guidance, and helps NCBA comply with it.

## Judge questions with answers
1. **"SAP Ariba, Coupa and other procurement suites already do this."**
   - Those are expensive suites that take a long time to roll out. LeakLens runs on the exports NCBA already has, in weeks, and checks KRA eTIMS invoice numbers for duplicates.
   - It combines cost-cutting with the new CBK third-party risk checks.
   - It's explainable: fixed rules make the decision and AI explains it.
2. **"What about false positives? Will you block legitimate payments?"**
   - It never blocks on its own. It flags, scores its confidence and puts the item in a queue for a person.
   - Thresholds can be tuned, and every rejected flag is logged to improve the rules.
3. **"Where do the KES 41m come from?"**
   - It's illustrative data with planted leaks.
   - The real-world range comes from APQC: 0.8–2% of disbursements lost to duplicates or errors.
   - The pilot would measure NCBA's actual figure over 3 months of past accounts-payable data, at zero risk because it reads data only.

## Build plan: 4 people, Streamlit for speed
| Who | Task | Time |
|---|---|---|
| **A: data** | Python script that generates `invoices.csv, vendors.csv, contracts/*.txt, licences.csv` with the planted leaks (Faker plus Kenyan vendor names) | 45 min |
| **B: engine** | `detectors.py`: D1–D6 in pandas, returning a findings DataFrame with KES impact. Unit-check it finds every planted leak. | 75 min |
| **C: UI + LLM** | Streamlit app: headline, detector tabs, duplicate side-by-side view, approve button with audit log. LLM prompts to explain findings, draft vendor emails and extract contract clauses. Cache LLM outputs so the demo can't fail. | 90 min |
| **D: pitch** | 7 slides (hook with the CIR figure → problem → demo → theme mapping → why NCBA and scale → compliance → ask), **record a backup demo video** at the end, and rehearse | ongoing |

**Plan to cut if time runs short:** keep D1, D2, D3 and the approval step, and turn D4–D6 into static cards.
