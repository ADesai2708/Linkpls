from datetime import datetime

from pydantic import BaseModel, Field


class CommentFrom(BaseModel):
    user_id: str
    username: str


class CommentData(BaseModel):
    comment_id: str
    post_id: str | None = None
    text: str | None = None
    created_at: datetime | None = None
    from_: CommentFrom | None = Field(
        default=None,
        alias="from"
    )

    model_config = {
        "populate_by_name": True
    }

class WebhookEvent(BaseModel):
    event_id: str
    event_type: str
    sent_at: datetime
    data: CommentData