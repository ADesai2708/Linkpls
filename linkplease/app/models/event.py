from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    comment_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    post_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    user_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    username: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    processing_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending"
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )