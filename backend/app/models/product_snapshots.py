"""Product snapshot model for product versioning."""

from sqlalchemy import UUID, Column, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class ProductSnapshot(Base, UUIDMixin, TimestampMixin):
    """Product snapshot for versioning and audit trail."""

    __tablename__ = "product_snapshots"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    snapshot_data = Column(JSONB, nullable=False)
    version = Column(String(50), nullable=False)
    change_summary = Column(String(500), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="snapshots")

    __table_args__ = (
        Index("ix_product_snapshots_tenant_id", "tenant_id"),
        Index("ix_product_snapshots_product_id", "product_id"),
        Index("ix_product_snapshots_version", "version"),
    )
