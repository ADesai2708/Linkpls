import hashlib
import hmac

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import SessionLocal, settings
from app.models import CommentState, Event
from app.schemas.webhook import WebhookEvent


router = APIRouter()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def verify_signature(
    raw_body: bytes,
    signature: str | None,
) -> bool:

    if not signature:
        print("HMAC DEBUG: signature header missing")
        return False

    print(
        "HMAC DEBUG: key fingerprint:",
        hashlib.sha256(
            settings.pseudogram_api_key.encode()
        ).hexdigest()[:12],
    )

    print(
        "HMAC DEBUG: body fingerprint:",
        hashlib.sha256(raw_body).hexdigest()[:12],
    )

    expected_signature = hmac.new(
        settings.pseudogram_api_key.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    received_signature = (
        signature[7:]
        if signature.startswith("sha256=")
        else signature
    )

    print("HMAC DEBUG: received prefix:", received_signature[:12])
    print("HMAC DEBUG: expected prefix:", expected_signature[:12])
    print("HMAC DEBUG: body length:", len(raw_body))
    print("HMAC DEBUG: match:",
          hmac.compare_digest(
              received_signature,
              expected_signature
          ))

    if not signature.startswith("sha256="):
        return False

    return hmac.compare_digest(
        received_signature,
        expected_signature,
    )


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    # Read the ORIGINAL request body.
    # HMAC must be calculated from these exact bytes.
    raw_body = await request.body()

    signature = request.headers.get(
        "X-PseudoGram-Signature"
    )

    if not verify_signature(
        raw_body,
        signature,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    # Parse the already-read body into our Pydantic schema.
    payload = WebhookEvent.model_validate_json(
        raw_body
    )

    existing_event = db.get(
        Event,
        payload.event_id
    )

    if existing_event:
        return {
            "status": "duplicate",
            "event_id": payload.event_id
        }

    event = Event(
        event_id=payload.event_id,
        event_type=payload.event_type,
        comment_id=payload.data.comment_id,
        post_id=payload.data.post_id,
        user_id=(
            payload.data.from_.user_id
            if payload.data.from_
            else None
        ),
        username=(
            payload.data.from_.username
            if payload.data.from_
            else None
        ),
        text=payload.data.text,
        sent_at=payload.sent_at
    )

    db.add(event)

    if payload.event_type == "comment.deleted":

        comment_state = db.get(
            CommentState,
            payload.data.comment_id
        )

        if comment_state:
            comment_state.status = "deleted"

        else:
            comment_state = CommentState(
                comment_id=payload.data.comment_id,
                status="deleted"
            )

            db.add(comment_state)

    elif payload.event_type == "comment.created":

        comment_state = db.get(
            CommentState,
            payload.data.comment_id
        )

        if comment_state:

            # Never resurrect a deleted comment.
            if comment_state.status != "deleted":

                comment_state.status = "active"

                comment_state.user_id = (
                    payload.data.from_.user_id
                    if payload.data.from_
                    else None
                )

                comment_state.text = payload.data.text

        else:

            comment_state = CommentState(
                comment_id=payload.data.comment_id,
                status="active",
                user_id=(
                    payload.data.from_.user_id
                    if payload.data.from_
                    else None
                ),
                text=payload.data.text
            )

            db.add(comment_state)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        return {
            "status": "duplicate",
            "event_id": payload.event_id
        }

    return {
        "status": "accepted",
        "event_id": payload.event_id
    }