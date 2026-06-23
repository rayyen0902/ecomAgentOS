"""Celery配置"""
from celery import Celery
from config.settings import settings
from tasks.scheduled import beat_schedule

celery_app = Celery(
    "ecommerce_agent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_soft_time_limit=300,
    task_time_limit=600,
    worker_prefetch_multiplier=1,
    beat_schedule=beat_schedule,
)

# 自动发现所有任务模块
celery_app.autodiscover_tasks(["tasks"])
