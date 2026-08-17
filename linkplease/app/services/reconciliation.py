from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Delivery
from app.services.pseudogram import PseudoGramClient


def reconcile_deliveries():
    db = SessionLocal()

    try:
        deliveries = db.scalars(
            select(Delivery)
            .where(
                Delivery.status == "awaiting_delivery"
            )
            .order_by(Delivery.created_at)
            .limit(100)
        ).all()

        client = PseudoGramClient()

        for delivery in deliveries:
            if not delivery.dm_id:
                continue

            try:
                result = client.get_dm_status(delivery.dm_id)
            except Exception as exc:
                delivery.last_error = f"Status check failed: {exc}"
                delivery.updated_at = datetime.now(timezone.utc)
                db.commit()
                continue

            status = result.get("status")

            if status == "delivered":
                delivery.status = "delivered"
                delivery.last_error = None
            elif status == "failed":
                if delivery.attempts < 5:
                    delivery.status = "queued"
                    delivery.dm_id = None
                    delivery.idempotency_key = None
                    delivery.next_attempt_at = (
                        datetime.now(timezone.utc) + timedelta(seconds=2)
                    )
                    delivery.last_error = "PseudoGram reported delivery failure."
                else:
                    delivery.status = "failed"
                    delivery.last_error = "Maximum attempts exceeded."
            elif status == "queued":
                delivery.status = "awaiting_delivery"
            else:
                delivery.last_error = f"Unknown DM status: {status}"

            delivery.updated_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()