Design a complete, clickable web prototype for **LeakLens**, our entry to the NCBA FinTech Hackathon, Challenge #6: Data-Driven Procurement & Vendor Cost Optimization. The theme is **Reuse, Automate, Reduce, Eliminate**. Use the attached folder: DESIGN-BRIEF.md, logo.svg, splash.html, findings.json (real numbers) and brief-photos/ (the official challenge).

The official brief asks for an analytics solution that identifies **duplicate subscriptions, overlapping vendor services, contract inefficiencies and spending anomalies**, in order to **improve procurement decisions and reduce avoidable expenditure**. LeakLens reads a bank's invoices, contracts and software licence reports, finds the money leaking out, and routes every fix to a person. The core principle must be visible everywhere: **Rules decide, AI explains, and a human approves.**

## Brand (build this first)
- **Logo:** refine logo.svg. The mark is a magnifying lens catching a gold drop (the leak), plus the wordmark "Leak**Lens**" with "Lens" in green.
- **Logo deliverables:**
  - full lockup
  - mark only
  - app icon (rounded square)
  - favicon
  - light and dark versions
- **Splash animation:** refine splash.html, about 3 seconds. The lens ring draws itself, the gold drop falls into the lens and settles, a white scan line sweeps through, then the wordmark rises with the tagline **"Find the leaks before you pay."** Respect prefers-reduced-motion.
- **Colours:**

| Colour | Hex |
|---|---|
| Green (primary) | #0B6E4F |
| Light green | #18A374 |
| Gold (money and leaks) | #F2A900 |
| Ink | #12263A |
| Dark-mode background | #0E1F2F |
| Rule blue | #2B59C3 |
| Risk red | #C8372D |

- **Type:** Inter, with tabular figures. Show money as "KES 56.0m".
- **Tone:** calm, audit-grade and trustworthy, a Bloomberg terminal crossed with Linear. Not cartoonish.
- **Modes:** light mode is the default for the projector. Also include a dark mode.
- **Do NOT use NCBA's logo or imitate NCBA's branding.** This is our own product pitched to NCBA.

## Screens: build ALL of them, linked into one click-through flow
1. **Splash.** The logo animation, which then fades into sign-in.
2. **Sign in / choose role.** Three cards: AP officer, Procurement manager and CFO. Each card has a one-line description of what that role can do.
3. **Connect data (REUSE).**
   - Four source cards, each with a "connected" tick and the record count:
     - ERP / Accounts-payable export: 2,988 invoices, 251 vendors
     - KRA eTIMS invoice numbers
     - Contract repository: 23 contracts
     - Licence admin reports: Microsoft 365, Adobe, Salesforce and 4 more
   - Message: "No new system. LeakLens reuses the data you already have."
   - Primary button: **Scan 12 months**.
4. **Scan in progress (AUTOMATE).**
   - A live checklist that ticks off one line at a time, about 4 seconds in total:
     - Matching 2,988 invoices…
     - Checking KRA eTIMS numbers…
     - Reading 23 contracts…
     - Counting active licence seats…
     - Looking for spending anomalies…
     - Checking vendor risk…
   - A gold KES counter climbs from 0 to 56.0m.
5. **Dashboard: the AHA screen (REDUCE).**
   - A huge headline: **"KES 56.0m avoidable spend"**, with "found in 12 seconds · 22 findings".
   - **Five cards named exactly after the brief.** Each shows its KES total and count, taken from findings.json:
     - Duplicate subscriptions & payments
     - Overlapping vendor services
     - Contract inefficiencies
     - Spending anomalies
     - Vendor risk (3 high-risk vendors)

     Idle licences go under duplicate subscriptions.
   - A horizontal bar chart of KES by category.
   - A "Top 5 actions this week" list.
   - A thin theme strip: **Reuse · Automate · Reduce · Eliminate**, each with one line of explanation.
6. **Findings list.** One tab per category. Rows show severity, title, vendor, KES amount, confidence and status (open, approved or rejected). Include filters and search.
7. **Finding detail: duplicate invoice.** This is the hero detail screen.
   - The two invoices side by side, with the identical KRA eTIMS number highlighted and the reformatted invoice number (INV-… vs INV…) highlighted.
   - A blue box **"Why the rules flagged it"**, which is deterministic and shows its confidence.
   - A green box **"Explanation (AI · Gemini)"**.
   - A "Draft email to vendor" button that opens a drawer with an editable email.
   - The primary action **"Hold payment / Request credit note"**.
8. **Finding detail: idle licences.** For 1,100 idle Microsoft 365 seats out of 4,000 (KES 19.8m), show a seat-usage bar, the renewal date and the action "Cancel idle seats at renewal".
9. **Finding detail: overlapping vendors.** For 3 video-conferencing tools (Zoom, Webex and Teams Rooms), compare them side by side by spend and recommend which one to keep. The saving is KES 6.2m a year.
10. **Finding detail: contract inefficiency.** The contract auto-renews in 24 days with its **notice deadline in 3 days**. Show a timeline from today to the notice deadline to the renewal, plus a 12% price-increase warning. Action: "Give notice".
11. **Finding detail: spending anomaly.** Three invoices of KES 980k, 975k and 955k in 4 days, each just under the KES 1m approval limit. Show a mini timeline with the limit line. Action: "Refer to internal audit".
12. **Approval (human in the loop).**
    - **As AP officer:** the action is locked with "Needs Procurement manager approval. Nothing is paid, held or cancelled automatically."
    - **As Procurement manager:** Approve and Reject buttons with a comment field, then a confirmation toast saying the decision is written to the audit trail.
13. **Vendor 360: CloudNest Hosting Ltd.**
    - Monthly spend chart, showing it's billed KES 600k a month against a KES 500k contract.
    - Contract terms.
    - A clause checklist: data protection ✗, exit ✓, audit rights ✗.
    - **Customer data stored in Ireland (outside Kenya)**, flagged against the Data Protection Act 2019 and the CBK third-party guidance.
    - Action: "Request addendum".
14. **Savings tracker (ELIMINATE).**
    - A funnel: KES found → approved → recovered.
    - A monthly trend.
    - Before and after: "Duplicate payments caught before payment".
    - Recovered amounts per category.
15. **Audit log.** A table of time, user, role, finding, action and decision, with an "Export for internal audit / CBK" button.
16. **Settings.** Rule thresholds a manager can tune: approval limit KES 1,000,000, duplicate window 45 days, idle-seat threshold 10%, renewal alert 30 days. Also an AI provider choice: Gemini or Claude. Add a note: "AI only explains. Rules decide."
17. **Mobile (for an Android app later).**
    - A lock-screen push notification: "⚠ Possible duplicate: KES 1.82m to Nyeri Mombasa Cloud Services Ltd. Hold payment?"
    - Tapping it opens a one-tap approval card.
    - A compact mobile dashboard with the KES headline.

## Layout and behaviour
- **Desktop web app** at 1440 wide. Left sidebar navigation: Dashboard, Findings, Vendors, Savings, Audit log, Settings. The top bar shows the role switcher and "Illustrative data".
- **Every number must come from findings.json**, and none may be invented. Always label the data as illustrative.
- **Include empty, loading and success states** where they matter: the scan, approve and email-sent states.
- **Accessibility:** WCAG AA contrast, and severity must never be shown by colour alone.
- **Clickable path for the 3-minute demo:**
  1. Splash
  2. Sign in as Procurement manager
  3. Connect data
  4. Scan
  5. Dashboard
  6. Duplicate detail
  7. Approve
  8. Idle licences
  9. Contract deadline
  10. Vendor 360 (CloudNest)
  11. Savings tracker
  12. Audit log
