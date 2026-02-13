# Operational Intelligence Dashboard

An AI-powered system that analyzes operational incidents and produces actionable insights through pattern detection, clustering, and trend analysis.

## Overview

This full-stack prototype demonstrates how AI can transform operational noise into strategic intelligence by:

- Detecting recurring issue patterns across support tickets
- Identifying trends and anomalies over time
- Calculating impact scores for prioritization
- Generating explainable, actionable insights
- Visualizing operational health metrics

## Architecture

```
┌─────────────┐          ┌──────────────┐
│   React     │  ◄─────  │   FastAPI    │
│  Dashboard  │   REST   │   Backend    │
└─────────────┘          └──────────────┘
                                │
                         ┌──────▼───────┐
                         │  AI Engine   │
                         │  - Sentence  │
                         │    Transformers│
                         │  - DBSCAN    │
                         │  - Analytics │
                         └──────────────┘
```

## Features

### Backend (Python + FastAPI)
- Generates 100 realistic demo Jira-style tickets with recurring patterns
- Uses Sentence Transformers for semantic text embeddings
- Clusters similar issues using DBSCAN algorithm
- Detects temporal trends and calculates impact scores
- Provides REST API for insights and raw data

### Frontend (React + TypeScript)
- Professional SaaS-style dashboard interface
- Real-time metrics: incidents, risk score, stability index
- Interactive charts: trend analysis, severity distribution, workflow breakdown
- AI-generated cluster summaries with actionable recommendations
- Executive summary with strategic insights

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

## Demo Data Patterns

The system simulates realistic operational issues:

1. **Reviewer Assignment Failures** - Load balancing and timeout issues
2. **Submission Workflow Bugs** - State machine and validation errors
3. **Dashboard Performance** - Query optimization and memory issues
4. **Timeout Errors** - Infrastructure and integration problems
5. **Release Regressions** - Deployment-related bugs

## AI Processing Pipeline

1. **Text Embedding**: Converts ticket titles and descriptions into semantic vectors
2. **Clustering**: Groups similar issues using DBSCAN (density-based clustering)
3. **Impact Scoring**: Calculates priority based on frequency, severity, and recurrence
4. **Trend Detection**: Analyzes temporal patterns and week-over-week changes
5. **Summary Generation**: Creates human-readable insights with context

## API Endpoints

- `GET /` - Service health check
- `GET /insights` - AI-processed operational insights
- `GET /tickets` - Raw demo ticket data

## Technology Stack

**Backend:**
- FastAPI
- Sentence Transformers (all-MiniLM-L6-v2)
- scikit-learn
- pandas
- NumPy

**Frontend:**
- React 18
- TypeScript
- Tailwind CSS
- Recharts
- Lucide Icons
- Axios

## Use Cases

This prototype demonstrates enterprise operational intelligence for:

- **DevOps Teams**: Identify recurring infrastructure issues
- **Support Organizations**: Detect high-impact support patterns
- **Engineering Leadership**: Track system stability and risk metrics
- **Product Teams**: Prioritize bug fixes based on impact analysis

## Demo Behavior

On startup:
1. Backend generates 100 demo tickets with realistic patterns
2. AI pipeline processes all tickets and identifies clusters
3. Frontend loads and displays insights immediately
4. Dashboard shows actionable intelligence within seconds

No manual setup or configuration required.

## Future Enhancements

- Real-time ticket ingestion from Jira/GitHub
- Custom alert thresholds and notifications
- Historical trend comparison
- Root cause analysis with LLMs
- Automated remediation suggestions
- Team performance metrics

## License

MIT
