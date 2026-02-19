"""Operational Intelligence Dashboard - FastAPI Backend.
AI-powered operational command center. Generates tickets and insights at startup.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ticket_generator import TicketGenerator
from ai_processor import OperationalAIProcessor
from typing import Dict, Any
import uvicorn

app = FastAPI(title="Operational Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ticket_generator = TicketGenerator()
demo_tickets = ticket_generator.generate_tickets()

ai_processor = OperationalAIProcessor()
insights_cache: Dict[str, Any] | None = None


@app.on_event("startup")
async def startup_event():
    """Generate tickets and run AI pipeline on startup."""
    global insights_cache, demo_tickets
    print("Generating demo tickets...")
    demo_tickets = ticket_generator.generate_tickets()
    print(f"Generated {len(demo_tickets)} tickets")
    print("Processing tickets with AI...")
    insights_cache = ai_processor.process_tickets(demo_tickets)
    print(
        f"Processed into {len(insights_cache['clusters'])} clusters. "
        f"Trend: {insights_cache['change_tracking']['trend_direction']}"
    )


@app.get("/")
async def root():
    return {
        "service": "Operational Intelligence API",
        "status": "running",
        "tickets_loaded": len(demo_tickets),
    }


@app.get("/tickets")
async def get_tickets():
    """Get raw demo tickets."""
    return {"tickets": demo_tickets, "total": len(demo_tickets)}


@app.get("/insights")
async def get_insights():
    """Get AI-processed operational insights with clusters and change tracking."""
    if insights_cache is None:
        return {"error": "Insights not yet processed"}
    return insights_cache


@app.get("/cluster/{cluster_id}")
async def get_cluster(cluster_id: int):
    """Get detailed view of a single cluster by ID."""
    if insights_cache is None:
        raise HTTPException(status_code=503, detail="Insights not yet processed")

    for cluster in insights_cache["clusters"]:
        if cluster["cluster_id"] == cluster_id:
            return cluster

    raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")


@app.post("/jira-draft/{cluster_id}")
async def create_jira_draft(cluster_id: int):
    """Generate a structured Jira draft for a cluster. No real Jira integration."""
    if insights_cache is None:
        raise HTTPException(status_code=503, detail="Insights not yet processed")

    cluster = None
    for c in insights_cache["clusters"]:
        if c["cluster_id"] == cluster_id:
            cluster = c
            break

    if cluster is None:
        raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found")

    summary = f"[OPS] {cluster['workflow_type']}: {cluster['summary'][:80]}..."
    priority = cluster.get("priority_level", "P3")
    impact_explanation = cluster.get("business_impact", "Recurring operational pattern detected.")
    cluster_summary = cluster["summary"]
    example_tickets = cluster.get("example_tickets", [])
    recommended_action = cluster.get("recommended_action", "Investigate and remediate.")
    owner_team = cluster.get("owner_team", "Platform Team")

    draft = {
        "summary": summary,
        "priority": priority,
        "impact_explanation": impact_explanation,
        "cluster_summary": cluster_summary,
        "example_tickets": [
            {"id": t["id"], "title": t["title"], "severity": t["severity"]}
            for t in example_tickets
        ],
        "recommended_action": recommended_action,
        "owner_team": owner_team,
        "incident_count": cluster["incident_count"],
        "impact_score": cluster["impact_score"],
        "urgency_tag": cluster.get("urgency_tag", "elevated"),
    }

    return {"draft": draft, "cluster_id": cluster_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
