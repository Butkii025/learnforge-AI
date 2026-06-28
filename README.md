<div align="center">

```
██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
██║     █████╗  ███████║██████╔╝██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
███████╗███████╗██║  ██║██║  ██║██║ ╚████║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
```

### Your AI-powered study agent for every software engineering student

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-Multi--Agent-4285F4?style=flat-square&logo=google&logoColor=white)](https://google.github.io/adk-docs/)
[![MCP](https://img.shields.io/badge/MCP-Server-6366F1?style=flat-square)](https://modelcontextprotocol.io)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white)](https://railway.app)
[![License](https://img.shields.io/badge/License-MIT-10B981?style=flat-square)](LICENSE)
[![Kaggle](https://img.shields.io/badge/Kaggle-Capstone%202026-20BEFF?style=flat-square&logo=kaggle&logoColor=white)](https://kaggle.com)

**[demo Video](#DemoVideo)**

</div>

---

## What is LearnForge?

LearnForge is a **multi-agent AI study system** built for software engineering students across four disciplines — CSE, IT, AI/ML, and Data Science. It runs entirely on your local machine using **Gemma 3 via Ollama** — no cloud API keys, no subscription, no internet required once set up.

You choose your engineering track. Four specialist AI agents — Tutor, Quiz, Planner, and Code Review — coordinate through an **orchestrator built with Google ADK** and access tools via a **local MCP server**. The result is a personalised, adaptive study companion that knows what you need to learn next.

---

## Table of Contents

- [Architecture](#architecture)
- [Agent system](#agent-system)
- [MCP server and tools](#mcp-server-and-tools)
- [Engineering tracks](#engineering-tracks)
- [Project structure](#project-structure)
- [Quick start](#quick-start)
- [Railway deployment](#railway-deployment)
- [Security](#security)
- [Tech stack](#tech-stack)
- [Screenshots](#screenshots)
- [demo Video](#DemoVideo)echo "# LearnForge-AI-2" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Butkii025/LearnForge-AI-2.git
git push -u origin main
- [Contributing](#contributing)
- [Developer](#developer)
---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STUDENT BROWSER                             │
│                    React 18 + Vite Frontend                         │
│         [Track Selector] [Tutor] [Quiz] [Planner] [Code Review]     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  REST + JWT
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                                │
│                                                                     │
│   ┌─────────────┐    ┌─────────────────────────────────────────┐   │
│   │  Security   │    │         ORCHESTRATOR AGENT (ADK)        │   │
│   │  Layer      │───▶│   Routes tasks · Manages state         │   │
│   │  JWT · Rate │    │   Coordinates specialist agents         │   │
│   │  Sanitizer  │    └────────────┬────────────────────────────┘   │
│   └─────────────┘                 │  delegates to                   │
│                          ┌────────┴────────┐                        │
│               ┌──────────▼──┐   ┌──────────▼──┐                    │
│               │ TutorAgent  │   │  QuizAgent  │                    │
│               │  (ADK)      │   │   (ADK)     │                    │
│               └──────────┬──┘   └──────────┬──┘                    │
│               ┌──────────▼──┐   ┌──────────▼──┐                    │
│               │PlannerAgent │   │ CodeReview  │                    │
│               │  (ADK)      │   │  Agent(ADK) │                    │
│               └──────────┬──┘   └──────────┬──┘                    │
│                          └────────┬─────────┘                       │
│                                   ▼                                 │
│                   ┌───────────────────────────────┐                 │
│                   │       LOCAL MCP SERVER        │                 │
│                   │  search_arxiv · run_code      │                 │
│                   │  get_progress · gen_quiz      │                 │
│                   │  get_concept_graph            │                 │
│                   └───────────────────────────────┘                 │
│                                   │                                 │
│              ┌────────────────────┼────────────────────┐            │
│              ▼                    ▼                    ▼            │
│         ┌─────────┐         ┌──────────┐        ┌──────────┐       │
│         │ arXiv   │         │ Sandbox  │        │ SQLite   │       │
│         │  API    │         │  Python  │        │   DB     │       │
│         └─────────┘         └──────────┘        └──────────┘       │
│                                                                     │
│                    ┌─────────────────────┐                          │
│                    │  Gemma 3 via Ollama │                          │
│                    │  (runs fully local) │                          │
│                    └─────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Data flow

```
Student input
     │
     ▼
[Security layer] ── sanitise · validate · rate-limit · JWT verify
     │
     ▼
[Orchestrator] ── classify intent ── route to specialist agent
     │
     ├─── "explain X"      ──▶  TutorAgent      ──▶ MCP: search_arxiv
     ├─── "quiz me on X"   ──▶  QuizAgent       ──▶ MCP: generate_quiz + get_progress
     ├─── "plan my week"   ──▶  PlannerAgent     ──▶ MCP: get_progress + concept_graph
     └─── "review my code" ──▶  CodeReviewAgent  ──▶ MCP: run_code_sandbox
                                      │
                                      ▼
                              [Gemma 3 / Ollama]
                                      │
                                      ▼
                              Response streamed back to React UI
```

---

## Agent system

LearnForge uses **Google ADK** to build a true multi-agent hierarchy. The orchestrator receives every student request, classifies intent, and delegates to the right specialist.

```
OrchestratorAgent
├── TutorAgent
│   ├── Explains concepts with intuition → key points → examples
│   ├── Adapts depth to student track and self-reported level
│   └── Uses: search_arxiv tool for recent papers
│
├── QuizAgent
│   ├── Generates adaptive 4-option MCQs (beginner / intermediate / advanced)
│   ├── Tracks wrong answers in SQLite for spaced repetition
│   └── Uses: generate_quiz + get_progress tools
│
├── PlannerAgent
│   ├── Builds 7-day and 30-day study roadmaps per track
│   ├── Adjusts plan dynamically based on quiz performance
│   └── Uses: get_progress + get_concept_graph tools
│
└── CodeReviewAgent
    ├── Reviews Python, JavaScript, and SQL code
    ├── Returns: correctness · style · time complexity · suggested fix
    └── Uses: run_code_sandbox tool (actual execution + real output)
```

### Agent communication pattern

```
Student: "Quiz me on transformers, I'm intermediate level"
         │
         ▼
OrchestratorAgent classifies → { intent: "quiz", topic: "transformers", level: "intermediate" }
         │
         ▼
QuizAgent.run(topic="transformers", level="intermediate")
         │
         ├── calls MCP: get_progress(student_id) → weak subtopics
         ├── calls MCP: generate_quiz(topic, level, weak_areas)
         │                    │
         │                    ▼
         │             Gemma 3 generates 5 MCQs
         │
         └── returns structured quiz JSON → React UI renders it
```

---

## MCP server and tools

The local MCP server runs as a separate process and exposes tools that all agents share.

```
MCP Server (localhost:8001)
│
├── search_arxiv(query: str, max_results: int)
│       Searches arXiv for recent papers, returns title + abstract + URL
│       Used by: TutorAgent (finding latest research on topics)
│
├── run_code_sandbox(code: str, language: str, timeout: int)
│       Executes code in a subprocess with strict resource limits
│       Returns: stdout, stderr, exit code, execution time
│       Used by: CodeReviewAgent (running student code safely)
│
├── get_student_progress(student_id: str)
│       Reads quiz history, accuracy per topic, streak from SQLite
│       Returns: JSON progress object
│       Used by: QuizAgent, PlannerAgent
│
├── generate_quiz(topic: str, level: str, weak_areas: list)
│       Sends structured prompt to Gemma 3 via Ollama
│       Returns: list of MCQ objects with options and explanations
│       Used by: QuizAgent
│
└── get_concept_graph(topic: str, track: str)
        Returns topic dependency map (what to learn before X)
        Used by: PlannerAgent (building logical study order)
```

### Sandbox security model

```
run_code_sandbox
        │
        ▼
subprocess.Popen(
  ["python", "-c", code],
  timeout=10,              ← hard kill after 10 seconds
  cwd="/tmp/sandbox",      ← isolated working directory
  env={},                  ← no environment variables passed
  preexec_fn=set_limits    ← ulimit: 64MB RAM, no network, no file writes
)
```

---

## Engineering tracks

LearnForge adapts its entire content — quiz bank, tutor knowledge, planner goals, and concept graph — based on the student's chosen track.

```
┌──────────────────────────────────────────────────────────────────┐
│                        TRACK SELECTOR                            │
│                                                                  │
│   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────┐  │
│   │    CSE    │  │    IT     │  │   AI/ML   │  │    Data    │  │
│   │           │  │           │  │           │  │  Science   │  │
│   │ DS & Algo │  │ Networks  │  │ ML Theory │  │ Statistics │  │
│   │ OS · DBMS │  │ Cyber Sec │  │Deep Learn │  │ Pandas·SQL │  │
│   │ Networks  │  │ Cloud/Dev │  │ NLP · LLM │  │ EDA · Viz  │  │
│   │ Sys Design│  │ Linux·SRE │  │ MLOps     │  │ Feature Eng│  │
│   └───────────┘  └───────────┘  └───────────┘  └────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

Each track maps to:
- A curated **topic list** shown in the sidebar
- A **quiz bank** tuned to that discipline's exam patterns
- A **concept dependency graph** for logical study ordering
- **Study plan templates** with realistic weekly hour targets
- **Tutor persona** calibrated to the vocabulary of that field

---

## Project structure

```
learnforge/
│
├── backend/                        Python + FastAPI
│   ├── agents/
│   │   ├── orchestrator.py         Root ADK agent — routes all requests
│   │   ├── tutor_agent.py          Explains concepts via Gemma 3
│   │   ├── quiz_agent.py           Generates and evaluates MCQs
│   │   ├── planner_agent.py        Builds personalised roadmaps
│   │   └── code_review_agent.py    Reviews code with sandbox execution
│   │
│   ├── mcp/
│   │   ├── server.py               MCP server entry point (port 8001)
│   │   └── tools/
│   │       ├── arxiv_tool.py       arXiv paper search
│   │       ├── sandbox_tool.py     Safe Python execution
│   │       ├── progress_tool.py    SQLite read/write
│   │       └── quiz_tool.py        MCQ generation via local LLM
│   │
│   ├── security/
│   │   ├── auth.py                 JWT issue + verify (python-jose)
│   │   ├── sanitizer.py            Prompt injection detection + strip
│   │   └── rate_limiter.py         slowapi per-route limits
│   │
│   ├── db/
│   │   ├── models.py               SQLAlchemy ORM models
│   │   └── migrations/             Alembic migration scripts
│   │
│   ├── api/
│   │   └── routes.py               FastAPI route definitions
│   │
│   ├── main.py                     App entry — mounts routes, CORS, middleware
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                       React 18 + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx         Collapsible nav with track-aware topics
│   │   │   ├── TopBar.jsx          Model status, user info, notifications
│   │   │   ├── TrackSelector.jsx   CSE / IT / AI/ML / DS switcher
│   │   │   ├── HomeDashboard.jsx   Landing — project info + stats + agents
│   │   │   ├── TutorChat.jsx       Multi-turn chat with streaming response
│   │   │   ├── QuizMode.jsx        Adaptive MCQ with instant feedback
│   │   │   ├── StudyPlanner.jsx    Weekly/monthly roadmap view
│   │   │   ├── CodeReview.jsx      Monaco editor + agent feedback panel
│   │   │   └── Analytics.jsx       Progress charts (Recharts)
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAgent.js         Calls orchestrator API, handles streaming
│   │   │   └── useProgress.js      Reads and updates student progress
│   │   │
│   │   ├── api/
│   │   │   └── client.js           Axios instance with JWT interceptor
│   │   │
│   │   ├── App.jsx                 Router + track context provider
│   │   └── main.jsx
│   │
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── cli/
│   ├── learnforge_cli.py           Agents CLI skill (4 commands)
│   └── setup.py                    pip-installable CLI package
│
├── .github/
│   └── workflows/
│       └── deploy.yml              CI: test → build → push to Railway
│
├── railway.toml                    Railway service config
├── docker-compose.yml              Local: frontend + backend + ollama
├── .env.example                    Required environment variables
└── README.md
```

---

## Quick start

### Prerequisites

- [Docker Desktop](https://docker.com) 24+
- [Ollama](https://ollama.ai) installed locally
- Git

### 1. Clone and configure

```bash
git clone https://github.com/yourusername/learnforge.git
cd learnforge
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-super-secret-key-here
OLLAMA_HOST=http://host.docker.internal:11434
DATABASE_URL=sqlite:///./db/progress.db
CORS_ORIGINS=http://localhost:3000
```

### 2. Pull the local model

```bash
ollama pull gemma3
```

### 3. Run everything

```bash
docker compose up
```

That's it. Open **http://localhost:3000**

```
docker compose up
│
├── pulls backend image   → FastAPI on :8000
├── pulls frontend image  → React on :3000
└── starts MCP server     → MCP on :8001
     │
     └── all connect to Ollama running natively on your machine
```

### 4. Optional — install the CLI skill

```bash
pip install -e ./cli
learnforge --help
```

```
Usage: learnforge [OPTIONS] COMMAND

Commands:
  study   Explain a topic with examples
  quiz    Take an adaptive MCQ session
  plan    Generate a personalised study roadmap
  review  Get AI feedback on your code file

Examples:
  learnforge study --topic "transformer attention" --track aiml
  learnforge quiz  --topic "backpropagation" --difficulty hard
  learnforge plan  --goal "master MLOps in 30 days" --track aiml
  learnforge review --file model.py
```

---

## Railway deployment

LearnForge deploys as **two Railway services** connected to the same repo.

```
GitHub main branch
        │
        │ push triggers
        ▼
GitHub Actions CI
        │
        ├── run tests (pytest + vitest)
        ├── build Docker image (backend)
        └── trigger Railway deploy
                │
                ├── Service 1: Backend
                │   Dockerfile: backend/Dockerfile
                │
                └── Service 2: Frontend
                    Build: npm run build → /dist
                    Serve: railway static site
```
---

## Security

LearnForge implements four layers of security:

```
Incoming request
       │
       ▼
┌─────────────────────────────────────────────┐
│  1. RATE LIMITING (slowapi)                 │
│     /api/chat     → 20 req/min per IP       │
│     /api/quiz     → 30 req/min per IP       │
│     /api/auth     → 5 req/min per IP        │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  2. JWT AUTHENTICATION (python-jose)        │
│     Bearer token required on all /api/*     │
│     Token expires: 24 hours                 │
│     Refresh token: 7 days                   │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  3. PROMPT INJECTION GUARD (sanitizer.py)   │
│     Strips: "ignore previous instructions"  │
│     Strips: system prompt override patterns │
│     Strips: jailbreak templates             │
│     Max input length: 4000 characters       │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  4. SANDBOXED CODE EXECUTION                │
│     Subprocess with: timeout=10s            │
│     ulimit: 64MB RAM · no network           │
│     Isolated /tmp/sandbox directory         │
│     Blocked: os · subprocess · open()       │
└─────────────────────────────────────────────┘
```

---

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| LLM | Gemma 3 via Ollama | Runs fully locally — no API key, no cost, no internet |
| Agent framework | Google ADK | Course requirement — orchestrator + specialist agent pattern |
| Tool protocol | MCP (Python SDK) | Course requirement — exposes tools to all agents cleanly |
| Backend | FastAPI + Python 3.11 | Async, typed, fast — ideal for streaming agent responses |
| Frontend | React 18 + Vite | Fast HMR in dev, tiny prod bundle, component-based UI |
| Styling | Tailwind CSS | Utility-first, no CSS file maintenance |
| Database | SQLite + SQLAlchemy | Zero config, ships in the container, persistent progress |
| Auth | python-jose + JWT | Stateless, Railway-compatible, standard |
| Deployment | Railway.app | GitHub auto-deploy, free tier, two services |
| CI | GitHub Actions | Auto-test and deploy on every push to main |
| CLI | Python + argparse | Agents CLI skill — course requirement |

---

## How it satisfies the competition rubric

```
Innovation ──────────────────────────────────────────── ✓
  Multi-track system serving 4 engineering disciplines.
  No other submission personalises content by student major.
  Code review agent with actual sandbox execution is unique.

Solution value ──────────────────────────────────────── ✓
  Addresses a real pain point: every CS student needs
  personalised help but can't afford tutors.
  Works offline — ideal for students with limited connectivity.

Technical implementation ────────────────────────────── ✓
  All 6 course concepts implemented with working code.
  Not a chatbot wrapper — a genuine multi-agent pipeline.
  MCP server provides clean tool abstraction across agents.

Demonstration ───────────────────────────────────────── ✓
  Video shows: track switching → tutor → quiz → CLI → deploy.
  Kaggle writeup maps every agent to course concepts.
  Public Railway URL for judges to try live.
```
---

## Screenshots

<img width="1200" height="673" alt="Screenshot 2026-06-26 024228" src="https://github.com/user-attachments/assets/0018bc69-bdef-432b-8670-e53e4c152e65" />

***

<img width="1251" height="535" alt="Screenshot 2026-06-26 195227" src="https://github.com/user-attachments/assets/c116c5f2-54ba-4ab4-ba5d-54a8eba04495" />

***

<img width="1460" height="519" alt="Screenshot 2026-06-26 195124" src="https://github.com/user-attachments/assets/8a0093e0-c7f5-4999-8dab-26cbcfe27be4" />

***

<img width="1270" height="457" alt="Screenshot 2026-06-26 194816" src="https://github.com/user-attachments/assets/9cac9b12-c2b1-4deb-b26d-88018b5d25aa" />

***
<img width="1242" height="438" alt="Screenshot 2026-06-26 195047" src="https://github.com/user-attachments/assets/983bd0fa-4463-4fe7-a12f-88bb90410f55" />

---

## DemoVideo

https://github.com/user-attachments/assets/1b1db7a2-c973-41da-bbc2-6c3a3a8b4470

---
## Contributing

Pull requests are welcome. For major changes, open an issue first.

```bash
# Development setup (no Docker needed)
cd backend && pip install -r requirements.txt && uvicorn main:app --reload
cd frontend && npm install && npm run dev
```

---

## Acknowledgements

- Google × Kaggle 5-Day AI Agents Intensive Course 2026
- Google ADK team for the agent framework
- Ollama project for making local LLMs accessible
- MCP SDK contributors

---

## Developer
* Priynashu Vijay
* 📝 License [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](/LICENSE)
#   L e a r n F o r g e - A I - 2  
 #   L e a r n F o r g e - A I - 2  
 #   L e a r n F o r g e  
 #   L e a r n F o r g e  
 