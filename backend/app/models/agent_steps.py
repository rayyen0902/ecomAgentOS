"""Agent step model for tracking individual steps within agent runs."""

from sqlalchemy import UUID, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class AgentStep(Base, UUIDMixin, TimestampMixin):
    """Agent step model for tracking individual steps within agent runs."""

    __tablename__ = "agent_steps"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    agent_run_id = Column(UUID(as_uuid=True), ForeignKey("agent_runs.id"), nullable=False)
    step_number = Column(String(50), nullable=False)
    step_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="running")
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    error_message = Column(String(1000), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    agent_run = relationship("AgentRun", back_populates="steps")

    __table_args__ = (
        Index("ix_agent_steps_tenant_id", "tenant_id"),
        Index("ix_agent_steps_agent_run_id", "agent_run_id"),
        Index("ix_agent_steps_step_number", "step_number"),
        Index("ix_agent_steps_step_type", "step_type"),
        Index("ix_agent_steps_status", "status"),
    )
