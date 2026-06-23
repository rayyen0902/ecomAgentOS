"""WebSocket实时推送API"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Any

router = APIRouter()

# 全局WebSocket连接管理
active_connections: list[WebSocket] = []


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    手机端实时连接端点

    推送类型：
    - approval_request: 审批请求
    - alert: 异常告警
    - task_complete: 任务完成通知
    - agent_log: Agent运行日志
    """
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # 处理客户端消息（心跳、指令确认等）
            await websocket.send_json({"type": "pong", "data": data})
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)


async def push_notification(client_id: str, notification: dict):
    """
    向指定客户端推送通知

    Args:
        client_id: 客户端ID
        notification: 通知数据，格式 {"type": "...", "data": {...}}
    """
    target = None
    for conn in active_connections:
        # TODO: 通过conn.state获取绑定的client_id
        # 简化实现：广播所有连接
        target = conn

    if target:
        try:
            await target.send_json(notification)
        except Exception:
            pass


async def push_approval_request(shop_id: str, approval_data: dict):
    """推送审批请求"""
    await push_notification("all", {
        "type": "approval_request",
        "data": {
            "shop_id": shop_id,
            **approval_data,
        },
    })


async def push_alert(shop_id: str, message: str, level: str = "warning"):
    """推送异常告警"""
    await push_notification("all", {
        "type": "alert",
        "data": {
            "shop_id": shop_id,
            "message": message,
            "level": level,
        },
    })


async def push_task_complete(task_id: str, result: dict):
    """推送任务完成通知"""
    await push_notification("all", {
        "type": "task_complete",
        "data": {
            "task_id": task_id,
            **result,
        },
    })


async def push_agent_log(shop_id: str, log_message: str, level: str = "info"):
    """推送Agent运行日志"""
    await push_notification("all", {
        "type": "agent_log",
        "data": {
            "shop_id": shop_id,
            "message": log_message,
            "level": level,
        },
    })
