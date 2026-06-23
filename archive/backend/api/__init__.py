"""API路由包"""
from .shops import router as shops_router
from .tasks import router as tasks_router
from .approvals import router as approvals_router
from .commands import router as commands_router
from .payments import router as payments_router
from .admin import router as admin_router

__all__ = [
    "shops_router",
    "tasks_router",
    "approvals_router",
    "commands_router",
    "payments_router",
    "admin_router",
]
