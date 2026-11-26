# STATUS: ONE HOUR LEFT. The plan has changed.

**The app is DONE and pushed:** data generator, rules engine (22/22 planted leaks found, 0 false positives, KES 56.0m), and the Streamlit app with approvals and an audit log.
**Nobody builds new features now.** Everyone pulls, runs it, and works on the PITCH.

```
git pull
pip install -r requirements.txt
streamlit run app.py
```
`out/findings.json` is committed, so the app works without regenerating.

| Who | Next 40 minutes | Done? |
|---|---|---|
| **Person 1: slides** | Build the 7-slide deck from tasks/P1 section 3 and docs/SOLUTION.md (Canva or Google Slides). Use the headline numbers from the app. | |
| **Person 2: demo driver** | Run the app on the presenting laptop, rehearse the 3-minute click path in tasks/P3 ("Demo script"), then **record the backup video** of it on screen. | |
| **Person 3: script + Q&A** | Write the spoken script (hook → problem → demo → theme mapping → why NCBA → ask). Learn the 3 judge answers in docs/SOLUTION.md. Time the full run. | |

**Last 10 minutes:** a full rehearsal together, timed at 3 minutes.

**Optional, only if someone has an `ANTHROPIC_API_KEY`:** set it and run `python explain.py`. That fills `cache/explanations.json` with real Claude explanations. Commit it. Otherwise the template explanations are used.

## AI provider (optional): Claude OR Gemini
Set ONE key, **pre-warm the cache before the demo**, then commit `cache/explanations.json`:
```
# PowerShell
$env:GEMINI_API_KEY="..."        # or $env:ANTHROPIC_API_KEY="..."
python explain.py                # prints "gemini" / "claude" per finding
```
If both keys are set, pick one with `$env:LEAKLENS_PROVIDER="gemini"`. With no key, the app uses template explanations. The app labels each explanation as "AI · Gemini", "AI · Claude" or "template".
