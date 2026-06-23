"""任务管理API"""
from fastapi import APIRouter

router = APIRouter()


@router.post("")
async def create_task():
    """创建任务（手动触发）"""
    pass


@router.get("")
async def list_tasks():
    """任务列表"""
    pass


@router.get("/{task_id}")
async def get_task(task_id: str):
    """任务详情+截图"""
    pass
