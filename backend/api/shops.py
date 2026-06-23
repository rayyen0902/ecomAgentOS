"""店铺管理API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from db.database import get_db
from models.shop import Shop

router = APIRouter()


class ShopCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., pattern="^(douyin|taobao|pdd|xiaohongshu)$")
    config: Optional[dict] = None


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    config: Optional[dict] = None


class ShopResponse(BaseModel):
    id: uuid.UUID
    name: str
    platform: str
    platform_shop_id: Optional[str] = None
    status: str
    config: Optional[dict] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("", response_model=ShopResponse)
async def create_shop(shop_in: ShopCreate, db: AsyncSession = Depends(get_db)):
    """添加店铺"""
    shop = Shop(
        name=shop_in.name,
        platform=shop_in.platform,
        config=shop_in.config,
    )
    db.add(shop)
    await db.flush()
    await db.refresh(shop)
    return shop


@router.get("", response_model=list[ShopResponse])
async def list_shops(
    tenant_id: Optional[uuid.UUID] = Query(None, description="租户ID过滤"),
    db: AsyncSession = Depends(get_db),
):
    """获取店铺列表"""
    stmt = select(Shop).order_by(Shop.created_at.desc())
    if tenant_id:
        stmt = stmt.where(Shop.tenant_id == tenant_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{shop_id}", response_model=ShopResponse)
async def get_shop_status(shop_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """获取店铺实时状态"""
    stmt = select(Shop).where(Shop.id == shop_id)
    result = await db.execute(stmt)
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    return shop


@router.delete("/{shop_id}")
async def delete_shop(shop_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """移除店铺"""
    stmt = select(Shop).where(Shop.id == shop_id)
    result = await db.execute(stmt)
    shop = result.scalar_one_or_none()
    if not shop:
        raise HTTPException(status_code=404, detail="店铺不存在")
    await db.delete(shop)
    await db.flush()
    return {"message": "店铺已删除"}
