from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ticket_generator import TicketGenerator
from ai_processor import OperationalAIProcessor
import uvicorn

app = FastAPI(title="Operational Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ticket_generator = TicketGenerator(num_tickets=100)
demo_tickets = ticket_generator.generate_tickets()

ai_processor = OperationalAIProcessor()
insights_cache = None

@app.on_event("startup")
async def startup_event():
    """Process tickets on startup"""
    global insights_cache
    print("Processing tickets with AI...")
    insights_cache = ai_processor.process_tickets(demo_tickets)
    print(f"Processed {len(demo_tickets)} tickets into {len(insights_cache['clusters'])} clusters")

@app.get("/")
async def root():
    return {
        "service": "Operational Intelligence API",
        "status": "running",
        "tickets_loaded": len(demo_tickets)
    }

@app.get("/insights")
async def get_insights():
    """Get AI-processed operational insights"""
    if insights_cache is None:
        return {"error": "Insights not yet processed"}
    return insights_cache

@app.get("/tickets")
async def get_tickets():
    """Get raw demo tickets"""
    return {
        "tickets": demo_tickets,
        "total": len(demo_tickets)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
