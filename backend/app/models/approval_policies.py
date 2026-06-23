"""Approval policy model for defining approval workflows."""

from sqlalchemy import UUID, Boolean, Column, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class ApprovalPolicy(Base, UUIDMixin, TimestampMixin):
    """Approval policy model for defining approval workflows."""

    __tablename__ = "approval_policies"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    trigger_conditions = Column(JSONB, nullable=True)
    approval_steps = Column(JSONB, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    approval_requests = relationship("ApprovalRequest", back_populates="policy")

    __table_args__ = (
        Index("ix_approval_policies_tenant_id", "tenant_id"),
        Index("ix_approval_policies_is_active", "is_active"),
    )
