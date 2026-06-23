"""SKU model for product variants."""

from sqlalchemy import UUID, Boolean, Column, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class SKU(Base, UUIDMixin, TimestampMixin):
    """SKU (Stock Keeping Unit) model for product variants."""

    __tablename__ = "skus"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    sku_code = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    compare_at_price = Column(Numeric(10, 2), nullable=True)
    cost_price = Column(Numeric(10, 2), nullable=True)
    inventory_quantity = Column(Numeric(10, 0), default=0, nullable=False)
    weight = Column(Numeric(10, 2), nullable=True)
    attributes = Column(JSONB, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    product = relationship("Product", back_populates="skus")
    price_history = relationship("PriceHistory", back_populates="sku")

    __table_args__ = (
        Index("ix_skus_tenant_id", "tenant_id"),
        Index("ix_skus_product_id", "product_id"),
        Index("ix_skus_sku_code", "sku_code"),
        Index("ix_skus_is_active", "is_active"),
    )
