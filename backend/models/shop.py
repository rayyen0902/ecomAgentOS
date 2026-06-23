"""店铺模型"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Shop(Base):
    __tablename__ = "shops"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)  # douyin/taobao/pdd/xiaohongshu
    platform_shop_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cookies: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    cookie_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="shop", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="shop", cascade="all, delete-orphan")
    agent_tasks = relationship("AgentTask", back_populates="shop", cascade="all, delete-orphan")
    approval_tasks = relationship("ApprovalTask", back_populates="shop", cascade="all, delete-orphan")
