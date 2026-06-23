"""SQLAlchemy declarative base and common types."""

from __future__ import annotations

import uuid

from sqlalchemy import UUID, Column, DateTime, Index, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at and updated_at timestamp columns."""

    created_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )


class UUIDMixin:
    """Mixin for UUID primary key."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TenantMixin:
    """Mixin for tenant_id foreign key."""

    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    Index("ix_%(tablename)s_tenant_id", tenant_id)
