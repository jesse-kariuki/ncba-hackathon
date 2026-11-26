# LeakLens: design brief (give this whole `design/` folder to Claude Design)

## Context
- This is for the **NCBA FinTech Hackathon** (Strathmore, 26 Nov 2026). The theme is **Reuse, Automate, Reduce, Eliminate**.
- We chose **Challenge #6: Data-Driven Procurement & Vendor Cost Optimization**. The photos of the official brief are in `brief-photos/`.
- The exact wording of the brief:
  - "An analytics solution that identifies **duplicate subscriptions, overlapping vendor services, contract inefficiencies and spending anomalies**."
  - Business value: "Improve procurement decisions and reduce avoidable expenditure."
- **LeakLens** reads a bank's invoices, contracts and software licence reports, finds money leaking out, and makes someone accountable for fixing each leak.
- Core principle, which must be visible in the UI: **Rules decide, AI explains, and a human approves.**

## Users
- **CFO / COO:** wants one number and a trend.
- **Procurement manager:** works through findings, approves actions and emails vendors.
- **Accounts payable officer:** gets a "stop, this looks like a duplicate" warning before paying.
- **Compliance / third-party risk:** checks vendor contracts against the Data Protection Act and the CBK third-party guidance.

## Real numbers to use (from `findings.json`, illustrative data)
- **Headline:** **KES 56.0m avoidable spend** found across **22 findings**, after scanning 2,988 invoices from 251 vendors over 12 months, plus 23 contracts and 7 licence reports.
- **The biggest findings:**
  - 1,100 idle Microsoft 365 seats: **KES 19.8m**
  - 3 video-conferencing tools doing the same job: **KES 6.2m**
  - a purchase split into 3 invoices just under the KES 1m approval limit: **KES 2.9m**
  - the same invoice paid twice (same KRA eTIMS number, invoice number reformatted)
  - a vendor billing 20% above its contract rate
  - a contract that auto-renews in 24 days with its **notice deadline in 3 days**
- **Vendor risk:** CloudNest Hosting has **no data-protection clause and stores customer data in Ireland**.

## Brand
- **Name:** LeakLens. Tagline: **"Find the leaks before you pay."**
- **The logo is `logo.svg`:** a lens catching a gold drop. **The splash is `splash.html`:** the ring draws, the drop falls into the lens, a scan line passes and the wordmark rises. Open it in a browser to see it.
- **Colour tokens:**

| Token | Hex | Use |
|---|---|---|
| Green | `#0B6E4F` | Primary, buttons, positive |
| Light green | `#18A374` | Accents |
| Gold | `#F2A900` | The leak, money and highlights |
| Ink | `#12263A` | Text |
| Navy background (dark mode) | `#0E1F2F` | Dark backgrounds |
| Rule blue | `#2B59C3` | "Rule" evidence |
| Risk red | `#C8372D` | High severity |

- Use **Inter** for type. Show numbers with tabular figures, and money as **KES 56.0m**.
- **Do NOT use NCBA's logo or imitate NCBA's branding.** This is our own product pitched to NCBA.
- **Tone:** calm, audit-grade and trustworthy, like a Bloomberg terminal crossed with Linear. Avoid cartoonish fintech looks.
- **Light mode is the default** for the projector. Also design a dark mode.

## Screens (★ = must have for the demo, ☆ = nice to have)
1. ★ **Splash / sign-in.** Show the logo animation, then "Sign in as: AP officer · Procurement manager · CFO".
2. ★ **Connect data (REUSE).** Four source cards with ticks: ERP / AP export, KRA eTIMS invoices, Contract repository (PDF), and Licence admin reports (M365, Adobe, Salesforce). The message is "no new system, we reuse what you have". Primary button: **Scan 12 months**.
3. ★ **Scan in progress (AUTOMATE).** A live checklist that ticks off one by one. The six steps are:
   - "Matching 2,988 invoices…"
   - "Checking eTIMS numbers…"
   - "Reading 23 contracts…"
   - "Counting active seats…"
   - "Looking for spending anomalies…"
   - "Checking vendor risk…"

   A counter climbs in KES as it runs. It takes about 4 seconds.
4. ★ **Dashboard: the AHA screen (REDUCE).**
   - A huge **KES 56.0m avoidable spend**, with "found in 12 seconds".
   - **Four cards named exactly after the brief:** Duplicate subscriptions · Overlapping vendor services · Contract inefficiencies · Spending anomalies. Add a fifth card: Vendor risk (3 high-risk vendors).
   - A bar chart of KES by category.
   - "Top 5 actions this week".
5. ★ **Finding detail.**
   - Evidence, with duplicates shown **side by side** and the matching eTIMS number highlighted.
   - A blue box **"Why the rules flagged it"**, which is deterministic and shows the confidence.
   - A green box **"Explanation (AI · Gemini)"**.
   - A button "Draft email to vendor".
   - The action button.
6. ★ **Approval (human in the loop).**
   - As AP officer, the action is locked with the message "Needs Procurement manager approval".
   - As manager, there are Approve and Reject buttons with a comment field, and the decision goes to the audit trail.
   - Microcopy: **"Nothing is paid, held or cancelled automatically."**
7. ★ **Savings tracker (ELIMINATE).**
   - KES found, then approved, then recovered, as a funnel or tracker.
   - Before and after: "duplicate payments caught **before** payment".
   - A monthly trend.
8. ☆ **Vendor 360.** One vendor's spend over time, contract terms (renewal, notice, price increase), clauses present or missing, and data location. Use the CloudNest example.
9. ☆ **Audit log.** A table of who did what and when, exportable for internal audit and CBK.
10. ☆ **Mobile view (for an Android app later).** A push notification: "⚠ Possible duplicate: KES 1.82m to Nyeri Mombasa Cloud Services Ltd. Hold payment?" Opening it shows a one-tap approval card.

## Theme mapping (show it as a strip on the dashboard or in the deck)
- **Reuse:** existing AP exports, eTIMS, contracts and licence reports.
- **Automate:** invoice matching, contract reading and drafting vendor emails.
- **Reduce:** avoidable spend, here KES 56.0m.
- **Eliminate:** duplicate payments before they're paid, redundant tools and missed renewal deadlines.

## Data shape
`findings.json` follows the schema in `../CONTRACT.md`. Each finding has: detector, title, vendor_name, kes_impact, confidence, severity, evidence[label, detail], rule_reason, suggested_action and status.
