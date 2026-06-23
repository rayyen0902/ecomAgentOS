"""管理后台API - 租户管理 + 运营数据 + 系统监控"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import uuid

from db.database import get_db

router = APIRouter()


class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    plan: str
    status: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/tenants")
async def list_tenants(db: AsyncSession = Depends(get_db)):
    """租户列表"""
    # TODO: 查询tenants表
    return []


@router.get("/tenants/{tenant_id}")
async def get_tenant(tenant_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """租户详情"""
    # TODO: 查询tenant + config + subscriptions + usage
    return {}


@router.patch("/tenants/{tenant_id}/status")
async def update_tenant_status(
    tenant_id: uuid.UUID,
    status: str,
    db: AsyncSession = Depends(get_db),
):
    """更新租户状态（激活/暂停/取消）"""
    # TODO: 更新tenants.status
    return {"status": "updated"}


@router.get("/dashboard")
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """运营数据总览"""
    return {
        "total_tenants": 156,
        "active_tenants": 142,
        "monthly_revenue": 89500,
        "total_shops": 1234,
        "total_agents_running": 89,
        "system_health": {
            "fastapi": "healthy",
            "postgres": "healthy",
            "redis": "healthy",
            "celery": "healthy",
            "comfyui": "healthy",
        },
    }
