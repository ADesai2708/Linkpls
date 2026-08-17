from sqlalchemy import select

from app.database import SessionLocal
from app.models import Event
from app.services.event_processor import process_event


def process_pending_events():

    db = SessionLocal()

    try:

        events = db.scalars(
            select(Event)
            .where(
                Event.processing_status == "pending"
            )
            .order_by(Event.received_at)
            .limit(100)
        ).all()

        for event in events:

            process_event(
                db,
                event.event_id
            )

    finally:

        db.close()