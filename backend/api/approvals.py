"""审批队列API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

from db.database import get_db
from models.approval import ApprovalTask
from models.task import AgentTask
from models.shop import Shop

router = APIRouter()


class ApprovalDecide(BaseModel):
    action: str = Field(..., pattern="^(approve|reject|modify)$")
    comment: Optional[str] = None
    modified_params: Optional[dict] = None


class ApprovalResponse(BaseModel):
    id: uuid.UUID
    agent_task_id: uuid.UUID
    shop_id: uuid.UUID
    priority: int
    title: str
    description: Optional[str] = None
    options: Optional[dict] = None
    status: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/pending", response_model=list[ApprovalResponse])
async def list_pending(
    shop_id: Optional[uuid.UUID] = Query(None),
    priority: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """获取待审批列表"""
    query = select(ApprovalTask).where(ApprovalTask.status == "pending")
    if shop_id:
        query = query.where(ApprovalTask.shop_id == shop_id)
    if priority:
        query = query.where(ApprovalTask.priority <= priority)
    query = query.order_by(ApprovalTask.priority.asc(), ApprovalTask.created_at.desc())

    result = await db.execute(query)
    approvals = result.scalars().all()
    return approvals


@router.post("/{approval_id}/decide")
async def decide(
    approval_id: uuid.UUID,
    data: ApprovalDecide,
    db: AsyncSession = Depends(get_db),
):
    """审批决策（approve/reject/modify）"""
    # 获取审批任务
    result = await db.execute(select(ApprovalTask).where(ApprovalTask.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="审批任务不存在")
    if approval.status != "pending":
        raise HTTPException(status_code=400, detail="该审批已处理")

    # 更新审批状态
    approval.status = data.action
    if data.comment:
        approval.options = approval.options or {}
        approval.options["comment"] = data.comment
    if data.modified_params:
        approval.options = approval.options or {}
        approval.options["modified_params"] = data.modified_params

    # 更新关联的Agent任务状态
    if approval.agent_task_id:
        task_result = await db.execute(
            select(AgentTask).where(AgentTask.id == approval.agent_task_id)
        )
        task = task_result.scalar_one_or_none()
        if task:
            task.approved_by = "user"
            task.approved_at = datetime.now()
            task.status = "approved" if data.action == "approve" else "rejected"

    await db.commit()

    # TODO: 如果approved，通过WebSocket通知RPA执行
    # TODO: 如果是modify，更新决策后重新推送审批

    return {"status": "processed", "action": data.action}
