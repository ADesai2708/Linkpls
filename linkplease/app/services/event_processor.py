from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CommentState, Delivery, DuplicateBlock, Event, Rule


def process_event(
    db: Session,
    event_id: str
) -> int:

    event = db.get(Event, event_id)

    if not event:
        return 0

    # If this event was already completed, don't process it again.
    if event.processing_status == "processed":
        return 0

    event.processing_status = "processing"
    db.commit()

    created_count = 0

    try:
        # We only process comment.created events.
        if event.event_type != "comment.created":
            event.processing_status = "processed"
            db.commit()
            return 0

        # Check whether the comment has been deleted.
        comment_state = db.get(
            CommentState,
            event.comment_id
        )

        if not comment_state:
            event.processing_status = "processed"
            db.commit()
            return 0

        if comment_state.status == "deleted":
            event.processing_status = "processed"
            db.commit()
            return 0

        if not event.user_id or not event.text:
            event.processing_status = "processed"
            db.commit()
            return 0

        # Find all rules.
        rules = db.scalars(
            select(Rule)
        ).all()

        for rule in rules:

            # Case-insensitive substring matching.
            if rule.keyword.lower() not in event.text.lower():
                continue

            # Check whether this user already has
            # a delivery for this rule.
            existing_delivery = db.scalar(
                select(Delivery).where(
                    Delivery.rule_id == rule.id,
                    Delivery.user_id == event.user_id
                )
            )

            if existing_delivery:
                duplicate_block = DuplicateBlock(
                    rule_id=rule.id,
                    user_id=event.user_id,
                    comment_id=event.comment_id
                )

                db.add(duplicate_block)
                continue

            delivery = Delivery(
                rule_id=rule.id,
                user_id=event.user_id,
                comment_id=event.comment_id,
                message=rule.dm_message,
                status="queued",
                attempts=0
            )

            db.add(delivery)
            created_count += 1

        event.processing_status = "processed"

        db.commit()

        return created_count

    except Exception:
        db.rollback()

        # The event was not successfully processed.
        # Put it back into pending so a later worker
        # can try again.
        event = db.get(Event, event_id)

        if event:
            event.processing_status = "pending"
            db.commit()

        raise