"""Tests for database models and migrations."""

import subprocess

from app.models import (
    SKU,
    AgentRun,
    AgentStep,
    AIUsageLog,
    ApprovalPolicy,
    ApprovalRequest,
    Order,
    PlatformAdapter,
    PriceHistory,
    Product,
    ProductSnapshot,
    RefundOrder,
    Shop,
    Tenant,
    User,
)


class TestModels:
    """Test all database models."""

    def test_tenant_model_import(self) -> None:
        """Test Tenant model can be imported and has correct attributes."""
        assert hasattr(Tenant, "id")
        assert hasattr(Tenant, "name")
        assert hasattr(Tenant, "slug")
        assert hasattr(Tenant, "is_active")
        assert hasattr(Tenant, "settings")
        assert hasattr(Tenant, "metadata_")

    def test_user_model_import(self) -> None:
        """Test User model can be imported and has correct attributes."""
        assert hasattr(User, "id")
        assert hasattr(User, "tenant_id")
        assert hasattr(User, "email")
        assert hasattr(User, "username")
        assert hasattr(User, "hashed_password")
        assert hasattr(User, "full_name")
        assert hasattr(User, "is_active")
        assert hasattr(User, "is_superuser")

    def test_shop_model_import(self) -> None:
        """Test Shop model can be imported and has correct attributes."""
        assert hasattr(Shop, "id")
        assert hasattr(Shop, "tenant_id")
        assert hasattr(Shop, "owner_id")
        assert hasattr(Shop, "name")
        assert hasattr(Shop, "slug")
        assert hasattr(Shop, "platform")
        assert hasattr(Shop, "is_active")

    def test_product_model_import(self) -> None:
        """Test Product model can be imported and has correct attributes."""
        assert hasattr(Product, "id")
        assert hasattr(Product, "tenant_id")
        assert hasattr(Product, "shop_id")
        assert hasattr(Product, "title")
        assert hasattr(Product, "description")
        assert hasattr(Product, "is_active")
        assert hasattr(Product, "is_published")

    def test_sku_model_import(self) -> None:
        """Test SKU model can be imported and has correct attributes."""
        assert hasattr(SKU, "id")
        assert hasattr(SKU, "tenant_id")
        assert hasattr(SKU, "product_id")
        assert hasattr(SKU, "sku_code")
        assert hasattr(SKU, "name")
        assert hasattr(SKU, "price")
        assert hasattr(SKU, "is_active")

    def test_order_model_import(self) -> None:
        """Test Order model can be imported and has correct attributes."""
        assert hasattr(Order, "id")
        assert hasattr(Order, "tenant_id")
        assert hasattr(Order, "shop_id")
        assert hasattr(Order, "order_number")
        assert hasattr(Order, "status")
        assert hasattr(Order, "total_amount")
        assert hasattr(Order, "currency")

    def test_refund_order_model_import(self) -> None:
        """Test RefundOrder model can be imported and has correct attributes."""
        assert hasattr(RefundOrder, "id")
        assert hasattr(RefundOrder, "tenant_id")
        assert hasattr(RefundOrder, "order_id")
        assert hasattr(RefundOrder, "refund_number")
        assert hasattr(RefundOrder, "status")
        assert hasattr(RefundOrder, "refund_amount")

    def test_approval_policy_model_import(self) -> None:
        """Test ApprovalPolicy model can be imported and has correct attributes."""
        assert hasattr(ApprovalPolicy, "id")
        assert hasattr(ApprovalPolicy, "tenant_id")
        assert hasattr(ApprovalPolicy, "name")
        assert hasattr(ApprovalPolicy, "is_active")
        assert hasattr(ApprovalPolicy, "trigger_conditions")
        assert hasattr(ApprovalPolicy, "approval_steps")

    def test_approval_request_model_import(self) -> None:
        """Test ApprovalRequest model can be imported and has correct attributes."""
        assert hasattr(ApprovalRequest, "id")
        assert hasattr(ApprovalRequest, "tenant_id")
        assert hasattr(ApprovalRequest, "policy_id")
        assert hasattr(ApprovalRequest, "request_number")
        assert hasattr(ApprovalRequest, "status")
        assert hasattr(ApprovalRequest, "requested_by")

    def test_agent_run_model_import(self) -> None:
        """Test AgentRun model can be imported and has correct attributes."""
        assert hasattr(AgentRun, "id")
        assert hasattr(AgentRun, "tenant_id")
        assert hasattr(AgentRun, "agent_type")
        assert hasattr(AgentRun, "status")
        assert hasattr(AgentRun, "trigger_source")
        assert hasattr(AgentRun, "input_data")
        assert hasattr(AgentRun, "output_data")

    def test_agent_step_model_import(self) -> None:
        """Test AgentStep model can be imported and has correct attributes."""
        assert hasattr(AgentStep, "id")
        assert hasattr(AgentStep, "tenant_id")
        assert hasattr(AgentStep, "agent_run_id")
        assert hasattr(AgentStep, "step_number")
        assert hasattr(AgentStep, "step_type")
        assert hasattr(AgentStep, "status")
        assert hasattr(AgentStep, "input_data")
        assert hasattr(AgentStep, "output_data")

    def test_ai_usage_log_model_import(self) -> None:
        """Test AIUsageLog model can be imported and has correct attributes."""
        assert hasattr(AIUsageLog, "id")
        assert hasattr(AIUsageLog, "tenant_id")
        assert hasattr(AIUsageLog, "user_id")
        assert hasattr(AIUsageLog, "provider")
        assert hasattr(AIUsageLog, "model")
        assert hasattr(AIUsageLog, "prompt_tokens")
        assert hasattr(AIUsageLog, "completion_tokens")
        assert hasattr(AIUsageLog, "total_tokens")
        assert hasattr(AIUsageLog, "latency_ms")

    def test_product_snapshot_model_import(self) -> None:
        """Test ProductSnapshot model can be imported and has correct attributes."""
        assert hasattr(ProductSnapshot, "id")
        assert hasattr(ProductSnapshot, "tenant_id")
        assert hasattr(ProductSnapshot, "product_id")
        assert hasattr(ProductSnapshot, "snapshot_data")
        assert hasattr(ProductSnapshot, "version")

    def test_price_history_model_import(self) -> None:
        """Test PriceHistory model can be imported and has correct attributes."""
        assert hasattr(PriceHistory, "id")
        assert hasattr(PriceHistory, "tenant_id")
        assert hasattr(PriceHistory, "sku_id")
        assert hasattr(PriceHistory, "price")
        assert hasattr(PriceHistory, "compare_at_price")
        assert hasattr(PriceHistory, "cost_price")

    def test_platform_adapter_model_import(self) -> None:
        """Test PlatformAdapter model can be imported and has correct attributes."""
        assert hasattr(PlatformAdapter, "id")
        assert hasattr(PlatformAdapter, "tenant_id")
        assert hasattr(PlatformAdapter, "name")
        assert hasattr(PlatformAdapter, "platform_type")
        assert hasattr(PlatformAdapter, "is_active")
        assert hasattr(PlatformAdapter, "config")
        assert hasattr(PlatformAdapter, "credentials")


