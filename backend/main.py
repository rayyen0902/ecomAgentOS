"""FastAPI应用入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.settings import settings
from api.shops import router as shops_router
from api.tasks import router as tasks_router
from api.approvals import router as approvals_router
from api.commands import router as commands_router
from api.payments import router as payments_router
from api.admin import router as admin_router
from api.websocket import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print(f"Starting ecommerce agent system on {settings.host}:{settings.port}")
    print(f"Debug mode: {settings.debug}")
    yield
    print("Shutting down ecommerce agent system")


app = FastAPI(
    title="多Agent电商自主运营系统",
    description="多Agent驱动的电商自主运营平台",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(shops_router, prefix="/api/shops", tags=["店铺管理"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["Agent任务"])
app.include_router(approvals_router, prefix="/api/approvals", tags=["审批队列"])
app.include_router(commands_router, prefix="/api/commands", tags=["自然语言指令"])
app.include_router(payments_router, prefix="/api/payments", tags=["支付订阅"])
app.include_router(admin_router, prefix="/api/admin", tags=["管理后台"])
app.include_router(websocket_router)


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "ecommerce-agent-system",
        "version": "1.0.0",
    }
