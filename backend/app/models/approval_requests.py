"""Approval request model for tracking approval workflows."""

from sqlalchemy import UUID, Column, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class ApprovalRequest(Base, UUIDMixin, TimestampMixin):
    """Approval request model for tracking approval workflows."""

    __tablename__ = "approval_requests"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    policy_id = Column(UUID(as_uuid=True), ForeignKey("approval_policies.id"), nullable=False)
    request_number = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    requested_by = Column(String(100), nullable=False)
    approved_by = Column(String(100), nullable=True)
    request_data = Column(JSONB, nullable=True)
    approval_data = Column(JSONB, nullable=True)
    notes = Column(String(1000), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    policy = relationship("ApprovalPolicy", back_populates="approval_requests")

    __table_args__ = (
        Index("ix_approval_requests_tenant_id", "tenant_id"),
        Index("ix_approval_requests_policy_id", "policy_id"),
        Index("ix_approval_requests_request_number", "request_number"),
        Index("ix_approval_requests_status", "status"),
    )
