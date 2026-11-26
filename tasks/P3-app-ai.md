# P3: App + AI (you drive the live demo)

**You own:**
- `app.py`
- `explain.py`
- `cache/`
- `out/audit_log.jsonl`

## Paste this into your Claude
> Read CLAUDE.md, CONTRACT.md and tasks/P3-app-ai.md. I'm P3. Build the Streamlit app.py reading out/findings.json, falling back to sample/sample_findings.json. Build explain.py with a cache. Update my STATUS.md row, commit and push.

## app.py (Streamlit). Start on `sample/sample_findings.json` right now, so you don't wait for anyone.
1. **Sidebar:**
   - A role switcher: `AP officer` / `Procurement manager` / `CFO`.
   - A "Scan 12 months of AP data" button, which shows a spinner for 2 seconds and then the results.
   - Counts: invoices, vendors and contracts, read from data/ if it exists.
2. **Headline, the AHA moment:**
   - A huge **"KES 41.2m avoidable spend found"**. Compute it as the sum of kes_impact, formatted as `KES 41.2m`.
   - The scan time.
   - A separate badge: "3 high-risk vendors", counting the D6 findings.
   - A small caption: "Illustrative data".
3. **A bar chart of KES by detector, plus 6 tabs** (Duplicates, Overlaps, Idle licences, Contracts, Anomalies, Vendor risk), each a table sorted by kes_impact.
4. **The finding detail panel:**
   - The evidence. For D1, show the 2 invoices **side by side** with the matching eTIMS number highlighted.
   - The `rule_reason` labelled **"Why the rules flagged it"**, and the AI explanation labelled **"Explanation (AI)"**. These two must look visually different.
   - The AI-drafted vendor email, which can be copied.
5. **Action buttons:**
   - Hold payment, Request credit note, Cancel seats and the other suggested actions.
   - Only the **Procurement manager** role can approve. AP officer sees "Approval required".
   - Each decision appends to `out/audit_log.jsonl` and moves the finding's status to approved or rejected.
   - An **Audit log** tab shows the log.
6. Use a clean NCBA-ish palette. Don't use the NCBA logo.

## explain.py
- `get_explanation(finding) -> {"explanation", "vendor_email"}`. It checks `cache/explanations.json` first.
- If the finding isn't cached and `ANTHROPIC_API_KEY` is set, call Claude with model `claude-sonnet-5-5`, read from an env var `LEAKLENS_MODEL`.
- **Mask personal data before sending:** replace employee approver names with role labels and bank account numbers with ****1234.
- Write the result into the cache.
- On any error, return the cached text or a template. **The demo must never crash or hang.** Use a 10-second timeout.
- Prompt rules: explain why the *rules* flagged it, in 2 sentences, for a procurement manager. Don't invent numbers; use only the fields given. The vendor email should be polite and firm, and reference the evidence.
- **Before feature freeze, pre-generate the cache for every finding** and commit `cache/explanations.json`, so the demo works offline.

## Demo script (3 minutes)
1. Scan.
2. Headline: KES 41.2m.
3. Open the top duplicate, side by side.
4. Show idle Microsoft 365 seats and the overlapping video tools.
5. Show the contract auto-renewing in N days.
6. Switch role, approve "Hold payment", show the audit log.
7. Show the vendor-risk card: "no data-protection clause, customer data in Ireland".
