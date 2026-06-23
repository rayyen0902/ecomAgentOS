"""Price history model for tracking price changes."""

from sqlalchemy import UUID, Column, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class PriceHistory(Base, UUIDMixin, TimestampMixin):
    """Price history for tracking price changes over time."""

    __tablename__ = "price_history"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    sku_id = Column(UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    compare_at_price = Column(Numeric(10, 2), nullable=True)
    cost_price = Column(Numeric(10, 2), nullable=True)
    changed_by = Column(String(100), nullable=True)
    reason = Column(String(255), nullable=True)

    # Relationships
    sku = relationship("SKU", back_populates="price_history")

    __table_args__ = (
        Index("ix_price_history_tenant_id", "tenant_id"),
        Index("ix_price_history_sku_id", "sku_id"),
        Index("ix_price_history_created_at", "created_at"),
    )
