"""Structured logging powered by structlog.

Initialises structlog once (ideally at application startup) so that every
call to ``get_logger()`` returns a ready-to-use logger.  Supports two output
formats:

* ``json``  – production-ready structured JSON lines
* ``console`` – human-readable coloured output

Each request carries a ``request_id`` that is automatically injected into
all log records emitted during that request's lifecycle.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

import structlog


def _generate_request_id() -> str:
    """Return a new UUID v4 string suitable for request tracing."""
    return uuid.uuid4().hex[:16]


def get_request_id() -> str:
    """Return a ``request_id`` from structlog context if present, else create one."""
    ctx = structlog.contextvars.get_contextvars()
    return ctx.get("request_id", _generate_request_id())


def configure_logging(
    level: str = "INFO",
    fmt: str = "json",
) -> None:
    """Configure structlog for the entire application.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        fmt: Output format – ``"json"`` or ``"console"``.
    """
    python_level = getattr(logging, level.upper(), logging.INFO)

    if fmt == "console":
        processor_chain: list[Any] = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        processor_chain = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processor_chain,
        wrapper_class=structlog.make_filtering_bound_logger(python_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger() -> structlog.stdlib.BoundLogger:
    """Return a pre-configured structlog bound logger."""
    return structlog.get_logger()


def request_id_processor(
    logger: Any,
    method: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """Inject a ``request_id`` into every log record."""
    event_dict.setdefault("request_id", get_request_id())
    return event_dict
