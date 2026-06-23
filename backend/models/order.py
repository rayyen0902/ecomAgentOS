"""订单模型"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id"))
    platform_order_id: Mapped[str] = mapped_column(String(100), unique=True)
    product_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    sale_price: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    buyer_info: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    logistics_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    fulfillment_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    shop = relationship("Shop", back_populates="orders")
    product = relationship("Product", back_populates="orders")
