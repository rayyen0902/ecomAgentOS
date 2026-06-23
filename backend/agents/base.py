"""Agent基类 - LangGraph多Agent框架"""
from abc import ABC, abstractmethod
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from config.llm import agnes_client, TEXT_MODEL


class AgentState(TypedDict):
    """Agent共享状态"""
    shop_id: str
    task_type: str
    input_data: dict
    decisions: list  # 决策记录（累加）
    actions: list  # 待执行动作（累加）
    requires_approval: bool  # 是否需要人工审批
    approval_status: str  # pending/approved/rejected
    result: dict
    errors: list  # 错误记录（累加）


class BaseAgent(ABC):
    """
    Agent抽象基类
    所有具体Agent继承此类，实现_analyze方法
    """

    def __init__(self, shop_id: str, input_data: dict | None = None):
        self.shop_id = shop_id
        self.input_data = input_data or {}
        self.graph = self._build_graph()

    @abstractmethod
    def _build_graph(self) -> StateGraph:
        """构建LangGraph状态图"""
        pass

    async def analyze(self, state: AgentState) -> AgentState:
        """LLM推理决策 - 子类必须实现"""
        pass

    async def check_approval_needed(self, state: AgentState) -> AgentState:
        """判断是否需要人工审批"""
        risk_actions = [a for a in state.get("actions", []) if a.get("risk_level") == "high"]
        state["requires_approval"] = len(risk_actions) > 0
        return state

    async def wait_for_approval(self, state: AgentState) -> AgentState:
        """推送审批通知，等待人工响应"""
        # 通过WebSocket推送到手机端
        await push_approval_request(self.shop_id, state)
        # 写入数据库等待审批（异步，不阻塞）
        await create_approval_task(state)
        return state

    async def execute_actions(self, state: AgentState) -> AgentState:
        """执行审批通过的动作"""
        results = []
        for action in state.get("actions", []):
            if action.get("risk_level") == "high" and not state.get("requires_approval"):
                # 高风险动作必须有审批
                continue
            try:
                result = await self._execute_action(action)
                results.append(result)
            except Exception as e:
                state["errors"].append({
                    "action": action,
                    "error": str(e),
                    "timestamp": None,
                })
        state["result"] = {"executed": results, "errors": state["errors"]}
        return state

    async def _execute_action(self, action: dict) -> dict:
        """执行单个动作 - 子类必须实现"""
        raise NotImplementedError

    async def run(self, state: AgentState | None = None) -> AgentState:
        """运行Agent状态图"""
        if state is None:
            state = AgentState(
                shop_id=self.shop_id,
                task_type=self.__class__.__name__.lower().replace("_agent", ""),
                input_data=self.input_data,
                decisions=[],
                actions=[],
                requires_approval=False,
                approval_status="pending",
                result={},
                errors=[],
            )
        # TODO: 使用LangGraph执行状态图
        return state


async def push_approval_request(shop_id: str, state: AgentState):
    """推送审批请求到WebSocket"""
    # TODO: 实现WebSocket推送
    pass


async def create_approval_task(state: AgentState):
    """创建审批任务到数据库"""
    # TODO: 实现数据库写入
    pass
