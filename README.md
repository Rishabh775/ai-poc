# Operational Intelligence Dashboard

AI-powered operational triage engine that analyzes simulated Jira tickets and converts operational noise into actionable decision insights for product managers.

**AI → Analysis → Prioritization → Action**

## Architecture

- **Backend:** Python FastAPI (`backend/`)
- **Frontend:** React + Vite + Tailwind CSS (`src/`)
- **Charts:** Recharts
- **AI:** Sentence Transformers, HDBSCAN (with DBSCAN fallback), NumPy

## Quick Start

No setup required. Start backend, then frontend.

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Server runs on **http://localhost:8000**. On startup it:
- Generates test tickets with real-world scenarios
- Runs the AI pipeline (hybrid clustering, embeddings, impact scoring)
- Caches insights for instant dashboard load
- Displays configuration and clustering results

### 2. Frontend

```bash
npm install
npm run dev
```

Dashboard runs on **http://localhost:5173**.

## Configuration

The system is configurable via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SIMILARITY_THRESHOLD` | 0.85 | Duplicate detection threshold (0.82-0.88) |
| `DBSCAN_EPS` | 0.32 | DBSCAN epsilon for clustering (DBSCAN fallback mode) |
| `MIN_SAMPLES` | 2 | Minimum samples for DBSCAN |
| `USE_HDBSCAN` | false | Set `true` to cluster with HDBSCAN instead (better for small datasets) |

For the small-ticket regime, HDBSCAN gives tighter topic clusters than DBSCAN's flat epsilon threshold; DBSCAN remains the default fallback when the `hdbscan` package isn't installed.

Example:
```bash
SIMILARITY_THRESHOLD=0.82 DBSCAN_EPS=0.35 python main.py
```

## Features

### Backend

| Feature | Description |
|---------|-------------|
| Test ticket generator | 25 real-world test cases across 8 categories |
| Text normalization | Lowercase, removes emails, manuscript IDs, strips whitespace |
| Hybrid clustering | Combines semantic embeddings + metadata (workflow_type, severity) |
| Semantic duplicate detection | Cosine similarity on embeddings, configurable threshold |
| Dynamic cluster assignment | Assigns new tickets to existing clusters based on centroid similarity |
| Cluster confidence scoring | Measures intra-cluster vs inter-cluster similarity |
| Per-cluster change tracking | Last 7 days vs previous 7 days: new, increasing, decreasing, resolved |
| Top keywords extraction | Most common terms in each cluster for explainability |
| Actionable insights | `recommended_action`, `priority_level` (P1–P4), `owner_team`, `business_impact`, `urgency_tag`, `risk_score`, `recurrence_signal` |
| Ownership mapping | submission → Backend Team, review → Platform Team, dashboard → Frontend Team, release → Release Engineering, infra → DevOps |
| Change tracking | Global: `trend_direction`, `delta_percent`, `stability_index` |
| Jira draft simulation | `POST /jira-draft/{id}` generates structured draft |

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info and config |
| GET | `/tickets` | Raw demo tickets |
| GET | `/insights` | AI-processed insights with clusters |
| GET | `/cluster/{id}` | Single cluster detail |
| GET | `/config` | Current system configuration |
| POST | `/check-duplicate` | Check if a ticket is a duplicate (title-only by default) |
| POST | `/assign-cluster` | Dynamically assign ticket to cluster |
| POST | `/jira-draft/{id}` | Generate Jira draft for a cluster |
| POST | `/tickets` | Manually add a new ticket (for testing) |

### Frontend

| Feature | Description |
|---------|-------------|
| Tab navigation | Overview, Check Duplicate, Cluster Changes, Cluster Confidence, All Tickets |
| Real-time suggestions | As you type in Check Duplicate, suggestions appear automatically |
| Top metrics | Total incidents, risk score, stability, trend, cluster count |
| Charts | Incidents over time, cluster distribution, severity breakdown, workflow ownership |
| Duplicate detection panel | Form to check for duplicate tickets with real-time similarity results |
| Cluster change tracker | Per-cluster trends (new, increasing, decreasing, resolved) |
| Cluster confidence panel | AI confidence scores for each cluster |
| All Tickets view | See every ticket with cluster assignment, filter by workflow/severity/cluster |
| Manual ticket creation | Add new tickets directly from the All Tickets panel for testing |
| Cluster action cards | Priority badge, owner team, impact score, confidence indicator |
| Priority sort toggle | Sort by frequency, severity, impact, recurrence, priority |
| Drill-down | Cluster detail panel with timeline, keywords, confidence, examples |
| Jira modal | "Create Jira Issue" opens preview of structured draft |

## Test Results - AI Grouping Validation

We tested the system with 25 real-world tickets across 8 categories to validate semantic clustering:

### Clustering Results

| Cluster | Count | Categories Found | Success Rate |
|---------|-------|------------------|---------------|
| 0 | 5 | **Reviewer Status** | 100% |
| 1 | 5 | Dashboard Performance (4), Configuration (1) | 80% |
| 2 | 5 | Timeout (4), Support (1) | 80% |
| 3 | 3 | **Release Regression** | 100% |
| None | 7 | Edge cases, short text, noise | Expected |

### Test Categories

```
Category A: Reviewer Status / Workflow State Mismatch
  - "Review completion state not updating"
  - "Reviewer stuck in incomplete state"  
  - "Status mismatch"
  → All 5 correctly clustered together (100%)

