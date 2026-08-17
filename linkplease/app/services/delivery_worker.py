from datetime import datetime, timezone
import uuid

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Delivery
from app.services.pseudogram import PseudoGramClient
from app.services.rate_limiter import RateLimiter
MAX_ATTEMPTS = 5


def process_queued_deliveries():
    db = SessionLocal()

    try:
        deliveries = db.scalars(
            select(Delivery)
            .where(Delivery.status == "queued")
            .order_by(Delivery.created_at)
            .limit(10)
        ).all()

        client = PseudoGramClient()
        rate_limiter = RateLimiter()

        for delivery in deliveries:

            delivery.status = "sending"
            delivery.attempts += 1

            db.commit()

            if not delivery.idempotency_key:
                delivery.idempotency_key = (
                    f"linkplease-{delivery.id}-{uuid.uuid4()}"
                )

                db.commit()
            rate_limiter.wait_if_needed()
            status_code, body, headers = client.send_dm(
                recipient_user_id=delivery.user_id,
                message=delivery.message,
                comment_id=delivery.comment_id,
                idempotency_key=delivery.idempotency_key,
            )

            if status_code in (200, 202):

                delivery.dm_id = body["dm_id"]

                if body.get("status") == "delivered":
                    delivery.status = "delivered"
                else:
                    delivery.status = "awaiting_delivery"

                delivery.last_error = None

            elif status_code == 429:

                retry_after = headers.get(
                    "Retry-After",
                    "60"
                )

                delivery.status = "queued"

                delivery.last_error = (
                    f"Rate limited. Retry after "
                    f"{retry_after} seconds."
                )

            elif status_code == 500:

                if delivery.attempts >= MAX_ATTEMPTS:

                    delivery.status = "failed"

                    delivery.last_error = (
                        "Maximum retry attempts exceeded."
                    )

                else:

                    delivery.status = "queued"

                    delivery.last_error = (
                        "PseudoGram returned 500."
                    )

            elif status_code == 400:

                delivery.status = "failed"

                delivery.last_error = (
                    body.get(
                        "detail",
                        "Invalid request"
                    )
                )

            else:

                delivery.status = "failed"

                delivery.last_error = (
                    f"Unexpected status code: "
                    f"{status_code}"
                )

            delivery.updated_at = (
                datetime.now(timezone.utc)
            )

            db.commit()

    finally:
        db.close()