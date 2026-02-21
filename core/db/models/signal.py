import uuid
from datetime import datetime

from sqlalchemy import String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    category: Mapped[str] = mapped_column(String, index=True)
    message: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    trend_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    composite_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    keyword_burst: Mapped[float | None] = mapped_column(Float, nullable=True)
    top_keyword: Mapped[str | None] = mapped_column(String, nullable=True)
    story_id: Mapped[str | None] = mapped_column(String, nullable=True)
    signal_type: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)
