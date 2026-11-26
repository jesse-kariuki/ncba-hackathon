# NCBA Hackathon: research on all 6 challenges (26 Nov 2026)
Theme: **Reuse, Automate, Reduce, Eliminate.** Every challenge is about cutting NCBA's internal costs.

## The hook that works for every challenge
- NCBA's FY2025 operating expenses were **KES 37.5bn, up 17%**. The cost-to-income ratio was **about 52.3%** against a **medium-term target of 45%** ([The Star](https://www.the-star.co.ke/business/2026-03-26-ncba-posts-sh234-billion-profit-as-dividend-rises-and-new-strategy-unveiled), [Tech-ish](https://tech-ish.com/2026/04/06/ncba-fy-2025-results/)). Sources differ slightly: 51% vs 52.3%.
- Opening line: "NCBA wants to take about 7 points off its cost-to-income ratio. Here's one piece of that."
- Caution: operating expenses include staff costs. Only claim savings on the part your idea actually touches.

## Scorecard (1–5; buildability = a mock-up in a few hours)
| # | Challenge | Innov | Scale | Security | Impact | Build | Theme fit | **Total** |
|---|---|---|---|---|---|---|---|---|
| 3 | AI Cybersecurity Ops | 4 | 4 | 5 | 5 | 4 | 4 | **26** |
| 6 | Procurement & Vendor Cost | 3 | 4 | 3 | 4 | 5 | 5 | **24** |
| 2 | Cloud & IT Cost Optimizer | 3 | 4 | 3 | 4 | 4 | 5 | **23** |
| 5 | Customer Self-Service | 2 | 5 | 3 | 4 | 4 | 4 | **22** |
| 1 | AI IT Service Desk | 2 | 4 | 3 | 3 | 5 | 4 | **21** |
| 4 | Network & Infra Optimization | 3 | 3 | 3 | 4 | 2 | 3 | **18** |

---

