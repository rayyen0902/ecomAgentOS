"""Core business models for ecomAgentOS.

This module defines the 12 core database tables required by the application:
- tenants
- users
- shops
- platform_adapters
- products
- product_snapshots
- skus
- price_history
- orders
- refund_orders
- approval_policies
- approval_requests
- agent_runs
- agent_steps

Each model includes:
- UUID primary key
- tenant_id foreign key
- created_at / updated_at timestamps
- Appropriate field types (String, JSONB, etc.)
- Indexes for performance
"""

from app.models.agent_runs import AgentRun
from app.models.agent_steps import AgentStep
from app.models.ai_usage_log import AIUsageLog
from app.models.approval_policies import ApprovalPolicy
from app.models.approval_requests import ApprovalRequest
from app.models.orders import Order
from app.models.platform_adapters import PlatformAdapter
from app.models.price_history import PriceHistory
from app.models.product_snapshots import ProductSnapshot
from app.models.products import Product
from app.models.refund_orders import RefundOrder
from app.models.shops import Shop
from app.models.skus import SKU
from app.models.tenants import Tenant
from app.models.users import User

__all__ = [
    "AIUsageLog",
    "ApprovalPolicy",
    "ApprovalRequest",
    "AgentRun",
    "AgentStep",
    "Order",
    "PlatformAdapter",
    "PriceHistory",
    "Product",
    "ProductSnapshot",
    "RefundOrder",
    "SKU",
    "Shop",
    "Tenant",
    "User",
]
