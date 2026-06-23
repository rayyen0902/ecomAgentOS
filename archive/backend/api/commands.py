"""自然语言指令API"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/natural")
async def natural_command():
    """自然语言指令入口"""
    pass