## #3 AI-Powered Cybersecurity Operations (RECOMMENDED)
**Evidence**
- Kenyan bank customers lost a record **about KES 1.9bn to fraud in 2025**. Only **KES 127m** of the KES 2.03bn exposed was recovered, and card fraud was about 34% of losses ([TechTrendsKE](https://techtrendske.co.ke/2026/11/06/kenya-banking-fraud-2025/), [Business Daily](https://www.businessdailyafrica.com/bd/corporate/companies/bank-customers-lose-a-record-sh1-9bn-to-fraud-5660082)).
- Kenya detected **4.56bn cyber threats in Oct–Dec 2025**, up 441% ([Capital FM](https://www.capitalfm.co.ke/business/2026/04/cyber-threats-surge-441pc-to-4-56bn-on-digital-growth/)).
- NCBA has spent heavily on security: a reported KES 644m ([Capital FM](https://www.capitalfm.co.ke/business/?p=99473)) and a wider Sh6.5bn ([Standard](https://www.standardmedia.co.ke/business/article/2001502437/ncba-splashes-sh6-5b-to-fortify-its-cybersecurity-infrastructure)). A 2026 NCBA job ad for Head of Group Security & Investigations names **AI-enabled fraud** as a threat ([NCBA](https://ncbagroup.com/blog/job/head-group-security-investigations/)).
- **Alert fatigue:** vendor-cited false-positive rates run roughly 46–80%, and average triage takes **56–70 minutes** (Cybersecurity Insiders 2025, via [Vectra](https://www.vectra.ai/topics/alert-fatigue)). These are vendor figures, so present them as "industry surveys".

**Already exists:** Microsoft Security Copilot has alert-triage agents for Defender and Sentinel ([Microsoft](https://techcommunity.microsoft.com/t5/microsoft-defender-xdr-blog/security-copilot-in-defender-empowering-the-soc-with-assistive/ba-p/4503047)). **You are at the Microsoft auditorium, so expect this question.**

**Our gap**
- Kenya-specific fraud playbooks such as SIM swap followed by a login from a new device, then a bank-to-M-Pesa sweep, mule accounts and card-testing bursts.
- Fixed rules set the risk score, and the AI only explains and drafts. Containment needs an analyst's approval.
- Personal data is masked before it reaches any LLM. This matters because the Data Protection Regulations 2021 restrict sending personal data abroad, and a foreign-hosted AI raises exactly that problem ([Chambers](https://chambers.com/practice-guides/guides/cloud-computing-2026/kenya/trends-and-developments)).

**Theme fit**
- **Reuse:** the SIEM logs, threat-intelligence feeds and past case notes NCBA already has.
- **Automate:** looking up IP reputation, the user's login history, SIM-swap status and similar past alerts.
- **Reduce:** triage time (show the before and after in the demo) and how long fraud sits undetected.
- **Eliminate:** duplicate alerts, obvious false positives and copy-paste case writing.

**Demo, 4 screens**
1. An alert queue with 40 raw alerts grouped into 6 incidents.
2. One incident shown with a risk score of 87/100 and the reasons: SIM swap 2 hours ago, a new device, and 3 transfers to M-Pesa.
3. The evidence the agent gathered automatically, laid out on a timeline.
4. The **aha moment:** a drafted case report plus a "Lock account?" button the analyst must approve. Show the triage time drop from about 60 minutes to about 3.

**Stack:** FastAPI, a React dashboard, mock SIEM JSON and an LLM that writes the explanation only.

## #6 Data-Driven Procurement & Vendor Cost Optimization (BACKUP)
**Evidence**
- Duplicate and erroneous payments are **0.8–2% of disbursements** (APQC, via [Corpay](https://www.corpay.com/resources/blog/duplicate-payment-detection)).
- A 2026 analysis of 481m invoices found average leakage of **0.35% of spend** ([CFOtech/Xelix](https://cfotech.co.uk/story/xelix-warns-ap-errors-leak-up-to-usd-53-billion-a-year)).
- Duplicate payments were **18% of overpayment losses** ([apexanalytix](https://www.sdcexec.com/sourcing-procurement/financial-management-software/news/22967818/apexanalytix-duplicate-payments-pricing-discrepancies-and-payments-of-cancelled-invoices-remain-top-causes-for-overpayment)).
- **53% of SaaS licences go unused or underused** ([Zylo 2025](https://zylo.com/news/2025-saas-management-index)).
- A CBK survey found **26% of banks can't continuously monitor their third-party vendors**, and vendor contracts are weak ([The Star](https://www.the-star.co.ke/business/kenya/2025-08-08-banks-exposed-by-poorly-drafted-tech-vendor-contracts-cbk-warns), [Eastleigh Voice](https://eastleighvoice.co.ke/cyber%20security/193031/kenyan-banks-tighten-oversight-of-third-party-tech-firms-amid-rising-cyber-threats)). CBK's draft third-party guidance closed for comment on 7 Nov 2026 ([DPA](https://digitalpolicyalert.org/event/43734-central-bank-of-kenya-closes-consultation-on-the-draft-guidance-note-on-third-party-technology-service-providers)), so this is very current.

**Angle:** a "Spend Leak Finder". Upload invoices, contracts and licence lists. It flags duplicates, overlapping vendors, auto-renewals coming up, price jumps and unused seats. It totals **KES recoverable** and drafts the email to each vendor.
- The new hook is **third-party risk**: each vendor also gets a risk flag, for example "contract has no data-protection clause". That turns a cost tool into a compliance tool, in line with the new CBK guidance.

**Theme fit**
- **Reuse:** existing ERP and accounts-payable data.
- **Automate:** matching invoices and checking contracts.
- **Reduce:** avoidable spend.
- **Eliminate:** duplicate vendors and payments.

**Aha moment:** "KES 41.2m recoverable found in 12 seconds." Use fake data and label it as illustrative.

**Buildability: easiest of all.** A CSV, pandas rules, an LLM to read contract clauses and one dashboard.

## #2 Intelligent Cloud & IT Cost Optimizer
- Cloud waste is about **27% of IaaS/PaaS spend (2025)**, rising to **29% in 2026**, the first increase in five years ([Flexera](https://www.flexera.com/about-us/press-center/flexera-finds-cloud-value-is-rising-while-ai-waste-grows)).
- Unused SaaS licences run at 46–53% (Zylo).
- **Caveat:** CBK treats moving core banking, payments or customer data to the cloud as *material outsourcing* that requires notifying CBK ([Chambers](https://chambers.com/practice-guides/guides/cloud-computing-2026/kenya/law-and-practice)). NCBA is likely to be mostly on its own servers or hybrid, so focus on **licences (Microsoft 365, Oracle, etc.) and idle servers**, not only cloud.
- This overlaps heavily with #6. If you choose #6, fold the licence analysis in as one tab.

## #5 Intelligent Customer Self-Service
- **This space is crowded.** NCBA already has a WhatsApp channel and a chatbot (both sets of terms dated Feb 2025, [NCBA](https://ncbagroup.com/wp-content/uploads/sites/2/securepdfs/2025/02/Chat-Bot-Terms-and-Conditions.pdf)). Equity has EVA, Absa has Abby, and Craft Silicon offers "Small Talk" voice AI in local languages ([Kenyan Wall Street](https://kenyanwallstreet.com/the-rise-of-conversational-ai-in-kenyas-banks), [Standard](https://www.standardmedia.co.ke/business/sci-tech/article/2001524058/craft-silicon-banks-on-small-talk-ai-to-offer-voice-powered-financial-assistance-in-local-languages)).
- In a 2025 KBA survey, 1 in 5 customers said complaints are only *sometimes* resolved within 2 days ([KBA](https://www.kba.co.ke/?p=78980)).
- **The only way to stand out is to complete the request rather than answer FAQs**, with OTP-confirmed actions. An example is during an M-Shwari outage like 30–31 Oct 2025 ([Star](https://www.the-star.co.ke/news/2025-10-31-m-shwari-service-temporarily-unavailable)): the bot proactively says "known issue, ETA X" and stops a flood of calls. That's a good *Eliminate* story, but it's still risky.

## #1 AI-Powered IT Service Desk
- Password resets are **20–50% of help-desk calls** (Gartner, via [GCN](https://gcn.com/?p=23078)). That's about **$20 per L1 ticket** (MetricNet 2024) versus **$1–4 for automated self-service** ([ScreenMeet](https://www.screenmeet.com/blog/it-help-desk-cost-per-ticket-benchmarks)).
- It's the easiest to build, but it reads as "another chatbot", and Microsoft Copilot and ServiceNow already do it.
- **Differentiators:**
  - The agent actually performs the action, such as a password reset after MFA or an access request routed to the line manager for approval.
  - It clusters 30 "Outlook is down" tickets into one incident.

## #4 Smart Network & Infrastructure Optimization
- There's real pain: the M-Shwari outage on 30–31 Oct 2025 and a Fuliza disruption on 30 Sep 2025 ([TechTrendsKE](https://techtrendske.co.ke/2025/11/01/safaricom-m-shwari-outage-kenya-digital-fragility/), [People Daily](https://peopledaily.digital/business/safaricom-confirms-m-shwari-outage-leaving-customers-stranded)).
- **Hardest to fake believably.** You'd need network telemetry, the judges will include network engineers, and our team has no network background. **Skip it.**

## Compliance points for any pitch
- **Data Protection Act 2019 and Regulations 2021:** mask personal data before it reaches the LLM, keep data in Kenya, and limit processing to its stated purpose.
- **CBK outsourcing guideline and the draft third-party guidance:** any AI vendor is a third party, so plan for audit logs and an exit clause.
- **Keep a human in the loop for any action that changes accounts or money.**

## Likely judge questions (for #3)
1. *"Microsoft Security Copilot already does this. Why you?"*
   - It's Kenya-specific: SIM swap, M-Pesa sweeps and mule-account playbooks.
   - Fixed rules make the decision, so it can be audited.
   - Personal data is masked before any AI sees it, which keeps NCBA on the right side of the data-protection rules.
   - It sits on top of Sentinel rather than replacing it.
2. *"What if the AI is wrong?"*
   - The AI never decides. Rules set the score, the AI explains it, and an analyst approves every containment action.
   - Every step is logged.
3. *"How does it pay back?"*
   - Analyst hours saved per alert.
   - Faster detection, against KES 1.9bn of industry fraud losses with only 7% recovered.
   - Fewer false-positive escalations.
