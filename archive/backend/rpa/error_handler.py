"""RPA异常处理"""
from typing import Type


class RPAError(Exception):
    """RPA基础异常"""
    pass


class CaptchaDetectedError(RPAError):
    """验证码错误"""
    pass


class LoginExpiredError(RPAError):
    """登录过期错误"""
    pass


class ElementNotFoundError(RPAError):
    """元素未找到错误"""
    pass


class RateLimitError(RPAError):
    """频率限制错误"""
    pass


class RPAErrorHandler:
    """RPA异常处理器"""

    RETRY_CONFIG = {
        "max_retries": 3,
        "backoff_factor": 2,  # 指数退避
        "captcha_action": "pause",  # 遇到验证码暂停等人工
        "ban_action": "rotate_ip",  # 疑似封IP时切换
    }

    ERROR_HANDLERS: dict[Type[RPAError], str] = {
        CaptchaDetectedError: "captcha",
        LoginExpiredError: "relogin",
        ElementNotFoundError: "selector_update",
        RateLimitError: "retry_backoff",
    }

    async def handle_error(self, error: RPAError, context: dict) -> str:
        """
        处理RPA异常

        Args:
            error: 异常对象
            context: 上下文信息（shop_id, task_type等）

        Returns:
            处理动作描述
        """
        error_type = type(error)

        if isinstance(error, CaptchaDetectedError):
            # 推送告警到手机端，暂停该店铺操作
            return f"captcha_detected: shop={context.get('shop_id')}, action=_pause_"

        elif isinstance(error, LoginExpiredError):
            # Cookie过期，提示重新登录
            return f"login_expired: shop={context.get('shop_id')}, action=_relogin_required_"

        elif isinstance(error, ElementNotFoundError):
            # 页面结构变更，记录日志并通知开发
            return f"element_not_found: shop={context.get('shop_id')}, action=_notify_dev_"

        elif isinstance(error, RateLimitError):
            # 频率限制，指数退避重试
            return f"rate_limited: shop={context.get('shop_id')}, action=_retry_backoff_"

        else:
            # 未知异常
            return f"unknown_error: {str(error)}"
