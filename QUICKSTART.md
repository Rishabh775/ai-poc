# Quick Start Guide

## Running the Operational Intelligence Dashboard

### Step 1: Start the Backend

Open a terminal and run:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

You should see:
```
Processing tickets with AI...
Processed 100 tickets into X clusters
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Keep this terminal open.

### Step 2: Start the Frontend

Open a new terminal and run:

```bash
npm install  # if you haven't already
npm run dev
```

The dashboard will open at `http://localhost:5173`

### What to Expect

1. The dashboard will show a loading screen for ~2 seconds
2. You'll see:
   - 4 key metrics cards (Total Incidents, Clusters, Risk Score, Stability Index)
   - Executive Summary with actionable recommendations
   - Incident trend chart over 90 days
   - Workflow distribution pie chart
   - Severity distribution bar chart
   - Top 5 AI-detected issue clusters with detailed summaries

### Demo Data

The system automatically generates 100 realistic operational tickets with patterns:
- Reviewer assignment failures
- Submission workflow bugs
- Dashboard performance issues
- Timeout errors
- Release regressions

### API Testing

You can also test the API directly:

```bash
curl http://localhost:8000/insights
curl http://localhost:8000/tickets
```

### Troubleshooting

**"Failed to load insights"**
- Make sure the backend is running on port 8000
- Check that Python dependencies are installed

**Python errors**
- Ensure Python 3.8+ is installed
- Try: `pip install --upgrade pip` then reinstall requirements

**Frontend not loading**
- Ensure Node.js 18+ is installed
- Try: `rm -rf node_modules && npm install`
