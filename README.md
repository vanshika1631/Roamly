# ✈ Roamly (EmotiTrip AI) — Windows Setup Guide

Emotionally-aware travel planner. FastAPI · SQLAlchemy · Neon · Groq · React.

---

## Prerequisites

Make sure you have these installed before starting:

- **Python 3.12** via Anaconda — [anaconda.com](https://anaconda.com)
- **Node.js 20+** — [nodejs.org](https://nodejs.org)
- **Docker Desktop** — [docker.com](https://www.docker.com/products/docker-desktop)
- **Git** — [git-scm.com](https://git-scm.com)

---

## API Keys You Need

| Key | Where to get it | When you need it |
|---|---|---|
| `GROQ_API_KEY` | console.groq.com → API Keys | Now (Phase 0) |
| `DATABASE_URL` | neon.tech → Connection string | Phase 1 |
| `REDIS_URL` | upstash.com → Redis → Connect | Phase 2 |
| `GOOGLE_PLACES_API_KEY` | console.cloud.google.com | Phase 3 |
| `AMADEUS_CLIENT_ID/SECRET` | developers.amadeus.com | Phase 2 |
| `MAPBOX_PUBLIC_TOKEN` | mapbox.com → Tokens | Phase 4 |
| `OPENWEATHER_API_KEY` | openweathermap.org → API Keys | Phase 4 |
| `SECRET_KEY` | Generate locally (see below) | Phase 5 |

Generate SECRET_KEY:
```cmd
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## One-Time Environment Setup

```cmd
conda create -n roamly python=3.12
conda activate roamly
```

> Always run `conda activate roamly` before working on the project.

---

## Phase 0 — Validation Spike

Proves the core concept before building anything else.

```cmd
cd roamly\backend
conda activate roamly
python -m venv .venv
.venv\Scripts\activate
pip install groq.venv\Scripts\activate
set GROQ_API_KEY=gsk_...your_key...
python spike.py
```

**Expected output:** Two itineraries for Lisbon — one quiet and restorative, one vibrant and celebratory. If they feel meaningfully different, proceed to Phase 1.

---

## Phase 1 — Full Backend Setup

### 1. Create your .env file

In the `backend` folder, create a new file called `.env` (copy from `.env.example`):

```cmd
cd roamly\backend
copy .env.example .env
```

Then open `.env` and fill in at minimum:
```
GROQ_API_KEY=gsk_...
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
SECRET_KEY=your_generated_secret
```

### 2. Install backend dependencies

```cmd
cd roamly\backend
conda activate roamly
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start Docker (Postgres + Redis)

```cmd
docker-compose up -d
```

Verify it's running:
```cmd
docker-compose ps
```

Stop when done:
```cmd
docker-compose down
```

### 4. Run database migrations

```cmd
alembic upgrade head
```

### 5. Start the FastAPI server

```cmd
uvicorn app.main:app --reload --port 8000
```

API docs available at: **http://localhost:8000/docs**

### 6. Start the ARQ worker (separate terminal)

```cmd
conda activate roamly
cd roamly\backend
.venv\Scripts\activate
arq app.worker.WorkerSettings
```

---

## Phase 4 — Frontend Setup

```cmd
cd roamly\frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## Running Everything Together

You need **3 terminals** open simultaneously:

| Terminal | Command | What it does |
|---|---|---|
| 1 | `uvicorn app.main:app --reload --port 8000` | FastAPI server |
| 2 | `arq app.worker.WorkerSettings` | Background job worker |
| 3 | `npm run dev` (in frontend/) | React dev server |

---

## Running Tests

```cmd
cd roamly\backend
pytest tests/ -v
```

---

## Common Windows Issues

**`source` is not recognized**
Use `.venv\Scripts\activate` instead of `source .venv/bin/activate`

**`cp` is not recognized**
Use `copy` instead of `cp`

**Port already in use**
```cmd
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```

**Conda environment not activating in terminal**
Run this once:
```cmd
conda init cmd.exe
```
Then restart your terminal.

**Docker not starting**
Make sure Docker Desktop is running in the system tray before running `docker-compose up -d`

---

## Project Structure

```
roamly/
├── frontend/                   React 18 + Vite + TypeScript + Tailwind
├── backend/
│   ├── spike.py                Phase 0 — run this first
│   ├── .env                    Your API keys (never commit this)
│   ├── .env.example            Template for .env
│   ├── requirements.txt        Python dependencies
│   ├── app/
│   │   ├── main.py             FastAPI app entry point
│   │   ├── config.py           Reads .env via pydantic-settings
│   │   ├── worker.py           ARQ background job definitions
│   │   ├── routers/            API route handlers
│   │   │   ├── intake.py       /api/intake/*
│   │   │   ├── trips.py        /api/trips/*
│   │   │   └── profile.py      /api/profile/*
│   │   ├── modules/
│   │   │   ├── profiler/       TEB generation via Groq
│   │   │   ├── solver/         OR-Tools constraint model
│   │   │   ├── generator/      Itinerary generation via Groq
│   │   │   └── auditor/        Bias audit + explainability
│   │   ├── db/
│   │   │   ├── models.py       SQLAlchemy ORM models
│   │   │   ├── session.py      Async DB session
│   │   │   └── migrations/     Alembic migration scripts
│   │   └── schemas/            Pydantic models (TEB, Trip, Itinerary)
│   └── tests/
├── docker-compose.yml          Local Postgres + Redis
└── README.md                   This file
```

---

## Build Phases

| Phase | Weeks | Focus |
|---|---|---|
| Phase 0 | Day 1-3 | ✅ Validation spike — proves the concept |
| Phase 1 | Wk 1-2 | FastAPI + emotional profiler + TEB → DB |
| Phase 2 | Wk 3-4 | OR-Tools + ARQ worker + itinerary generation |
| Phase 3 | Wk 5 | Bias auditor + explainability |
| Phase 4 | Wk 6-7 | React frontend |
| Phase 5 | Wk 8 | Polish + deploy |