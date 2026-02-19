# Operational Intelligence Dashboard

AI-powered operational command center that analyzes simulated Jira tickets and converts operational noise into actionable decision insights for product managers.

**AI → Analysis → Prioritization → Action**

## Architecture

- **Backend:** Python FastAPI (`backend/`)
- **Frontend:** React + Vite + Tailwind CSS (`src/`)
- **Charts:** Recharts

## Quick Start

No setup required. Start backend, then frontend.

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Server runs on **http://localhost:8000**. On startup it:
- Generates 80–120 Jira-style demo tickets
- Runs the AI pipeline (embeddings, clustering, impact scoring)
- Caches insights for instant dashboard load

### 2. Frontend

```bash
npm install
npm run dev
```

Dashboard runs on **http://localhost:5173**.

## Features

### Backend

| Feature | Description |
|--------|-------------|
| Demo ticket generator | 80–120 tickets with recurring patterns (reviewer failures, submission bugs, dashboard perf, timeouts, release regressions, infra, backlog spikes) |
| AI pipeline | sentence-transformers embeddings → DBSCAN clustering → impact scoring (frequency + severity + recurrence) |
| Actionable insights | `recommended_action`, `priority_level` (P1–P4), `owner_team`, `business_impact`, `urgency_tag`, `risk_score`, `recurrence_signal` |
| Ownership mapping | submission → Backend Team, review → Platform Team, dashboard → Frontend Team, release → Release Engineering, infra → DevOps |
| Change tracking | Last 7 days vs previous 7 days: `trend_direction`, `delta_percent`, `stability_index` |
| Jira draft simulation | `POST /jira-draft/{id}` generates structured draft (summary, priority, impact, examples, recommended action, owner) — no real Jira integration |

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tickets` | Raw demo tickets |
| GET | `/insights` | AI-processed insights with clusters |
| GET | `/cluster/{id}` | Single cluster detail |
| POST | `/jira-draft/{id}` | Generate Jira draft for a cluster |

### Frontend

| Feature | Description |
|--------|-------------|
| Top metrics | Total incidents, top issue, risk score, stability index, trend direction |
| Charts | Incidents over time, cluster distribution, severity breakdown, workflow ownership |
| Cluster action cards | Priority badge, owner team, impact score, urgency tag, summary, recommended action, example tickets |
| Priority sort toggle | Sort by frequency, severity, impact, recurrence, priority |
| Drill-down | Click “Details” to open cluster detail panel (timeline, severity, examples, AI explanation, ownership, priority reasoning) |
| Jira modal | “Create Jira Issue” opens preview of structured draft |

## Tech Stack

- **Backend:** FastAPI, sentence-transformers, scikit-learn, pandas, numpy
- **Frontend:** React, Vite, Tailwind CSS, Recharts, lucide-react

## Project Layout

```
ai-poc/
├── backend/
│   ├── main.py           # FastAPI app, endpoints
│   ├── ai_processor.py   # Embeddings, clustering, insights
│   ├── ticket_generator.py
│   └── requirements.txt
├── src/
│   ├── App.tsx
│   ├── services/api.ts
│   └── components/
│       ├── MetricCard.tsx
│       ├── TrendChart.tsx
│       ├── SeverityChart.tsx
│       ├── WorkflowChart.tsx
│       ├── ClusterDistributionChart.tsx
│       ├── ClusterPanel.tsx
│       ├── ClusterDetailPanel.tsx
│       ├── JiraModal.tsx
│       └── ExecutiveSummary.tsx
└── README.md
```
