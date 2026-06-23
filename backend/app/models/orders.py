"""Order model for customer orders."""

from sqlalchemy import UUID, Column, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Order(Base, UUIDMixin, TimestampMixin):
    """Order model for customer orders."""

    __tablename__ = "orders"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    order_number = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    total_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    customer_email = Column(String(255), nullable=True)
    customer_name = Column(String(255), nullable=True)
    shipping_address = Column(JSONB, nullable=True)
    billing_address = Column(JSONB, nullable=True)
    items = Column(JSONB, nullable=True)
    notes = Column(String(1000), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    refund_orders = relationship("RefundOrder", back_populates="order")

    __table_args__ = (
        Index("ix_orders_tenant_id", "tenant_id"),
        Index("ix_orders_shop_id", "shop_id"),
        Index("ix_orders_order_number", "order_number"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_created_at", "created_at"),
    )
