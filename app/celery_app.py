from celery import Celery
from kombu import Exchange, Queue

from app.config import settings

report_exchange = Exchange(settings.REPORT_EXCHANGE, type="direct", durable=True)
report_queue = Queue(
    settings.REPORT_QUEUE,
    exchange=report_exchange,
    routing_key=settings.REPORT_ROUTING_KEY,
    durable=True,
)

celery_app = Celery(
    "report_module",
    broker=settings.RABBITMQ_URL,
    backend="rpc://",
    include=["app.tasks.report_task"],
)

celery_app.conf.update(
    task_queues=(report_queue,),
    task_default_queue=settings.REPORT_QUEUE,
    task_default_exchange=settings.REPORT_EXCHANGE,
    task_default_routing_key=settings.REPORT_ROUTING_KEY,
    task_routes={
        "tasks.generate_report": {
            "queue": settings.REPORT_QUEUE,
            "exchange": settings.REPORT_EXCHANGE,
            "routing_key": settings.REPORT_ROUTING_KEY,
        }
    },
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Ho_Chi_Minh",
    task_track_started=True,
    task_create_missing_queues=False,
)
