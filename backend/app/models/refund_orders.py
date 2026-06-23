"""Refund order model for handling returns and refunds."""

from sqlalchemy import UUID, Column, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class RefundOrder(Base, UUIDMixin, TimestampMixin):
    """Refund order model for handling returns and refunds."""

    __tablename__ = "refund_orders"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    refund_number = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    refund_amount = Column(Numeric(12, 2), nullable=False)
    reason = Column(String(500), nullable=True)
    notes = Column(String(1000), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="refund_orders")

    __table_args__ = (
        Index("ix_refund_orders_tenant_id", "tenant_id"),
        Index("ix_refund_orders_order_id", "order_id"),
        Index("ix_refund_orders_refund_number", "refund_number"),
        Index("ix_refund_orders_status", "status"),
    )
