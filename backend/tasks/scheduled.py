"""定时任务配置"""
from celery.schedules import crontab
from tasks.celery_app import celery_app

# Agent定时任务调度配置
beat_schedule = {
    "selection_scan": {
        "task": "tasks.scheduled.selection_scan",
        "schedule": crontab(hour=8, minute=0),  # 每天8点选品巡检
    },
    "price_check": {
        "task": "tasks.scheduled.price_check",
        "schedule": crontab(minute="*/15"),  # 每15分钟竞品价格检查
    },
    "ads_optimization": {
        "task": "tasks.scheduled.ads_optimization",
        "schedule": crontab(minute=0, hour="*/2"),  # 每2小时广告优化
    },
    "inventory_check": {
        "task": "tasks.scheduled.inventory_check",
        "schedule": crontab(hour="9,18", minute=0),  # 每天9点和18点库存检查
    },
    "order_process": {
        "task": "tasks.scheduled.order_process",
        "schedule": crontab(minute="*/5"),  # 每5分钟处理新订单
    },
}


@celery_app.task(name="tasks.scheduled.selection_scan")
def selection_scan():
    """每天8点选品巡检"""
    pass


@celery_app.task(name="tasks.scheduled.price_check")
def price_check():
    """每15分钟竞品价格检查"""
    pass


@celery_app.task(name="tasks.scheduled.ads_optimization")
def ads_optimization():
    """每2小时广告优化"""
    pass


@celery_app.task(name="tasks.scheduled.inventory_check")
def inventory_check():
    """每天9点和18点库存检查"""
    pass


@celery_app.task(name="tasks.scheduled.order_process")
def order_process():
    """每5分钟处理新订单"""
    pass
