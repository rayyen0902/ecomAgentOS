"""Product model for main product catalog."""

from sqlalchemy import UUID, Boolean, Column, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Product(Base, UUIDMixin, TimestampMixin):
    """Product model for main product catalog."""

    __tablename__ = "products"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), nullable=False)
    platform_adapter_id = Column(
        UUID(as_uuid=True), ForeignKey("platform_adapters.id"), nullable=True
    )
    external_id = Column(String(255), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(String(10000), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    tags = Column(JSONB, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    shop = relationship("Shop", back_populates="products")
    platform_adapter = relationship("PlatformAdapter", back_populates="products")
    snapshots = relationship("ProductSnapshot", back_populates="product")
    skus = relationship("SKU", back_populates="product")

    __table_args__ = (
        Index("ix_products_tenant_id", "tenant_id"),
        Index("ix_products_shop_id", "shop_id"),
        Index("ix_products_platform_adapter_id", "platform_adapter_id"),
        Index("ix_products_external_id", "external_id"),
        Index("ix_products_is_active", "is_active"),
    )
