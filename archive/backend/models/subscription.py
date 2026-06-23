"""订阅和租户模型"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Integer, DateTime, func, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class Tenant(Base):
    """租户表"""
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    plan: Mapped[str] = mapped_column(String(20), default="starter")
    status: Mapped[str] = mapped_column(String(20), default="active")
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tenant_config = relationship("TenantConfig", back_populates="tenant", uselist=False)
    subscriptions = relationship("Subscription", back_populates="tenant", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="tenant", cascade="all, delete-orphan")


class TenantConfig(Base):
    """租户配置表"""
    __tablename__ = "tenant_configs"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), primary_key=True)
    max_shops: Mapped[int] = mapped_column(Integer, nullable=False)
    max_monthly_images: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_monthly_videos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    features_enabled: Mapped[dict] = mapped_column(JSONB, default=dict)
    celery_queue: Mapped[str | None] = mapped_column(String(50), nullable=True)
    api_rate_limit: Mapped[int] = mapped_column(Integer, default=100)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", back_populates="tenant_config")


class Subscription(Base):
    """订阅记录表"""
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    plan: Mapped[str] = mapped_column(String(20), nullable=False)
    price_monthly: Mapped[Numeric | None] = mapped_column(Numeric(10, 2), nullable=True)
    price_paid: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    billing_cycle: Mapped[str | None] = mapped_column(String(10), nullable=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
    payment_method: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tenant = relationship("Tenant", back_populates="subscriptions")


class UsageRecord(Base):
    """用量记录表"""
    __tablename__ = "usage_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    resource_type: Mapped[str] = mapped_column(String(50))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tenant = relationship("Tenant", back_populates="usage_records")