class TestMigration:
    """Test database migrations."""

    def test_upgrade_head(self) -> None:
        """Test that alembic upgrade head works."""
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_downgrade_1(self) -> None:
        """Test that alembic downgrade -1 works."""
        # First ensure we're at head
        subprocess.run(["alembic", "upgrade", "head"], capture_output=True)

        # Then downgrade one step
        result = subprocess.run(
            ["alembic", "downgrade", "-1"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Restore to head
        subprocess.run(["alembic", "upgrade", "head"], capture_output=True)

    def test_migration_files_exist(self) -> None:
        """Test that migration files exist."""
        import os

        versions_dir = "/Users/caopinggege/Desktop/ecomAgentOS/backend/alembic/versions"
        assert os.path.exists(versions_dir)
        files = [f for f in os.listdir(versions_dir) if f.endswith(".py")]
        assert len(files) > 0


class TestHealthCheck:
    """Test health check endpoint with database connection."""

    def test_health_endpoint_with_database(self) -> None:
        """Test that /health endpoint includes database status."""
        from contextlib import asynccontextmanager
        from unittest.mock import AsyncMock, patch

        from fastapi.testclient import TestClient

        from app.main import app

        mock_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalar.return_value = 1
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_maker():
            yield mock_session

        with patch("app.db.dependencies.async_session_maker", mock_session_maker):
            client = TestClient(app)
            response = client.get("/api/v1/health")
            assert response.status_code == 200

            data = response.json()
            assert "status" in data
            assert "version" in data
            assert "timestamp" in data
            assert "database" in data
            assert data["database"] == "ok"
