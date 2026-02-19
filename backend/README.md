# Operational Intelligence Backend

AI-powered operational insights engine that analyzes Jira-style tickets.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Server runs on `http://localhost:8000`

## Endpoints

| Method | Path | Description |
|--------|------|--------------|
| GET | `/` | Service status |
| GET | `/tickets` | Raw demo tickets (80-120) |
| GET | `/insights` | AI-processed insights with clusters and change tracking |
| GET | `/cluster/{id}` | Single cluster detail for drill-down |
| POST | `/jira-draft/{id}` | Generate Jira draft (no real integration) |

## Features

- Generates 80-120 realistic demo tickets with recurring patterns
- sentence-transformers for semantic embeddings
- DBSCAN clustering for issue grouping
- Impact scoring (frequency + severity + recurrence)
- Actionable insights (recommended_action, priority, owner_team, etc.)
- Ownership mapping (workflow → team)
- Change tracking (last 7d vs previous 7d)
- Jira draft simulation
