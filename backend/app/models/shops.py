"""Shop model for e-commerce stores."""

from sqlalchemy import UUID, Boolean, Column, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Shop(Base, UUIDMixin, TimestampMixin):
    """Shop model representing an e-commerce store."""

    __tablename__ = "shops"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    platform = Column(String(50), nullable=False)
    settings = Column(JSONB, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="shops")
    owner = relationship("User", back_populates="shops")
    products = relationship("Product", back_populates="shop")

    __table_args__ = (
        Index("ix_shops_tenant_id", "tenant_id"),
        Index("ix_shops_owner_id", "owner_id"),
        Index("ix_shops_slug", "slug"),
        Index("ix_shops_platform", "platform"),
    )
