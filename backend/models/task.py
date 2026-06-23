"""Agent任务模型"""
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id"))
    agent_type: Mapped[str] = mapped_column(String(50))
    task_type: Mapped[str] = mapped_column(String(100))
    input_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    decision: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    actions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    approved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    screenshot_urls: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    shop = relationship("Shop", back_populates="agent_tasks")
    approval_tasks = relationship("ApprovalTask", back_populates="agent_task", cascade="all, delete-orphan")
