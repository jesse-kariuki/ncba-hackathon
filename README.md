# LeakLens: NCBA FinTech Hackathon (Challenge #6, Procurement & Vendor Cost)

> LeakLens finds the money NCBA leaks to duplicate invoices, overlapping vendors, idle licences and risky contracts. **Rules decide, AI explains, and a person approves.**

## Team: 3 people, each running Claude Code
| | Role | Brief |
|---|---|---|
| **P1** | Fake data, contract extraction, pitch deck, backup video | [tasks/P1-data-contracts-pitch.md](tasks/P1-data-contracts-pitch.md) |
| **P2** | Detection engine and integrator | [tasks/P2-detection-engine.md](tasks/P2-detection-engine.md) |
| **P3** | Streamlit app, AI explanations, live demo | [tasks/P3-app-ai.md](tasks/P3-app-ai.md) |

## How the three Claudes work together
They can't talk to each other directly. They coordinate through this repo:
- **`CLAUDE.md`**: shared rules. Claude Code reads it automatically when started in this folder.
- **`CONTRACT.md`**: frozen file formats, so all three can build at the same time.
- **`STATUS.md`**: the progress board. Each Claude updates its own row on every push.
- **`sample/`**: stand-in data, so nobody waits on anybody.

## Start (each person)
```
git clone https://github.com/jesse-kariuki/ncba-hackathon.git
cd ncba-hackathon
pip install -r requirements.txt
claude
```
Then paste the prompt from your task file.

## Run the full demo
```
python generate_data.py && python detectors.py && streamlit run app.py
```

## Pitch
Slides outline, script and judge Q&A: [PITCH.md](PITCH.md). Claude Design brief, logo and splash: [design/](design/)

## Full website (Next.js + FastAPI)
```
uvicorn backend.main:app --port 8000
cd frontend && npm install && npm run dev   # http://localhost:3000
```

## Docs
- [docs/SOLUTION.md](docs/SOLUTION.md): the full solution, demo flow and judge Q&A
- [docs/RESEARCH.md](docs/RESEARCH.md): research on all 6 challenges, with sources
