from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Delivery
from app.models.delivery import DuplicateBlock


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db)
):
    # Count DMs the mock API confirmed as delivered.
    sent = db.scalar(
        select(func.count())
        .select_from(Delivery)
        .where(Delivery.status == "delivered")
    ) or 0

    # Count deliveries we permanently gave up on after MAX_ATTEMPTS.
    failed = db.scalar(
        select(func.count())
        .select_from(Delivery)
        .where(Delivery.status == "failed")
    ) or 0

    # Count deliveries still in flight:
    # queued    = not yet attempted
    # sending   = attempt in progress (transient, rarely seen at query time)
    # awaiting_delivery = sent but mock API not yet confirmed delivered
    queued = db.scalar(
        select(func.count())
        .select_from(Delivery)
        .where(
            Delivery.status.in_(
                ["queued", "sending", "awaiting_delivery"]
            )
        )
    ) or 0

    # Count duplicate blocks — one row per (user, rule, comment) we
    # deliberately chose NOT to DM because that user already has a
    # delivery for that rule.
    duplicates_blocked = db.scalar(
        select(func.count())
        .select_from(DuplicateBlock)
    ) or 0

    return {
        "sent": sent,
        "failed": failed,
        "queued": queued,
        "duplicates_blocked": duplicates_blocked
    }