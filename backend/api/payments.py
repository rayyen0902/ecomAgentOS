"""支付系统API - 微信支付 + 支付宝"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional
import uuid

from db.database import get_db

router = APIRouter()


class PaymentCreate(BaseModel):
    plan: str = Field(..., pattern="^(starter|basic|growth|pro|enterprise)$")
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")
    payment_method: str = Field(..., pattern="^(wechat|alipay)$")


class PaymentResponse(BaseModel):
    order_id: str
    payment_url: Optional[str] = None
    qr_code: Optional[str] = None
    status: str
    amount: float
    plan: str
    billing_cycle: str

    class Config:
        from_attributes = True


@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    data: PaymentCreate,
    tenant_id: uuid.UUID = Query(..., description="租户ID"),
    db: AsyncSession = Depends(get_db),
):
    """创建支付订单"""
    # 价格配置
    PRICES = {
        "starter": {"monthly": 99, "yearly": 990},
        "basic": {"monthly": 299, "yearly": 2990},
        "growth": {"monthly": 599, "yearly": 5990},
        "pro": {"monthly": 999, "yearly": 9990},
        "enterprise": {"monthly": 2999, "yearly": 29990},
    }

    price_map = PRICES.get(data.plan, PRICES["starter"])
    amount = price_map.get(data.billing_cycle, price_map["monthly"])

    # 创建支付订单
    order_id = f"pay_{uuid.uuid4().hex[:12]}"

    # 根据支付方式调用对应API
    if data.payment_method == "wechat":
        # TODO: 调用微信支付API
        payment_url = f"https://pay.weixin.qq.com/qrcode?order={order_id}"
    elif data.payment_method == "alipay":
        # TODO: 调用支付宝API
        payment_url = f"https://openapi.alipay.com/gateway?order={order_id}"
    else:
        raise HTTPException(status_code=400, detail="不支持的支付方式")

    return PaymentResponse(
        order_id=order_id,
        payment_url=payment_url,
        status="pending",
        amount=amount,
        plan=data.plan,
        billing_cycle=data.billing_cycle,
    )


@router.post("/callback")
async def payment_callback(
    payment_method: str,
    db: AsyncSession = Depends(get_db),
):
    """
    支付回调通知

    微信支付/支付宝异步通知处理
    验证签名 -> 更新订单状态 -> 激活租户套餐
    """
    # TODO: 验证支付签名
    # TODO: 更新subscription状态为active
    # TODO: 更新tenant plan
    return {"status": "success"}


@router.get("/usage")
async def get_usage(
    tenant_id: uuid.UUID = Query(...),
    resource_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """获取租户用量统计"""
    # TODO: 查询usage_records
    return {
        "tenant_id": str(tenant_id),
        "resources": {
            "images": {"used": 123, "limit": 1000},
            "videos": {"used": 5, "limit": 100},
            "api_calls": {"used": 45678, "limit": 100000},
            "rpa_operations": {"used": 890, "limit": 5000},
        },
    }
