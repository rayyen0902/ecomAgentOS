"""Platform adapter model for different e-commerce platforms."""

from sqlalchemy import UUID, Boolean, Column, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class PlatformAdapter(Base, UUIDMixin, TimestampMixin):
    """Platform adapter for connecting to different e-commerce platforms."""

    __tablename__ = "platform_adapters"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    platform_type = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    config = Column(JSONB, nullable=True)
    credentials = Column(JSONB, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    # Relationships
    products = relationship("Product", back_populates="platform_adapter")

    __table_args__ = (
        Index("ix_platform_adapters_tenant_id", "tenant_id"),
        Index("ix_platform_adapters_platform_type", "platform_type"),
    )
