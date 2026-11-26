# P2: Detection engine (and the integrator)

**You own:**
- `detectors.py`
- `test_detectors.py`
- `out/findings.json`

**You're also the integrator.** At each checkpoint, pull, run the whole pipeline and shout if anything breaks.

## Paste this into your Claude
> Read CLAUDE.md, CONTRACT.md and tasks/P2-detection-engine.md. I'm P2. Build detectors.py producing out/findings.json exactly per CONTRACT. Until data/ exists, generate a tiny throwaway fixture inside test_detectors.py. Then test against data/planted_leaks.json. Update my STATUS.md row, commit and push.

## detectors.py
- **Entry point:** `run_all(data_dir="data") -> list[dict]`. It writes `out/findings.json`, sorted by `kes_impact` from highest to lowest.
- **Each detector is a pure function** `detect_dX(dfs) -> list[dict]`. Each finding uses the CONTRACT schema and has a clear `rule_reason`.

| Detector | Rule | kes_impact | Suggested action |
|---|---|---|---|
| D1 duplicate | **(a)** Same `etims_number` → confidence 0.97. **(b)** Same vendor and amount within 45 days, with invoice ids that are ≥85 similar after stripping non-alphanumerics (use `rapidfuzz`) → 0.85. **(c)** Two vendor_ids sharing a `bank_account` or `kra_pin` that both received the same amount → 0.9. | The duplicate amount | `request_credit_note` / `hold_payment` |
| D2 overlap | ≥2 active vendors in `video_conferencing` or `sms_gateway`, active meaning invoiced in the last 90 days | Annual spend of every vendor except the cheapest | `consolidate_vendor` |
| D3 unused | `seats_paid − seats_active_90d` | Idle seats × `price_per_seat_kes_year` | `cancel_seats` |
| D4 contract | **(a)** `auto_renew` is true and renewal_date − notice_days falls within 30 days of today (2026-11-26). **(b)** Average invoiced monthly amount > contract_rate × 1.05. **(c)** Escalation > 7%. Uses `contracts_extracted.json` | For (b), the overcharge × 12 | `give_notice` / `renegotiate` |
| D5 anomaly | **(a)** Split purchase: ≥2 invoices from the same vendor within 7 days, each between 90% and 100% of the KES 1m limit. **(b)** A month's spend > mean + 3σ of that vendor's months. | The excess | `investigate` |
| D6 vendor risk | Any of: no data-protection clause; `processes_customer_data` with `data_location` ≠ KE; no exit clause; no audit-rights clause | 0 | `request_addendum`, severity high if customer data is involved |

**Severity:** high if ≥ KES 1m or customer data is involved, medium if ≥ KES 200k, otherwise low.

## test_detectors.py
Load `data/planted_leaks.json`, then **assert every planted leak is found** by the right detector. Print the recall per detector and how many findings weren't in the answer key, which are the false positives. Aim for **100% recall** and **fewer than 5 extra findings**. Tune the thresholds, not the data. If the data itself is wrong, tell P1.

## Integration checks (at T+45, T+90 and T+120)
`python generate_data.py && python detectors.py && python test_detectors.py && streamlit run app.py`
