from fastapi import FastAPI

from app.database import Base, engine
from app.models import (
    Rule,
    Event,
    CommentState,
    Delivery,
    DuplicateBlock,
)
from app.routes.rules import router as rules_router
from app.routes.webhook import router as webhook_router
from app.routes.stats import router as stats_router

# Create all tables on startup if they don't already exist.
# In production you'd use Alembic migrations instead.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="LinkPlease Automation API",
    version="1.0.0"
)

app.include_router(rules_router)
app.include_router(webhook_router)
app.include_router(stats_router)


@app.get("/")
def root():
    return {
        "message": "LinkPlease API is running"
    }


@app.get("/health")
def health():
    try:
        with engine.connect():
            return {
                "status": "healthy",
                "database": "connected"
            }

    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }