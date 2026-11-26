# LeakLens pitch: 7 slides, 3 minutes (+ Q&A)
Challenge #6, Data-Driven Procurement & Vendor Cost Optimization · Theme: **Reuse, Automate, Reduce, Eliminate**
**Brand:**
- Colours: green `#0B6E4F`, gold `#F2A900`, ink `#12263A`, dark background `#0E1F2F`
- Font: Inter
- Logo: `design/logo.svg`
- Visuals: screenshots from the Claude Design project or the website (`localhost:3000`)

---

## Slide 1: Hook (20s)
**Title:** NCBA wants 7 points off its cost-to-income ratio.

- NCBA's FY2025 operating costs: **KES 37.5bn, up 17%**.
- Cost-to-income ratio: **about 52%**, against a **target of 45%**.
- Say: "Part of that gap is money already leaving the bank by mistake. LeakLens finds it."

Sources: [The Star, 26 Mar 2026](https://www.the-star.co.ke/business/2026-03-26-ncba-posts-sh234-billion-profit-as-dividend-rises-and-new-strategy-unveiled) · [Tech-ish](https://tech-ish.com/2026/04/06/ncba-fy-2025-results/)

## Slide 2: Problem (25s)
**Title:** Banks leak money they've already approved.

- **0.8–2% of payments** are duplicates or errors (APQC). That's **KES 8–20m per KES 1bn** of vendor spend.
- **46–53% of software licences** go unused (Zylo 2025/2026).
- **26% of Kenyan banks** can't continuously monitor their vendors (CBK survey). CBK's new third-party guidance closed for comment on 7 Nov 2026.
- Today these leaks are found in the annual audit, **after** the money has gone.

Sources: [Corpay/APQC](https://www.corpay.com/resources/blog/duplicate-payment-detection) · [Zylo](https://zylo.com/news/2025-saas-management-index) · [The Star](https://www.the-star.co.ke/business/kenya/2025-08-08-banks-exposed-by-poorly-drafted-tech-vendor-contracts-cbk-warns)

## Slide 3: Live demo (75s)
**Title:** LeakLens: find the leaks before you pay. Switch to the website at `localhost:3000`.

1. Connect data and scan. The **KES 56.0m** headline appears.
2. Open the duplicate invoice. Two invoices side by side with the **same KRA eTIMS number**. The rule's reason sits next to the AI explanation.
3. Switch to the AP officer role: the action is **locked**. Switch to Procurement manager, **Approve**, and it's written to the audit log.
4. Show the idle licences: **1,100 idle Microsoft 365 seats, KES 19.8m**.
5. Vendor 360, CloudNest: **no data-protection clause, customer data stored in Ireland**.

**Backup if the demo breaks:** the backup video, or the Streamlit app (`streamlit run app.py`).

## Slide 4: How it maps to the theme (20s)
| | What LeakLens does |
|---|---|
| **Reuse** | Existing AP exports, KRA eTIMS numbers, contracts and licence reports. No new system. |
| **Automate** | Matches 2,988 invoices, reads 23 contracts and drafts vendor emails in seconds. |
| **Reduce** | KES 56.0m of avoidable spend identified (illustrative data). |
| **Eliminate** | Duplicates stopped *before* payment, redundant tools, missed renewal deadlines. |

## Slide 5: Why NCBA, and how it scales (20s)
- It helps hit the **45% cost-to-income target**, and gets NCBA ahead of **CBK's third-party vendor rules**.
- **Phase 1:** the group's own spend across Kenya, Uganda, Rwanda and Tanzania.
- **Phase 2:** offer it to **SME customers on LOOP BIZ+** as "find your business's spend leaks", which turns a cost tool into revenue and keeps customers.
- **It pays for itself** if it finds just 0.1% of vendor spend.

## Slide 6: Trust and compliance (15s)
**Title:** Rules decide. AI explains. Humans approve.
- Every finding comes from a deterministic rule with a confidence score. The AI (Gemini or Claude) only explains and drafts.
- **Nothing is paid, held or cancelled automatically.** Only the Procurement manager role can approve, and every step is in an append-only audit log.
- Personal data is masked before any text reaches the AI. That covers the Data Protection Act 2019, the 2021 Regulations and the CBK outsourcing guideline.

## Slide 7: The ask (10s)
**Title:** A 3-month, read-only pilot on NCBA's past accounts-payable data.
- Zero risk: it reads data only. We measure the real KES figure.
- Stack: FastAPI rules engine, Next.js web app (installable on Android as a PWA), and Gemini/Claude for explanations.
- Team: [names]

---

## Say out loud
- "The numbers in the demo come from **illustrative data** with planted leaks. The real-world range comes from APQC."

## Likely judge questions
1. **"SAP Ariba and Coupa already do this."**
   - Those are expensive suites that take a long time to roll out. LeakLens runs on the exports NCBA already has, in weeks.
   - It's Kenya-specific: it checks KRA eTIMS numbers and the CBK third-party rules.
   - It's explainable: rules decide, the AI only explains.
2. **"What about false positives? Will you block legitimate payments?"**
   - It never blocks on its own. Every finding goes to a person's queue with its confidence score.
   - Thresholds can be tuned in Settings.
   - On our test data it found **22 of 22 planted leaks with 0 false positives**.
3. **"Where does KES 56m come from?"**
   - It's illustrative data.
   - The real benchmark is APQC's 0.8–2% of disbursements.
   - The pilot measures NCBA's actual figure.
4. **"What if the AI is wrong?"**
   - The AI never decides. The rule's reason is shown separately in blue, and a human approves every action.

## Running the demo
```
pip install -r requirements.txt fastapi "uvicorn[standard]" python-multipart
uvicorn backend.main:app --port 8000          # terminal 1, from the repo root
cd frontend && npm install && npm run dev     # terminal 2, then open http://localhost:3000
```
Reset between rehearsals: **Settings → Reset demo**.
