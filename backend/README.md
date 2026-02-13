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

- `GET /` - Service status
- `GET /insights` - AI-processed operational insights
- `GET /tickets` - Raw demo tickets

## Features

- Generates 100 realistic demo tickets with recurring patterns
- Uses Sentence Transformers for semantic embeddings
- DBSCAN clustering for issue grouping
- Trend detection and impact scoring
- Explainable AI summaries
