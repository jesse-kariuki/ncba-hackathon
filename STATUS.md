# STATUS board (each person edits ONLY their own row and commits it with their work)

| Person | Owns | Done | Doing now | Blocked on |
|---|---|---|---|---|
| P1: Data + Contracts + Pitch | generate_data.py, extract_contracts.py, data/, PITCH.md | – | starting | – |
| P2: Detection engine (integrator) | detectors.py, test_detectors.py, out/findings.json | – | starting | – |
| P3: App + AI | app.py, explain.py, cache/ | – | starting | – |

## Checkpoints (everyone pulls and runs the full pipeline at each one)
- **T+45 min:** P1 pushes data v1. P2 switches from sample data to real data.
- **T+90 min:** P2 pushes findings.json v1. P3 switches from sample findings to real findings.
- **T+120 min:** **FEATURE FREEZE.** Only fixes after this. P1 records the backup demo video.
- **T+150 min:** rehearse the pitch twice, timed.
