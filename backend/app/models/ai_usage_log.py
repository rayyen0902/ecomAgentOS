"""AI usage log model for tracking AI API calls."""

from sqlalchemy import UUID, Column, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base, TimestampMixin, UUIDMixin


class AIUsageLog(Base, UUIDMixin, TimestampMixin):
    """AI usage log model for tracking AI API calls."""

    __tablename__ = "ai_usage_logs"

    tenant_id = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    prompt_tokens = Column(Numeric(10, 0), default=0, nullable=False)
    completion_tokens = Column(Numeric(10, 0), default=0, nullable=False)
    total_tokens = Column(Numeric(10, 0), default=0, nullable=False)
    latency_ms = Column(Numeric(10, 0), default=0, nullable=False)
    request_data = Column(JSONB, nullable=True)
    response_data = Column(JSONB, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    __table_args__ = (
        Index("ix_ai_usage_logs_tenant_id", "tenant_id"),
        Index("ix_ai_usage_logs_user_id", "user_id"),
        Index("ix_ai_usage_logs_provider", "provider"),
        Index("ix_ai_usage_logs_model", "model"),
        Index("ix_ai_usage_logs_created_at", "created_at"),
    )
