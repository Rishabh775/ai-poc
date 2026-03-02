"""Operational Intelligence Dashboard - FastAPI Backend.
AI-powered operational command center. Generates tickets and insights at startup.

Features:
- Real-time duplicate detection with configurable threshold
- Hybrid clustering (semantic + metadata)
- Dynamic cluster assignment
- Cluster confidence scoring
- Per-cluster change tracking
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn

from ticket_generator import TicketGenerator
from ai_processor import OperationalAIProcessor
import config


app = FastAPI(title="Operational Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DuplicateCheckRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    workflow_type: Optional[str] = ""
    severity: Optional[str] = ""
    title_only: bool = True


class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    confidence_score: float
    matched_cluster_id: Optional[int]
    similar_tickets: List[Dict]
    message: str


class ClusterAssignmentRequest(BaseModel):
    title: str
    description: str
    workflow_type: str
    severity: str


class CreateTicketRequest(BaseModel):
    title: str
    description: str
    workflow_type: str
    severity: str
    category: Optional[str] = None


ticket_generator = TicketGenerator()
demo_tickets = ticket_generator.generate_tickets()

ai_processor = OperationalAIProcessor()
insights_cache: Dict[str, Any] | None = None


@app.on_event("startup")
async def startup_event():
    """Run AI pipeline on startup."""
    global insights_cache, demo_tickets
    print("=" * 60)
    print("Operational Intelligence - AI Triage Engine")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Similarity Threshold: {config.SIMILARITY_THRESHOLD}")
    print(f"  DBSCAN EPS: {config.DBSCAN_EPS}")
    print(f"  Min Samples: {config.MIN_SAMPLES}")
    print("-" * 60)
    print(f"Starting with {len(demo_tickets)} tickets")
    if demo_tickets:
        print("Processing tickets with AI clustering...")
        insights_cache = ai_processor.process_tickets(demo_tickets)
        print(
            f"Processed into {len(insights_cache['clusters'])} clusters. "
            f"Trend: {insights_cache['change_tracking']['trend_direction']}"
        )
        avg_conf = insights_cache["metrics"].get("average_cluster_confidence", 0)
        print(f"Average cluster confidence: {avg_conf:.1%}")
    else:
        print("No tickets to process. Add tickets via API.")
    print("=" * 60)


@app.get("/")
async def root():
    return {
        "service": "Operational Intelligence API",
        "status": "running",
        "tickets_loaded": len(demo_tickets),
        "config": config.get_config(),
    }


@app.get("/tickets")
async def get_tickets():
    """Get raw demo tickets."""
    return {"tickets": demo_tickets, "total": len(demo_tickets)}


@app.get("/tickets/search")
async def search_tickets(q: str = ""):
    """Search tickets by title (for autocomplete)."""
    if insights_cache is None:
        raise HTTPException(status_code=503, detail="Insights not yet processed")

    if not q or len(q) < 2:
        return {"tickets": [], "total": 0}

    q_lower = q.lower()
    matching = [
        {
            "id": t["id"],
            "title": t["title"],
            "severity": t["severity"],
            "workflow_type": t["workflow_type"],
        }
        for t in demo_tickets
        if q_lower in t["title"].lower() or q_lower in t["description"].lower()
    ][:10]

    return {"tickets": matching, "total": len(matching)}


@app.get("/tickets-with-clusters")
async def get_tickets_with_clusters():
    """Get all tickets with their cluster assignments for debugging/verification."""
    if insights_cache is None:
        raise HTTPException(status_code=503, detail="Insights not yet processed")

    cluster_map = {}
    for cluster in insights_cache["clusters"]:
        for ticket in cluster.get("example_tickets", []):
            cluster_map[ticket["id"]] = {
                "cluster_id": cluster["cluster_id"],
                "workflow_type": cluster["workflow_type"],
                "priority_level": cluster.get("priority_level"),
                "impact_score": cluster["impact_score"],
                "confidence_score": cluster.get("cluster_confidence_score"),
            }

    tickets_with_clusters = []
    for ticket in demo_tickets:
        cluster_info = cluster_map.get(ticket["id"], {})
        tickets_with_clusters.append(
            {
                **ticket,
                "cluster_id": cluster_info.get("cluster_id"),
                "cluster_workflow": cluster_info.get("workflow_type"),
                "cluster_priority": cluster_info.get("priority_level"),
                "cluster_impact": cluster_info.get("impact_score"),
                "cluster_confidence": cluster_info.get("confidence_score"),
            }
        )

    return {
        "tickets": tickets_with_clusters,
        "total": len(tickets_with_clusters),
        "clusters": insights_cache["clusters"],
    }


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


@app.post("/check-duplicate", response_model=DuplicateCheckResponse)
async def check_duplicate(request: DuplicateCheckRequest):
    """Check if a ticket is a duplicate of existing clusters.

    Uses semantic embeddings and cosine similarity to find similar tickets.
    By default, searches only by title (title_only=True) as users may not
    remember workflow type or severity.

    Returns:
        - is_duplicate: Whether similarity exceeds threshold
        - confidence_score: Maximum similarity score
        - matched_cluster_id: ID of most similar cluster
        - similar_tickets: Example tickets from matched cluster
    """
    if insights_cache is None:
        raise HTTPException(status_code=503, detail="Insights not yet processed")

    result = ai_processor.check_duplicate(
        title=request.title,
        description=request.description,
        workflow_type=request.workflow_type,
        severity=request.severity,
        title_only=request.title_only,
    )

    return result


@app.post("/assign-cluster")
async def assign_to_cluster(request: ClusterAssignmentRequest):
    """Dynamically assign a new ticket to an existing cluster or indicate new cluster needed.

    Uses centroid-based matching to find the best cluster match.
    """
    if insights_cache is None:
        raise HTTPException(status_code=503, detail="Insights not yet processed")

    result = ai_processor.assign_to_cluster(
        title=request.title,
        description=request.description,
        workflow_type=request.workflow_type,
        severity=request.severity,
    )

    return result


@app.get("/config")
async def get_config():
    """Get current system configuration."""
    return config.get_config()


@app.post("/tickets")
async def create_ticket(request: CreateTicketRequest):
    """Manually add a new ticket for testing purposes."""
    global demo_tickets, insights_cache

    import uuid
    from datetime import datetime

    ticket_id = f"OPS-{uuid.uuid4().hex[:8].upper()}"
    new_ticket = {
        "id": ticket_id,
        "title": request.title,
        "description": request.description,
        "workflow_type": request.workflow_type,
        "severity": request.severity,
        "category": request.category or "manual",
        "timestamp": datetime.now().isoformat(),
    }

    demo_tickets.append(new_ticket)

    insights_cache = None
    insights_cache = ai_processor.process_tickets(demo_tickets)

    return {"ticket": new_ticket, "message": "Ticket created and clusters updated"}


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
    impact_explanation = cluster.get(
        "business_impact", "Recurring operational pattern detected."
    )
    cluster_summary = cluster["summary"]
    example_tickets = cluster.get("example_tickets", [])
    recommended_action = cluster.get("recommended_action", "Investigate and remediate.")
    owner_team = cluster.get("owner_team", "Platform Team")
    confidence = cluster.get("cluster_confidence_score", 0)
    top_keywords = cluster.get("top_keywords", [])

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
        "confidence_score": confidence,
        "top_keywords": top_keywords,
    }

    return {"draft": draft, "cluster_id": cluster_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
