from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    rule_id: Mapped[str] = mapped_column(
        ForeignKey("rules.id"),
        nullable=False
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    comment_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="queued"
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    dm_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    idempotency_key: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "rule_id",
            "user_id",
            name="uq_delivery_rule_user"
        ),
    )


class DuplicateBlock(Base):
    """
    One row per (rule, user, comment) we chose NOT to DM because
    a Delivery already existed for that (rule, user) pair.

    The unique constraint prevents double-counting if the same event
    is re-processed after a crash (idempotent insertion).
    """
    __tablename__ = "duplicate_blocks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    rule_id: Mapped[str] = mapped_column(
        ForeignKey("rules.id"),
        nullable=False
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    comment_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "rule_id",
            "user_id",
            "comment_id",
            name="uq_duplicate_block_rule_user_comment"
        ),
    )