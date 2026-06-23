"""多租户中间件 - 数据隔离 + 资源配额 + 用量计量"""
from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import Optional

from db.database import get_db
from models.shop import Shop


class TenantMiddleware:
    """
    租户中间件：
    - 从请求头获取tenant_id
    - 强制过滤所有业务查询（tenant_id WHERE条件）
    - 检查套餐权益（店铺数/图片额度/视频额度）
    - 记录用量
    """

    PLAN_LIMITS = {
        "starter": {"max_shops": 3, "monthly_images": 50, "monthly_videos": 5},
        "basic": {"max_shops": 10, "monthly_images": 200, "monthly_videos": 20},
        "growth": {"max_shops": 25, "monthly_images": 1000, "monthly_videos": 100},
        "pro": {"max_shops": 50, "monthly_images": 5000, "monthly_videos": 500},
        "enterprise": {"max_shops": -1, "monthly_images": -1, "monthly_videos": -1},  # -1表示无限
    }

    def __init__(self):
        self.tenant_id_header = "X-Tenant-ID"
        self.api_key_header = "X-API-Key"

    async def process_request(self, request: Request, db: AsyncSession) -> Optional[JSONResponse]:
        """
        处理租户请求

        Returns:
            如果有错误返回JSONResponse，否则返回None
        """
        tenant_id = request.headers.get(self.tenant_id_header)
        if not tenant_id:
            # 跳过不需要租户的端点
            if request.url.path in ("/health", "/docs", "/openapi.json"):
                return None
            raise HTTPException(status_code=401, detail="缺少租户ID")

        # TODO: 验证tenant_id有效性，加载租户配置
        # tenant = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        # tenant_config = await db.execute(select(TenantConfig).where(TenantConfig.tenant_id == tenant_id))

        # 将tenant_id注入request state，供后续依赖使用
        request.state.tenant_id = tenant_id

        # 检查API速率限制
        # TODO: 基于Redis实现速率限制

        return None

    async def check_quota(self, tenant_id: str, resource_type: str, quantity: int = 1) -> bool:
        """
        检查租户配额

        Args:
            tenant_id: 租户ID
            resource_type: 资源类型（images/videos/api_calls/rpa_operations）
            quantity: 使用数量

        Returns:
            是否还有配额
        """
        # TODO: 查询usage_records本月用量 + tenant_configs配额
        return True

    async def record_usage(self, tenant_id: str, resource_type: str, quantity: int = 1):
        """记录用量"""
        # TODO: 写入usage_records表
        pass

    def get_plan_limits(self, plan: str) -> dict:
        """获取套餐限制"""
        return self.PLAN_LIMITS.get(plan, self.PLAN_LIMITS["starter"])


# 全局中间件实例
tenant_middleware = TenantMiddleware()


async def get_current_tenant(request: Request) -> str:
    """依赖注入：获取当前租户ID"""
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        raise HTTPException(status_code=401, detail="缺少租户ID")
    return tenant_id


# PostgreSQL RLS策略SQL（用于在数据库层面强制执行租户隔离）
RLS_POLICIES_SQL = """
-- 启用shops表的行级安全
ALTER TABLE shops ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON shops
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

-- 对所有业务表应用RLS
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_products ON products
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_orders ON orders
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_agent_tasks ON agent_tasks
    USING (tenant_id = current_setting('app.tenant_id')::UUID);
"""
