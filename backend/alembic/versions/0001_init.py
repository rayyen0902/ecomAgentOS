"""Initial migration - align with current model definitions.

Revision ID: 0001_init
Revises:
Create Date: 2026-06-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # === shops ===
    op.create_table(
        "shops",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("platform_shop_id", sa.String(100), nullable=True),
        sa.Column("cookies", postgresql.JSONB, nullable=True),
        sa.Column("cookie_expires_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("config", postgresql.JSONB, nullable=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # === products ===
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("shop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shops.id"), nullable=False),
        sa.Column("platform_product_id", sa.String(100), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("cost", sa.Numeric(10, 2), nullable=True),
        sa.Column("current_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("stock_quantity", sa.Integer(), server_default="0"),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("platform_data", postgresql.JSONB, nullable=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # === competitor_prices ===
    op.create_table(
        "competitor_prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("competitor_shop", sa.String(100), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # === orders ===
    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("shop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shops.id"), nullable=False),
        sa.Column("platform_order_id", sa.String(100), unique=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("quantity", sa.Integer(), server_default="1"),
        sa.Column("sale_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("buyer_info", postgresql.JSONB, nullable=True),
        sa.Column("logistics_no", sa.String(100), nullable=True),
        sa.Column("fulfillment_type", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("shipped_at", sa.DateTime(), nullable=True),
    )

    # === agent_tasks ===
    op.create_table(
        "agent_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("shop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shops.id"), nullable=True),
        sa.Column("agent_type", sa.String(50), nullable=False),
        sa.Column("task_type", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("priority", sa.Integer(), server_default="0"),
        sa.Column("input_data", postgresql.JSONB, nullable=True),
        sa.Column("decision", postgresql.JSONB, nullable=True),
        sa.Column("actions", postgresql.JSONB, nullable=True),
        sa.Column("approved_by", sa.String(100), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("screenshot_urls", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )

    # === approval_tasks ===
    op.create_table(
        "approval_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("agent_task_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agent_tasks.id"), nullable=False),
        sa.Column("shop_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shops.id"), nullable=False),
        sa.Column("priority", sa.Integer(), server_default="5"),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("options", postgresql.JSONB, nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("approved_by", sa.String(100), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # === tenants ===
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(200), unique=True, nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("plan", sa.String(20), server_default="starter"),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("trial_ends_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # === tenant_configs ===
    op.create_table(
        "tenant_configs",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), primary_key=True),
        sa.Column("max_shops", sa.Integer(), nullable=False),
        sa.Column("max_monthly_images", sa.Integer(), nullable=True),
        sa.Column("max_monthly_videos", sa.Integer(), nullable=True),
        sa.Column("features_enabled", postgresql.JSONB, server_default="{}"),
        sa.Column("celery_queue", sa.String(50), nullable=True),
        sa.Column("api_rate_limit", sa.Integer(), server_default="100"),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # === subscriptions ===
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("plan", sa.String(20), nullable=False),
        sa.Column("price_monthly", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_paid", sa.Numeric(10, 2), nullable=False),
        sa.Column("billing_cycle", sa.String(10), nullable=True),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("payment_method", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # === usage_records ===
    op.create_table(
        "usage_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1"),
        sa.Column("recorded_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("usage_records")
    op.drop_table("subscriptions")
    op.drop_table("tenant_configs")
    op.drop_table("tenants")
    op.drop_table("approval_tasks")
    op.drop_table("agent_tasks")
    op.drop_table("orders")
    op.drop_table("competitor_prices")
    op.drop_table("products")
    op.drop_table("shops")
