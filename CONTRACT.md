# CONTRACT: frozen interfaces (change only with the whole team's agreement)

## Pipeline
```
generate_data.py (P1) ─► data/*.csv, data/contracts/*.txt, data/planted_leaks.json
extract_contracts.py (P1) ─► data/contracts_extracted.json
detectors.py (P2) ─► out/findings.json
app.py (P3) reads out/findings.json, falls back to sample/sample_findings.json if it's missing
app.py (P3) writes out/audit_log.jsonl
```
All money is **KES**, stored as an integer. Dates are **ISO `YYYY-MM-DD`**.

## data/vendors.csv
`vendor_id, vendor_name, category, kra_pin, bank_account, country, onboarded_date`
- **category** is one of: `video_conferencing, sms_gateway, office_supplies, cloud_hosting, software_licence, security, consulting, facilities, telecom, marketing`
- **country** is `KE` or another ISO code. It feeds the D6 data-outside-Kenya check.

## data/invoices.csv
`invoice_id, etims_number, vendor_id, amount_kes, invoice_date, paid_date, description, cost_centre, approver`
- The approval limit is **KES 1,000,000**. Above it needs a second approver, which matters for the D5 split-purchase check.

## data/licences.csv
`licence_id, vendor_id, product, seats_paid, seats_active_90d, price_per_seat_kes_year, renewal_date`

## data/contracts/<vendor_id>.txt
This is plain-text contract prose. It must mention:
- the rate
- whether it auto-renews
- the notice period
- the renewal date
- whether it has a data-protection clause, an exit clause and an audit-rights clause

## data/contracts_extracted.json
```json
[{"vendor_id":"V012","contract_rate_kes":150000,"rate_unit":"month","auto_renew":true,
  "renewal_date":"2026-12-19","notice_days":30,"annual_escalation_pct":12,
  "has_data_protection_clause":false,"has_exit_clause":true,"has_audit_rights_clause":false,
  "processes_customer_data":true,"data_location":"IE"}]
```

## data/planted_leaks.json (the answer key; P2 tests against it)
```json
[{"leak_id":"L01","detector":"D1_duplicate","vendor_id":"V007","invoice_ids":["INV-2026-0418","INV2026418"],"kes_impact":1840000}]
```

## out/findings.json (the only thing the app reads)
```json
[{"finding_id":"F-0001",
  "detector":"D1_duplicate",
  "title":"Same invoice paid twice",
  "vendor_id":"V007","vendor_name":"Acme Office Supplies Ltd",
  "kes_impact":1840000,
  "confidence":0.97,
  "severity":"high",
  "evidence":[{"label":"INV-2026-0418","detail":"eTIMS KRAMW0042026000318 · KES 1,840,000 · paid 2026-03-04"}],
  "rule_reason":"same etims_number and amount, paid 15 days apart",
  "suggested_action":"hold_payment",
  "explanation":null,
  "status":"open"}]
```
- **detector** is one of: `D1_duplicate, D2_overlap, D3_unused_licences, D4_contract, D5_anomaly, D6_vendor_risk`
- **severity** is one of: `high, medium, low`
- **suggested_action** is one of: `hold_payment, request_credit_note, cancel_seats, consolidate_vendor, give_notice, renegotiate, request_addendum, investigate`
- **explanation** is `null` from P2. P3 fills it from `cache/explanations.json`, keyed by finding_id, or from a live LLM call.
- `kes_impact` for D6 may be 0. Those findings are risk findings, not cost findings.

## cache/explanations.json (P3)
`{"F-0001": {"explanation": "...", "vendor_email": "..."}}`

## out/audit_log.jsonl (P3, append-only)
`{"ts":"2026-11-26T15:02:11","finding_id":"F-0001","action":"hold_payment","role":"procurement_manager","user":"demo","decision":"approved"}`
