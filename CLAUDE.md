# LeakLens: shared instructions for every teammate's Claude

You are one of **3 Claude sessions** building LeakLens together for the NCBA FinTech Hackathon. Each session belongs to a different teammate. You can't talk to the other two Claudes. **The only way to communicate is through this repo**: `CONTRACT.md` (interfaces), `STATUS.md` (progress board) and git.

## What we're building
LeakLens is a spend-leak finder for NCBA procurement, built for challenge #6: Data-Driven Procurement & Vendor Cost Optimization. The theme is **Reuse, Automate, Reduce, Eliminate**.
- Fixed rules (pandas) **decide** what counts as a leak.
- The LLM only **explains** findings, drafts vendor emails and extracts contract clauses.
- A human approves every action.
- Full plan: `docs/SOLUTION.md`. Research and sources: `docs/RESEARCH.md`.

## Rules for every session
1. **Read `CONTRACT.md` first.** File names, columns and JSON shapes there are FROZEN. Don't change them without the whole team agreeing out loud; if they change, update CONTRACT.md in the same commit.
2. **Only edit the files your person owns** (see `tasks/`). Touching another person's file causes merge conflicts.
3. **Before you start and before every push:** `git pull --rebase`.
4. **Commit small and often.** Push at least every 30 minutes, even if it's not perfect. Other people need your output.
5. **Update `STATUS.md`** with your own row only, in the same commit: what's done, what's next, any blockers.
6. **If you're blocked waiting on another person's output, use the files in `sample/`.** Never wait.
7. **The demo must never depend on the network.** All LLM output is cached in `cache/`. A live call runs only if `ANTHROPIC_API_KEY` is set, and it falls back to the cache if the call fails.
8. Use Python 3.11+, keep requirements in `requirements.txt` only, and use **no database**. Everything is CSV or JSON files.
9. Data is fake. Never put real NCBA, customer or personal data in the repo.

## Run
```
pip install -r requirements.txt
python generate_data.py        # Person 1 → data/
python detectors.py            # Person 2 → out/findings.json
streamlit run app.py           # Person 3
```