Category B: Dashboard Performance / Slowness  
  - "Analytics dashboard timing out"
  - "Performance degradation on metrics screen"
  - "Dashboard slow"
  → 4/5 clustered together (80%)

Category C: Timeout / System Errors
  - "Backend 504 error during submission"
  - "Review submission fails after 30s"
  - "Timeout on save"
  → 4/5 clustered together (80%)

Category D: Release Regression
  - "Feature working before deployment, now broken"
  - "Post-deploy regression in assignment workflow"
  → All 3 correctly clustered together (100%)
```

### Duplicate Detection Tests

| Test Input | Confidence | Result |
|------------|------------|--------|
| "Dashboard loads very slowly" | 88.3% | ✅ Duplicate found |
| "Getting 504 when submitting" | 86.0% | ✅ Duplicate found |
| "Review submitted but status shows draft" | 82.4% | ⚠️ Near threshold |

### Key Findings

1. **Semantic embeddings work**: Tickets with different wording but same meaning are grouped correctly
2. **Hybrid clustering helps**: Using workflow_type + severity as metadata improves accuracy
3. **Threshold tuning**: 0.85 is a good default, but edge cases may need lower threshold
4. **Short text is harder**: Very short titles ("Not working", "Please fix ASAP") are correctly left as noise

## Tech Stack

- **Backend:** FastAPI, sentence-transformers, scikit-learn, pandas, numpy
- **Frontend:** React, Vite, Tailwind CSS, Recharts, lucide-react

## Project Layout

```
ai-poc/
├── backend/
│   ├── main.py              # FastAPI app, endpoints
│   ├── ai_processor.py       # Embeddings, hybrid clustering, insights
│   ├── config.py            # Configuration from environment
│   ├── ticket_generator.py  # Real-world test tickets
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
│       ├── ExecutiveSummary.tsx
│       ├── DuplicateCheckPanel.tsx     # NEW: with real-time suggestions
│       ├── ClusterChangeTracker.tsx
│       ├── ClusterConfidencePanel.tsx
│       └── AllTicketsPanel.tsx        # NEW: view all tickets
└── README.md
```

## How It Works

### Hybrid Clustering

The system combines:
1. **Semantic embeddings** (384 dimensions from all-MiniLM-L6-v2)
2. **Metadata encoding** (5-dim one-hot workflow + 1-dim severity weight)

This makes clustering robust to:
- Different wordings (semantic similarity)
- Short tickets (metadata helps disambiguate)
- Slack-generated tickets (workflow context)

### Duplicate Detection

When checking for duplicates:
1. Generate embedding for the input ticket (title-only by default)
2. Compute cosine similarity against all existing embeddings
3. If max similarity > threshold (0.85), mark as duplicate
4. Return matched cluster and similar tickets

**Title-Only Search**: By default, duplicate search uses only the ticket title (not workflow type or severity), since users often don't remember those details. This makes it easier to find duplicates just by describing the issue.

### Real-time Suggestions

As users type in the Check Duplicate panel:
- Debounced API calls (500ms delay)
- Shows suggestions when typing ≥ 5 characters
- Displays confidence score and similar tickets
- Click to view full details

### Confidence Scoring

For each cluster, compute:
- **Intra-cluster similarity**: Average similarity between all tickets in cluster
- **Inter-cluster similarity**: Average similarity to tickets in other clusters
- **Confidence**: (intra - inter + 1) / 2

Higher confidence = tickets are more similar to each other than to other clusters.
